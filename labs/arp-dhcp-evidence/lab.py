"""Correlate bounded synthetic DHCP and ordinary ARP packet excerpts."""
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "arp-dhcp-evidence"
ZERO = "0.0.0.0"
BROADCAST = "255.255.255.255"
EMPTY_MAC = "00:00:00:00:00:00"
BLOCKS = tuple(IPv4Network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
LIMITATIONS = [
    "Frames are synthetic summaries from one observation point, not a PCAP or proof of client acceptance, connectivity or server trust.",
    "Missing messages may reflect the capture window or visibility. A renewal need not repeat Discover and Offer; no failure cause is inferred.",
    "Only one allocation or unicast renewal attempt per client/xid and ordinary ARP request/reply excerpts are supported; relays, rebinding, INIT-REBOOT, probes and announcements are excluded."
]


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()), f"{label}: missing or unsupported fields")


def records(value, label, maximum=30):
    require(isinstance(value, list) and 1 <= len(value) <= maximum, f"{label}: expected 1-{maximum} records")
    return value


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}", value), "invalid ID")
    return value


def address(value, special=()):
    require(isinstance(value, str), "address must be text")
    parsed = IPv4Address(value)
    require(value in special or any(parsed in block for block in BLOCKS), "use documentation IPv4 addresses")
    return value


def mac(value, allow_empty=False):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{2}(?::[0-9a-f]{2}){5}", value), "invalid lowercase MAC")
    require((allow_empty and value == EMPTY_MAC) or (value.startswith("02:") and value != EMPTY_MAC), "use synthetic locally administered unicast MACs beginning 02:")
    return value


def integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, f"invalid {label}")


def packet_order(packets, used_frames):
    last = 0
    for packet in records(packets, "packets"):
        require(isinstance(packet, dict) and "frame" in packet, "packet needs frame")
        frame = packet["frame"]
        integer(frame, 1, 1000000, "frame")
        require(frame > last and frame not in used_frames, "frames must increase in each excerpt and be unique across the case")
        used_frames.add(frame)
        last = frame


def validate_dhcp(packet):
    fields(packet, "frame message xid client_mac ciaddr yiaddr requested_ip server_id ip_destination lease_seconds", "DHCP packet")
    require(packet["message"] in ("DISCOVER", "OFFER", "REQUEST", "ACK", "NAK"), "unsupported DHCP message")
    integer(packet["xid"], 0, 2**32 - 1, "transaction ID")
    mac(packet["client_mac"])
    address(packet["ciaddr"], (ZERO,))
    address(packet["yiaddr"], (ZERO,))
    address(packet["ip_destination"], (BROADCAST,))
    for field in ("requested_ip", "server_id"):
        if packet[field] is not None:
            address(packet[field])
    if packet["lease_seconds"] is not None:
        integer(packet["lease_seconds"], 1, 2**32 - 1, "lease duration")
    message = packet["message"]
    if message == "DISCOVER":
        require(packet["ciaddr"] == packet["yiaddr"] == ZERO and packet["server_id"] is None and packet["requested_ip"] is None and packet["lease_seconds"] is None and packet["ip_destination"] == BROADCAST, "unsupported Discover form")
    elif message == "REQUEST":
        require(packet["yiaddr"] == ZERO and packet["lease_seconds"] is None, "Request has no yiaddr or lease in this model")
        if packet["ciaddr"] == ZERO:
            require(packet["requested_ip"] is not None and packet["server_id"] is not None and packet["ip_destination"] == BROADCAST, "only selecting-state allocation Request supported")
        else:
            require(packet["requested_ip"] is None and packet["server_id"] is None and packet["ip_destination"] != BROADCAST, "only unicast renewal Request supported")
    else:
        require(packet["server_id"] is not None and packet["requested_ip"] is None, "reply needs server identifier and no requested-IP option")
        if message == "NAK":
            require(packet["ciaddr"] == ZERO, "NAK ciaddr must be zero")
            require(packet["yiaddr"] == ZERO and packet["lease_seconds"] is None, "NAK must not assign a lease")
            require(packet["ip_destination"] == BROADCAST, "NAK must be broadcast in this no-relay model")
        else:
            require(packet["yiaddr"] != ZERO and packet["lease_seconds"] is not None, "Offer/ACK needs address and positive lease")
            if message == "OFFER":
                require(packet["ciaddr"] == ZERO, "Offer ciaddr must be zero")
                require(packet["ip_destination"] in (BROADCAST, packet["yiaddr"]), "Offer destination must be broadcast or its offered address in this model")


def validate_ack_delivery(request, reply):
    """Check fields whose meaning depends on the observed Request."""
    # RFC 2131 Table 3 permits the copied Request ciaddr or zero in an ACK.
    require(reply["ciaddr"] in (ZERO, request["ciaddr"]), "ACK ciaddr contradicts its Request")
    if request["ciaddr"] != ZERO:
        require(reply["ip_destination"] == request["ciaddr"], "renewal ACK must be unicast to the Request ciaddr in this no-relay model")
    else:
        # The capture summary omits the broadcast flag, so both are supported.
        require(reply["ip_destination"] in (BROADCAST, reply["yiaddr"]), "allocation ACK destination must be broadcast or its assigned address")


def dhcp_result(session):
    matching = [p for p in session["packets"] if (p["client_mac"], p["xid"]) == (session["client_mac"], session["xid"])]
    ignored = [p["frame"] for p in session["packets"] if p not in matching]
    messages = [p["message"] for p in matching]
    require(len(messages) == len(set(messages)), "split retransmissions or multiple offers into separate evidence before using this model")
    require(not ("ACK" in messages and "NAK" in messages), "conflicting terminal replies outside model")
    rank = {"DISCOVER": 0, "OFFER": 1, "REQUEST": 2, "ACK": 3, "NAK": 3}
    require([rank[m] for m in messages] == sorted(rank[m] for m in messages), "unsupported DHCP order")
    lookup = {p["message"]: p for p in matching}
    prefix = f"{session['id']}: client {session['client_mac']}, xid {session['xid']}; matching frames {[p['frame'] for p in matching]}; ignored frames {ignored}"
    request = lookup.get("REQUEST")
    if request is None:
        return "request-not-observed", prefix + "; no matching Request, so no request/reply lease conclusion.", None
    renewal = request["ciaddr"] != ZERO
    require(not renewal or not ({"DISCOVER", "OFFER"} & set(messages)), "renewal cannot include allocation steps in this attempt")
    wanted_ip = request["ciaddr"] if renewal else request["requested_ip"]
    wanted_server = request["ip_destination"] if renewal else request["server_id"]
    reply = lookup.get("ACK") or lookup.get("NAK")
    if reply is None:
        return "ack-not-observed", prefix + f"; {'renewal' if renewal else 'allocation'} Request for {wanted_ip}; no matching ACK/NAK in this excerpt.", None
    if reply["message"] == "ACK":
        validate_ack_delivery(request, reply)
    if reply["server_id"] != wanted_server or (reply["message"] == "ACK" and reply["yiaddr"] != wanted_ip):
        return "reply-mismatch", prefix + f"; expected server/address {wanted_server}/{wanted_ip}; reply has {reply['server_id']}/{reply['yiaddr']}.", None
    if reply["message"] == "NAK":
        return "nak-observed", prefix + f"; server {wanted_server} returned NAK, not a lease acknowledgement.", None
    if renewal:
        label = "renewal-ack-observed"
    else:
        offer = lookup.get("OFFER")
        complete = "DISCOVER" in lookup and offer is not None and offer["server_id"] == wanted_server and offer["yiaddr"] == wanted_ip
        label = "allocation-ack-observed" if complete else "allocation-ack-with-gaps"
    detail = prefix + f"; {label}: ACK frame {reply['frame']} matches server {wanted_server} and address {wanted_ip}, lease {reply['lease_seconds']} seconds; reply destination {reply['ip_destination']}, ciaddr {reply['ciaddr']}."
    return label, detail, reply


def validate_arp(packet):
    fields(packet, "frame opcode sender_ip sender_mac target_ip target_mac", "ARP packet")
    require(packet["opcode"] in ("request", "reply"), "unsupported ARP opcode")
    address(packet["sender_ip"])
    address(packet["target_ip"])
    require(packet["sender_ip"] != packet["target_ip"], "announcements/probes outside ordinary ARP model")
    mac(packet["sender_mac"])
    mac(packet["target_mac"], allow_empty=packet["opcode"] == "request")
    if packet["opcode"] == "request":
        require(packet["target_mac"] == EMPTY_MAC, "this fixture format uses zero target MAC for an ordinary request")


def arp_result(exchange):
    requests = [p for p in exchange["packets"] if p["opcode"] == "request" and (p["sender_ip"], p["sender_mac"], p["target_ip"]) == (exchange["requester_ip"], exchange["requester_mac"], exchange["target_ip"])]
    replies = [p for p in exchange["packets"] if p["opcode"] == "reply" and (p["sender_ip"], p["target_ip"], p["target_mac"]) == (exchange["target_ip"], exchange["requester_ip"], exchange["requester_mac"])]
    matching = requests + replies
    ignored = [p["frame"] for p in exchange["packets"] if p not in matching]
    mappings = sorted({p["sender_mac"] for p in replies})
    paired_replies = [p for p in replies if any(request["frame"] < p["frame"] for request in requests)]
    unpaired_frames = [p["frame"] for p in replies if p not in paired_replies]
    if len(mappings) > 1:
        label = "mapping-disagreement"
    elif paired_replies:
        label = "exchange-observed"
    elif replies:
        label = "reply-without-prior-request"
    elif requests:
        label = "request-no-reply-observed"
    else:
        label = "no-matching-frames"
    detail = f"{exchange['id']}: target {exchange['target_ip']}; request frames {[p['frame'] for p in requests]}; reply frames {[p['frame'] for p in replies]}; mappings {mappings}; ignored frames {ignored}."
    if unpaired_frames:
        detail += f" Reply frames {unpaired_frames} have no earlier observed matching request."
    return label, detail, requests


def evidence_text(data):
    lines = ["SYNTHETIC PACKET EXCERPTS; not a PCAP or a real capture", data["capture_note"]]
    for session in data["dhcp_sessions"]:
        lines.append(f"DHCP query {session['id']}: client={session['client_mac']} xid={session['xid']}")
        for p in session["packets"]:
            lines.append(f"frame {p['frame']}: {p['message']} xid={p['xid']} client={p['client_mac']} ciaddr={p['ciaddr']} yiaddr={p['yiaddr']} requested={p['requested_ip']} server={p['server_id']} destination={p['ip_destination']} lease={p['lease_seconds']}")
    for exchange in data["arp_exchanges"]:
        lines.append(f"ARP query {exchange['id']}: requester={exchange['requester_ip']}/{exchange['requester_mac']} target={exchange['target_ip']} related-DHCP={exchange['related_dhcp']}")
        for p in exchange["packets"]:
            lines.append(f"frame {p['frame']}: {p['opcode']} sender={p['sender_ip']}/{p['sender_mac']} target={p['target_ip']}/{p['target_mac']}")
    return "\n".join(lines) + "\n"


def analyse(case):
    validate_case(case, LAB_ID)
    fields(case["context"], "question", "context")
    require(isinstance(case["context"]["question"], str) and case["context"]["question"].strip(), "question required")
    data = case["data"]
    fields(data, "capture_note dhcp_sessions arp_exchanges", "data")
    require(isinstance(data["capture_note"], str) and data["capture_note"].strip(), "capture note required")
    decisions, observations, sessions, acknowledgements, frames = {}, [], {}, {}, set()
    for session in records(data["dhcp_sessions"], "DHCP sessions", 10):
        fields(session, "id client_mac xid packets", "DHCP session")
        key = identifier(session["id"])
        require(key not in decisions, "duplicate decision ID")
        mac(session["client_mac"])
        integer(session["xid"], 0, 2**32 - 1, "transaction ID")
        packet_order(session["packets"], frames)
        for packet in session["packets"]:
            validate_dhcp(packet)
        label, detail, ack = dhcp_result(session)
        decisions[key], sessions[key], acknowledgements[key] = label, session, ack
        observations.append(detail)
    for exchange in records(data["arp_exchanges"], "ARP exchanges", 10):
        fields(exchange, "id requester_ip requester_mac target_ip related_dhcp packets", "ARP exchange")
        key = identifier(exchange["id"])
        require(key not in decisions and key + "-lease-link" not in decisions, "duplicate decision ID")
        address(exchange["requester_ip"])
        address(exchange["target_ip"])
        require(exchange["requester_ip"] != exchange["target_ip"], "ARP endpoints must differ")
        mac(exchange["requester_mac"])
        require(isinstance(exchange["related_dhcp"], str) and exchange["related_dhcp"] in sessions, "unknown related DHCP session")
        related = sessions[exchange["related_dhcp"]]
        require(exchange["requester_mac"] == related["client_mac"], "related DHCP must identify the same client MAC")
        packet_order(exchange["packets"], frames)
        for packet in exchange["packets"]:
            validate_arp(packet)
        label, detail, requests = arp_result(exchange)
        decisions[key] = label
        observations.append(detail)
        ack = acknowledgements[exchange["related_dhcp"]]
        if ack is None or not requests:
            link = "lease-link-not-established"
            detail = "needs a matched DHCP Request/ACK and an observed ARP request"
        elif min(p["frame"] for p in requests) <= ack["frame"]:
            link = "arp-precedes-ack"
            detail = f"ARP request precedes ACK frame {ack['frame']}; this ACK cannot explain earlier use"
        elif exchange["requester_ip"] != ack["yiaddr"]:
            link = "lease-address-disagreement"
            detail = f"ARP uses {exchange['requester_ip']}, while ACK frame {ack['frame']} offers {ack['yiaddr']}"
        else:
            link = "same-client-address-observed"
            detail = f"later ARP request uses ACK frame {ack['frame']} address {ack['yiaddr']} and the same client MAC"
        decisions[key + "-lease-link"] = link
        observations.append(f"{key}-lease-link: {detail}; this is correlation, not proof of identity or client acceptance.")
    require(case["artifacts"] == {"packets.txt": evidence_text(data)}, "packet text must mirror authoritative JSON")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITATIONS.copy()}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
