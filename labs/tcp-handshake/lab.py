"""Offline fictional practice: TCP handshake investigation."""

from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = 'tcp-handshake'


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()),
            f"{label}: missing or unsupported fields")


def items(value, label, minimum=1, maximum=100):
    require(isinstance(value, list) and minimum <= len(value) <= maximum,
            f"{label}: expected {minimum}-{maximum} records")
    return value


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value),
            "record IDs must be short lowercase names")
    return value


def domain(value, wildcard=False):
    require(isinstance(value, str), "domain must be text")
    candidate = value.lower()
    if wildcard and candidate.startswith("*."):
        candidate = candidate[2:]
    require(len(candidate) <= 253 and candidate.endswith(".test") and
            all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part)
                for part in candidate.split(".")), "use ASCII .test domains only")
    return value.lower()


def integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, f"invalid {label}")
    return value


def boolean(value, label):
    require(type(value) is bool, f"{label} must be a boolean")


def enumeration(value, choices, label):
    require(isinstance(value, str) and value in choices, f"unsupported {label}")


def unique(values, label):
    require(len(values) == len(set(values)), f"duplicate {label}")


def question(case, extra=""):
    validate_case(case, LAB_ID)
    fields(case["context"], "question " + extra, "context")
    require(isinstance(case["context"]["question"], str) and
            case["context"]["question"].strip(), "question is required")


from ipaddress import IPv4Address, IPv4Network

LIMITATIONS = ['Missing packets can reflect capture position, loss or a short capture; they do not prove a firewall or server fault.', 'Only one ordinary, payload-free opening attempt per flow is supported; this is not a packet decoder or TCP state implementation.']


def address(value):
    require(isinstance(value, str), "address must be text")
    try:
        parsed = IPv4Address(value)
    except ValueError as error:
        raise ValueError("invalid IPv4 address") from error
    require(any(parsed in IPv4Network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")),
            "use documentation addresses")


def packet_csv(flows):
    lines = ["flow,frame,direction,flags,sequence,acknowledgement"]
    for flow in flows:
        for p in flow["packets"]:
            ack = "" if p["ack"] is None else str(p["ack"])
            lines.append(f'{flow["id"]},{p["frame"]},{p["direction"]},{p["flags"]},{p["seq"]},{ack}')
    return "\n".join(lines) + "\n"


def synack_suffix(packets, index):
    """Validate repeated SYN-ACKs and their optional single final ACK."""
    response = packets[index]
    while index + 1 < len(packets) and packets[index + 1]["flags"] == "SYN-ACK":
        require(packets[index + 1]["seq"] == response["seq"] and
                packets[index + 1]["ack"] == response["ack"], "inconsistent SYN-ACK retransmission")
        index += 1
    remaining = packets[index + 1:]
    require(len(remaining) <= 1 and all(p["flags"] == "ACK" for p in remaining), "only a final ACK may follow SYN-ACK")
    return remaining


def classify(packets):
    first = packets[0]
    if first["flags"] != "SYN":
        require(all(p["flags"] != "SYN" for p in packets), "split distinct attempts into separate flows")
        if first["flags"] == "SYN-ACK":
            synack_suffix(packets, 0)
        else:
            require(len(packets) == 1, "a late-capture ACK or reset must end the excerpt")
        return "initial-syn-not-observed", "the excerpt begins after the initial SYN or contains no initial SYN"
    client_next = (first["seq"] + 1) % (2**32)
    index = 1
    while index < len(packets) and packets[index]["flags"] == "SYN":
        require(packets[index]["seq"] == first["seq"], "different SYN sequence numbers need separate flows")
        index += 1
    if index == len(packets):
        return "no-response-observed", f"{index} SYN observation(s); no server response in this excerpt"
    response = packets[index]
    require(response["flags"] in {"SYN-ACK", "RST-ACK"}, "unsupported opening packet order")
    require(all(p["flags"] != "SYN" for p in packets[index:]), "late SYN outside this small model")
    if response["flags"] == "RST-ACK":
        require(index + 1 == len(packets), "split packets after reset into another flow")
        if response["ack"] != client_next:
            return "acknowledgement-mismatch", f"reset ACK={response['ack']}; expected {client_next}"
        return "reset-observed", f"server-direction RST-ACK acknowledges {client_next}; cause is not established"
    server_next = (response["seq"] + 1) % (2**32)
    remaining = synack_suffix(packets, index)
    if response["ack"] != client_next:
        return "acknowledgement-mismatch", f"SYN-ACK ACK={response['ack']}; expected {client_next}"
    if not remaining:
        return "final-ack-not-observed", f"SYN-ACK acknowledges {client_next}; final client ACK is absent"
    final = remaining[0]
    if final["seq"] != client_next or final["ack"] != server_next:
        return "acknowledgement-mismatch", f"final SEQ/ACK={final['seq']}/{final['ack']}; expected {client_next}/{server_next}"
    return "handshake-observed", f"SYN {first['seq']} -> SYN-ACK {response['seq']}/{client_next} -> ACK {client_next}/{server_next}"


def analyse(case):
    question(case)
    fields(case["data"], "flows", "data")
    flows = items(case["data"]["flows"], "flows")
    decisions, observations = {}, []
    for flow in flows:
        fields(flow, "id client server server_port capture_note packets", "flow")
        key = identifier(flow["id"])
        require(key not in decisions, "duplicate flow ID")
        address(flow["client"])
        address(flow["server"])
        require(flow["client"] != flow["server"], "endpoints must differ")
        integer(flow["server_port"], 1, 65535, "server port")
        require(isinstance(flow["capture_note"], str) and flow["capture_note"].strip(), "capture note required")
        packets = items(flow["packets"], "packets", 1, 30)
        last = 0
        for p in packets:
            fields(p, "frame direction flags seq ack", "packet")
            integer(p["frame"], 1, 1000000, "frame")
            require(p["frame"] > last, "frames must increase within a flow")
            last = p["frame"]
            enumeration(p["flags"], {"SYN", "SYN-ACK", "ACK", "RST-ACK"}, "flag combination")
            expected_direction = "c2s" if p["flags"] in {"SYN", "ACK"} else "s2c"
            require(p["direction"] == expected_direction, "direction outside ordinary client-initiated model")
            integer(p["seq"], 0, 2**32 - 1, "sequence number")
            if p["flags"] == "SYN":
                require(p["ack"] is None, "SYN without ACK uses null acknowledgement")
            else:
                integer(p["ack"], 0, 2**32 - 1, "acknowledgement")
        decision, detail = classify(packets)
        decisions[key] = decision
        observations.append(f"{key}: {detail}.")
    require(case["artifacts"] == {"packets.csv": packet_csv(flows)}, "CSV must mirror authoritative JSON packets")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITATIONS.copy()}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
