"""Compare supplied IPv4/IPv6 reachability; no socket or firewall operations."""
from pathlib import Path
import ipaddress
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require

LAB_ID = "ipv6-parity"
ROOT = Path(__file__).resolve().parent


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), "unexpected fields")


def analyse(case):
    data = case["data"]
    fields(data, "services")
    require(isinstance(data["services"], list) and 1 <= len(data["services"]) <= 12, "one to twelve services required")
    decisions, observations, ports = {}, [], set()
    for service in data["services"]:
        fields(service, "id port intended ipv4 ipv6")
        ident = service["id"]
        require(isinstance(ident, str) and re.fullmatch(r"s[0-9]{2}", ident) and ident + "-parity" not in decisions, "unique neutral service ID required")
        require(type(service["port"]) is int and 1 <= service["port"] <= 65535 and service["port"] not in ports, "invalid or duplicate service port")
        ports.add(service["port"])
        require(service["intended"] in {"allow", "deny"}, "intended must be allow or deny for both families")
        results = []
        for family in ("ipv4", "ipv6"):
            row = service[family]
            fields(row, "address listener configured_rule outcome")
            require(isinstance(row["address"], str), "address must be text")
            address = ipaddress.ip_address(row["address"])
            net = ipaddress.ip_network("192.0.2.0/24" if family == "ipv4" else "2001:db8::/32")
            require(address in net, "wrong family or address outside documentation range")
            require(type(row["listener"]) is bool, "listener must be boolean")
            require(row["configured_rule"] in {"allow", "deny", "not-reviewed"}, "unsupported rule summary")
            require(row["outcome"] in {"connect", "refused", "timeout", "not-tested"}, "unsupported outcome")
            require(row["outcome"] != "connect" or row["listener"], "connected without a listener; forwarding is outside this model")
            if row["outcome"] == "not-tested":
                result = "unverified"
            elif row["outcome"] == "connect":
                result = "reachable-as-intended" if service["intended"] == "allow" else "reachable-outside-intent"
                if row["configured_rule"] == "deny":
                    result += ";rule-observation-disagreement"
            else:
                result = "allowed-path-not-working" if service["intended"] == "allow" else "not-reachable-cause-unproven"
            decisions[ident + "-" + family] = result
            observations.append(f"{ident} {family}: {row['address']}:{service['port']}; listener={str(row['listener']).lower()}; rule={row['configured_rule']}; outcome={row['outcome']}.")
            results.append(row["outcome"])
        if "not-tested" in results:
            parity = "comparison-incomplete"
        elif (results[0] == "connect") != (results[1] == "connect"):
            parity = "unequal-observed-reachability"
        elif results[0] == "connect":
            parity = "both-observed-reachable"
        else:
            parity = "both-observed-not-reachable"
        decisions[ident + "-parity"] = parity
    return {"decisions": decisions, "observations": observations, "limitations": ["One named service, client position and time per row; a successful connection does not prove public reachability, and failed connections do not prove a firewall caused them.", "IPv4 and IPv6 rules, listeners and paths need separate evidence. Shared inet tables or dual-stack sockets alone do not establish equal enforcement."]}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
