"""Choose a first hop from a small synthetic IPv4 forwarding table."""
from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "network-address-path"
BLOCKS = tuple(IPv4Network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
LIMITATIONS = [
    "This is first-hop selection in one supplied table, not proof of delivery, return routing, DNS availability or firewall permission.",
    "IPv4 unicast only; no policy routing, recursive gateways, interface failure, NAT, VPN, IPv6 or equal-cost load balancing is simulated.",
    "Metrics are comparable only inside this teaching table. An equal best prefix and metric is reported as unresolved, not chosen by row order."
]


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()), f"{label}: missing or unsupported fields")


def records(value, label):
    require(isinstance(value, list) and 1 <= len(value) <= 30, f"{label}: expected 1-30 records")
    return value


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}", value), "invalid ID")
    return value


def address(value):
    require(isinstance(value, str), "IPv4 address must be text")
    parsed = IPv4Address(value)
    require(any(parsed in block for block in BLOCKS), "use documentation IPv4 addresses")
    return parsed


def hostname(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}\.test", value), "use a simple lowercase .test name")


def network(value):
    require(isinstance(value, str) and "/" in value, "route prefix must be text CIDR")
    parsed = IPv4Network(value, strict=True)
    require(str(parsed) == value, "use canonical route CIDR")
    require(parsed.prefixlen == 0 or any(parsed.subnet_of(block) for block in BLOCKS), "route outside documentation blocks")
    return parsed


def evidence_text(data):
    lines = ["SYNTHETIC READ-ONLY SNAPSHOT; not a real VM transcript", "INTERFACES: id address/prefix"]
    lines += [f"{i['id']} {i['cidr']}" for i in data["interfaces"]]
    lines.append("ROUTES: id destination via interface metric (on-link means no gateway)")
    lines += [f"{r['id']} {r['destination']} {r['via'] or 'on-link'} {r['interface']} {r['metric']}" for r in data["routes"]]
    lines.append("SUPPLIED NAME EVIDENCE: name address (unknown means no address supplied)")
    lines += [f"{name} {ip or 'unknown'}" for name, ip in data["names"].items()]
    lines.append("REQUESTS: id target")
    lines += [f"{q['id']} {q['target']}" for q in data["requests"]]
    return "\n".join(lines) + "\n"


def validate_data(case):
    validate_case(case, LAB_ID)
    fields(case["context"], "question", "context")
    require(isinstance(case["context"]["question"], str) and case["context"]["question"].strip(), "question required")
    data = case["data"]
    fields(data, "interfaces routes names requests", "data")
    interfaces = {}
    for item in records(data["interfaces"], "interfaces"):
        fields(item, "id cidr", "interface")
        key = identifier(item["id"])
        require(key not in interfaces, "duplicate interface ID")
        require(isinstance(item["cidr"], str) and "/" in item["cidr"], "interface needs CIDR")
        iface = IPv4Interface(item["cidr"])
        address(str(iface.ip))
        require(24 <= iface.network.prefixlen <= 30 and str(iface) == item["cidr"], "interface supports canonical /24 through /30")
        require(iface.ip not in (iface.network.network_address, iface.network.broadcast_address), "interface needs a usable host address")
        require(all(not iface.network.overlaps(other.network) for other in interfaces.values()), "overlapping interfaces unsupported")
        interfaces[key] = iface
    routes, seen, connected = [], set(), set()
    for row in records(data["routes"], "routes"):
        fields(row, "id destination via interface metric", "route")
        key = identifier(row["id"])
        require(key not in seen, "duplicate route ID")
        seen.add(key)
        prefix = network(row["destination"])
        require(isinstance(row["interface"], str) and row["interface"] in interfaces, "route has unknown interface")
        iface = interfaces[row["interface"]]
        require(type(row["metric"]) is int and 0 <= row["metric"] <= 9999, "invalid metric")
        if row["via"] is None:
            require(prefix == iface.network and row["interface"] not in connected, "one exact connected route per interface required")
            connected.add(row["interface"])
        else:
            gateway = address(row["via"])
            require(gateway in iface.network and gateway not in (iface.ip, iface.network.network_address, iface.network.broadcast_address), "gateway must be another usable on-link address")
        routes.append((row, prefix))
    require(connected == set(interfaces), "missing connected route")
    require(isinstance(data["names"], dict) and len(data["names"]) <= 30, "names must be a bounded object")
    for name, value in data["names"].items():
        hostname(name)
        if value is not None:
            address(value)
    seen = set()
    for row in records(data["requests"], "requests"):
        fields(row, "id target", "request")
        key = identifier(row["id"])
        require(key not in seen, "duplicate request ID")
        seen.add(key)
        require(isinstance(row["target"], str), "target must be text")
        if row["target"].endswith(".test"):
            hostname(row["target"])
            require(row["target"] in data["names"], "every name needs supplied evidence")
            value = data["names"][row["target"]]
        else:
            value = row["target"]
        if value is not None:
            dest = address(value)
            require(all(dest not in (i.network.network_address, i.network.broadcast_address) for i in interfaces.values()), "network/broadcast destination outside unicast model")
    require(case["artifacts"] == {"snapshot.txt": evidence_text(data)}, "snapshot must mirror authoritative JSON")
    return data, interfaces, routes


def analyse(case):
    data, interfaces, routes = validate_data(case)
    decisions, observations = {}, []
    for request in data["requests"]:
        key, target = request["id"], request["target"]
        resolved = data["names"].get(target) if target.endswith(".test") else target
        if resolved is None:
            decisions[key] = "name-unresolved"
            observations.append(f"{key}: {target} has no supplied address; no route lookup is possible from this evidence.")
            continue
        dest = address(resolved)
        if any(dest == iface.ip for iface in interfaces.values()):
            decisions[key] = "local-host"
            observations.append(f"{key}: {target} -> {dest} is this host's own interface address; no Ethernet next hop is selected.")
            continue
        matches = [(r, n) for r, n in routes if dest in n]
        if not matches:
            decisions[key] = "no-route"
            observations.append(f"{key}: {target} -> {dest}; no supplied route matches.")
            continue
        # Prefix length wins before metric; table order must not decide a tie.
        best_rank = min((-n.prefixlen, r["metric"]) for r, n in matches)
        best = [(r, n) for r, n in matches if (-n.prefixlen, r["metric"]) == best_rank]
        candidates = ", ".join(sorted(r["id"] for r, _ in matches))
        if len(best) > 1:
            decisions[key] = "equal-route-cost"
            ids = ", ".join(sorted(r["id"] for r, _ in best))
            observations.append(f"{key}: {target} -> {dest}; matches [{candidates}]; equal best routes [{ids}] at /{-best_rank[0]}, metric {best_rank[1]}; next hop unresolved.")
            continue
        row, prefix = best[0]
        hop = row["via"] or str(dest)
        decisions[key] = "via-gateway" if row["via"] else "on-link"
        observations.append(f"{key}: {target} -> {dest}; matches [{candidates}]; choose {row['id']} {prefix}, metric {row['metric']}, interface {row['interface']}; next-hop/ARP target {hop}; IP destination stays {dest}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITATIONS.copy()}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
