"""Small IPv4 path worksheet: routing, inbound rules and an explicit relay."""
from ipaddress import ip_address, ip_network
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAB_ID = "cloud-network-path"
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require

VPC = ip_network("10.44.0.0/16")
DOCS = [ip_network(s) for s in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]
LIMITS = ["IPv4 TCP only. Return routing uses longest-prefix match. Inbound rules allow traffic; established replies and internal outbound traffic are assumed allowed.", "No NAT gateway, IPv6, DNS, network ACL, operating-system firewall or application authentication is modelled. A relay exists only when explicitly listed; this is not a cloud test."]


def keys(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")


def addr(value):
    require(isinstance(value, str), "address must be text")
    result = ip_address(value)
    require(result.version == 4 and (result in VPC or any(result in n for n in DOCS)), "use model VPC or documentation IPv4 addresses")
    return result


def net(value):
    require(isinstance(value, str), "CIDR must be text")
    result = ip_network(value, strict=True)
    require(result.version == 4, "IPv4 only")
    return result


def port(value):
    require(type(value) is int and 1 <= value <= 65535, "TCP port must be 1-65535")


def indexed(value, fields):
    require(isinstance(value, list) and 0 < len(value) <= 20, "supply 1-20 rows")
    output = {}
    for row in value:
        keys(row, fields)
        ident = row["id"]
        require(isinstance(ident, str) and re.fullmatch(r"[a-z][0-9]+", ident) and ident not in output, "use unique neutral IDs")
        output[ident] = row
    return output


def leg(source, endpoint, destination_port):
    external = addr(source) not in VPC
    if external and endpoint["public"] is None:
        return "no-public-address"
    routes = [r for r in endpoint["routes"] if addr(source) in net(r["cidr"])]
    selected = max(routes, key=lambda r: net(r["cidr"]).prefixlen) if routes else None
    expected = "igw" if external else "local"
    if selected is None or selected["target"] != expected:
        return "return-route-missing"
    if not any(addr(source) in net(r["cidr"]) and r["port"] == destination_port for r in endpoint["inbound"]):
        return "inbound-not-allowed"
    return "reachable-in-model"


def analyse(case):
    data = case["data"]
    keys(data, ["endpoints", "relays", "requests"])
    endpoints = indexed(data["endpoints"], ["id", "private", "public", "subnet", "routes", "inbound"])
    addresses = set()
    for endpoint in endpoints.values():
        private = addr(endpoint["private"])
        subnet = net(endpoint["subnet"])
        require(subnet.subnet_of(VPC) and private in subnet and private not in (subnet.network_address, subnet.broadcast_address), "private address must be a host in its VPC subnet")
        for value in (endpoint["private"], endpoint["public"]):
            if value is not None:
                parsed = addr(value)
                require(value not in addresses, "duplicate endpoint address")
                addresses.add(value)
                if value == endpoint["public"]:
                    require(any(parsed in n for n in DOCS), "public address must be a documentation address")
        require(isinstance(endpoint["routes"], list) and len(endpoint["routes"]) <= 20, "invalid routes")
        seen = set()
        for route in endpoint["routes"]:
            keys(route, ["cidr", "target"])
            destination = net(route["cidr"])
            require(destination not in seen and route["target"] in ("local", "igw", "blackhole"), "duplicate route or unsupported target")
            seen.add(destination)
        require(isinstance(endpoint["inbound"], list) and len(endpoint["inbound"]) <= 20, "invalid inbound rules")
        for rule in endpoint["inbound"]:
            keys(rule, ["cidr", "port"])
            net(rule["cidr"])
            port(rule["port"])
    require(isinstance(data["relays"], list) and len(data["relays"]) <= 20, "invalid relays")
    relay_keys = set()
    request_keys = set()
    for relay in data["relays"]:
        keys(relay, ["via", "listen", "target", "port"])
        require(isinstance(relay["via"], str) and relay["via"] in endpoints and isinstance(relay["target"], str) and relay["target"] in endpoints and relay["via"] != relay["target"], "unknown or circular relay")
        port(relay["listen"])
        port(relay["port"])
        key = (relay["via"], relay["listen"])
        require(key not in relay_keys, "ambiguous relay listener")
        relay_keys.add(key)
        request_key = (relay["via"], relay["target"], relay["port"])
        require(request_key not in request_keys, "ambiguous relay request mapping")
        request_keys.add(request_key)
    requests = indexed(data["requests"], ["id", "source", "target", "port", "via"])
    decisions, observations = {}, []
    for row in requests.values():
        addr(row["source"])
        port(row["port"])
        require(isinstance(row["target"], str) and row["target"] in endpoints, "unknown destination")
        if row["via"] is None:
            verdict = leg(row["source"], endpoints[row["target"]], row["port"])
            evidence = f"direct {row['source']} -> {row['target']}:{row['port']}"
        else:
            require(isinstance(row["via"], str) and row["via"] in endpoints, "unknown relay")
            relay = next((r for r in data["relays"] if r["via"] == row["via"] and r["target"] == row["target"] and r["port"] == row["port"]), None)
            require(relay is not None, "request has no declared relay mapping")
            first = leg(row["source"], endpoints[relay["via"]], relay["listen"])
            second = leg(endpoints[relay["via"]]["private"], endpoints[row["target"]], row["port"])
            verdict = "reachable-via-relay" if first == second == "reachable-in-model" else f"relay-leg-1:{first}" if first != "reachable-in-model" else f"relay-leg-2:{second}"
            evidence = f"{row['source']} -> {relay['via']}:{relay['listen']} -> {row['target']}:{row['port']}; legs={first},{second}"
        decisions[row["id"]] = verdict
        observations.append(f"{row['id']}: {evidence}; result={verdict}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
