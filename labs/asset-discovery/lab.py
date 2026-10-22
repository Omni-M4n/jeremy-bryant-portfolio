"""Offline fictional practice: Asset discovery and inventory."""

from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = 'asset-discovery'


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
import xml.etree.ElementTree as ET

LIMITATIONS = ['A saved scan is a time-limited observation, not proof of ownership, vulnerability or complete coverage.', 'Only this documented XML subset and TCP states open, closed and filtered are supported; no scanning occurs.']
NETWORKS = tuple(IPv4Network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))


def address(value):
    require(isinstance(value, str), "address must be text")
    try:
        parsed = IPv4Address(value)
    except ValueError as error:
        raise ValueError("invalid IPv4 address") from error
    require(any(parsed in network for network in NETWORKS), "use documentation IPv4 addresses")
    return value


def xml_shape(node, tag, attrs, children):
    require(node.tag == tag and set(node.attrib) == set(attrs.split()), f"unsupported {tag} XML attributes")
    require(not (node.text or "").strip() and not (node.tail or "").strip(), "XML mixed content unsupported")
    require(all(child.tag in children for child in node), f"unsupported {tag} XML children")


def parse_scan(raw):
    require(isinstance(raw, str) and 0 < len(raw) <= 50000, "bounded XML text is required")
    require("<!" not in raw and "<?" not in raw, "XML declarations, DTDs and entities are unsupported")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        raise ValueError("malformed scan XML") from error
    xml_shape(root, "nmaprun", "scanner", {"host"})
    require(root.attrib["scanner"] == "nmap", "expected saved Nmap-shaped evidence")
    require(len(root) <= 100, "too many hosts")
    found = {}
    for host in root:
        xml_shape(host, "host", "", {"status", "address", "ports"})
        require([c.tag for c in host] in (["status", "address"], ["status", "address", "ports"]),
                "host requires one status, one address and optional ports")
        status, addr = host[0], host[1]
        xml_shape(status, "status", "state", set())
        enumeration(status.attrib["state"], {"up", "down"}, "host state")
        xml_shape(addr, "address", "addr addrtype", set())
        require(addr.attrib["addrtype"] == "ipv4", "only IPv4 is supported")
        ip = address(addr.attrib["addr"])
        require(ip not in found, "duplicate scan host")
        states = {}
        if len(host) == 3:
            ports = host[2]
            xml_shape(ports, "ports", "", {"port"})
            require(len(ports) <= 100, "too many ports")
            for port in ports:
                xml_shape(port, "port", "protocol portid", {"state"})
                require(port.attrib["protocol"] == "tcp" and
                        re.fullmatch(r"[1-9][0-9]{0,4}", port.attrib["portid"]), "invalid TCP port")
                number = integer(int(port.attrib["portid"]), 1, 65535, "port")
                require(number not in states and len(port) == 1, "duplicate port or missing state")
                xml_shape(port[0], "state", "state", set())
                state = port[0].attrib["state"]
                enumeration(state, {"open", "closed", "filtered"}, "port state")
                states[number] = state
        require(status.attrib["state"] == "up" or not states, "down host cannot have port observations")
        found[ip] = (status.attrib["state"], states)
    return found


def analyse(case):
    question(case)
    data = case["data"]
    fields(data, "scope approved nmap_xml", "data")
    scope = [address(ip) for ip in items(data["scope"], "scope")]
    unique(scope, "scope address")
    approved = {}
    for row in items(data["approved"], "approved inventory"):
        fields(row, "ip owner expected_tcp_ports", "inventory record")
        ip = address(row["ip"])
        require(ip in scope and ip not in approved, "duplicate or out-of-scope inventory host")
        identifier(row["owner"])
        ports = [integer(p, 1, 65535, "expected port") for p in items(row["expected_tcp_ports"], "expected ports", 0)]
        unique(ports, "expected port")
        approved[ip] = set(ports)
    found = parse_scan(data["nmap_xml"])
    require(set(found) <= set(scope), "scan includes an out-of-scope host")
    require(case["artifacts"] == {"scan.xml": data["nmap_xml"]}, "scan.xml must exactly mirror authoritative data.nmap_xml")
    decisions, observations = {}, []
    for ip in sorted(set(approved) | set(found), key=IPv4Address):
        if ip not in found:
            decision, detail = "not-observed-in-scan", "approved host has no host record"
        else:
            status, states = found[ip]
            opened = {p for p, state in states.items() if state == "open"}
            if status != "up":
                decision, detail = "not-observed-up", "saved host state is down; absence is not proof of removal"
            elif ip not in approved:
                decision, detail = "unregistered-host-observed", f"up with open TCP ports {sorted(opened)}; no approved record"
            else:
                extra = opened - approved[ip]
                missing = approved[ip] - opened
                decision = ("unapproved-service-observed" if extra else
                            "expected-service-not-observed" if missing else "expected-services-observed")
                detail = f"open={sorted(opened)}; unexpected={sorted(extra)}; expected-not-observed-open={sorted(missing)}"
        decisions[ip] = decision
        observations.append(f"{ip}: {detail}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITATIONS.copy()}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
