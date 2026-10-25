"""Read fictional route and DNS snapshots; never connect a VPN or send DNS."""
from pathlib import Path
import ipaddress
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require

LAB_ID = "vpn-routing-review"
ROOT = Path(__file__).resolve().parent
NETS = (ipaddress.ip_network("192.0.2.0/24"), ipaddress.ip_network("198.51.100.0/24"), ipaddress.ip_network("203.0.113.0/24"), ipaddress.ip_network("2001:db8::/32"))


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), "unexpected fields")


def address(value):
    require(isinstance(value, str), "address must be text")
    parsed = ipaddress.ip_address(value)
    require(any(parsed.version == net.version and parsed in net for net in NETS), "use documentation addresses")
    return parsed


def domain(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\.test", value), "use lowercase .test names")


def routes(rows):
    require(isinstance(rows, list) and len(rows) <= 20, "bounded route list required")
    result, seen = [], set()
    for row in rows:
        fields(row, "prefix metric path")
        require(isinstance(row["prefix"], str), "prefix must be text")
        net = ipaddress.ip_network(row["prefix"], strict=True)
        require(net.prefixlen == 0 or any(net.version == allowed.version and net.subnet_of(allowed) for allowed in NETS), "route outside documentation ranges or default")
        require(type(row["metric"]) is int and 0 <= row["metric"] <= 65535 and row["path"] in {"local", "tunnel"}, "invalid metric or path")
        key = (str(net), row["metric"])
        require(key not in seen, "equal-prefix/metric ties are unsupported")
        seen.add(key)
        result.append((net, row["metric"], row["path"]))
    return result


def route_to(destination, rows):
    options = [r for r in rows if destination.version == r[0].version and destination in r[0]]
    if not options:
        return "none", "no-route"
    net, metric, path = min(options, key=lambda r: (-r[0].prefixlen, r[1]))
    return path, f"{net} metric={metric}"


def dns_rules(rows):
    require(isinstance(rows, list) and len(rows) <= 12, "bounded DNS rule list required")
    seen = set()
    for row in rows:
        fields(row, "suffix server")
        if row["suffix"] != ".":
            domain(row["suffix"])
        address(row["server"])
        key = (row["suffix"], row["server"])
        require(key not in seen, "duplicate DNS rule")
        seen.add(key)
    return rows


def dns_path(name, rules, routing):
    matches = [r for r in rules if r["suffix"] == "." or name == r["suffix"] or name.endswith("." + r["suffix"])]
    if not matches:
        return "none", "no-resolver"
    score = lambda r: 0 if r["suffix"] == "." else len(r["suffix"].split("."))
    best = max(map(score, matches))
    selected = [r for r in matches if score(r) == best]
    paths, evidence = set(), []
    for row in sorted(selected, key=lambda r: r["server"]):
        path, match = route_to(address(row["server"]), routing)
        paths.add(path)
        evidence.append(f"{row['suffix']}->{row['server']} via {path} ({match})")
    return "+".join(sorted(paths)), "; ".join(evidence)


def analyse(case):
    data = case["data"]
    fields(data, "before_routes after_routes before_dns after_dns flows queries")
    before, after = routes(data["before_routes"]), routes(data["after_routes"])
    dns_before, dns_after = dns_rules(data["before_dns"]), dns_rules(data["after_dns"])
    require(all(isinstance(data[k], list) and len(data[k]) <= 12 for k in ("flows", "queries")) and data["flows"] and data["queries"], "bounded nonempty flow and query lists required")
    decisions, observations = {}, []
    for group in ("flows", "queries"):
        for row in data[group]:
            fields(row, "id destination intended" if group == "flows" else "id name intended")
            ident = row["id"]
            pattern = r"f[0-9]{2}" if group == "flows" else r"q[0-9]{2}"
            require(isinstance(ident, str) and re.fullmatch(pattern, ident) and ident not in decisions, "unique neutral row ID required")
            require(row["intended"] in {"local", "tunnel"}, "intended path must be local or tunnel")
            if group == "flows":
                destination = address(row["destination"])
                old, old_evidence = route_to(destination, before)
                new, new_evidence = route_to(destination, after)
            else:
                domain(row["name"])
                old, old_evidence = dns_path(row["name"], dns_before, before)
                new, new_evidence = dns_path(row["name"], dns_after, after)
            met = "met" if new == row["intended"] else "unmet"
            decisions[ident] = f"before:{old};after:{new};intent:{met}"
            observations.append(f"{ident}: before {old_evidence}; after {new_evidence}; intended={row['intended']}.")
    return {"decisions": decisions, "observations": observations, "limitations": ["This is one simple destination-routing table per snapshot: longest prefix, then lowest metric. No policy rules, ECMP, source routing, tunnel handshake or reachability is modelled.", "DNS uses explicit suffix rules with unbound resolver addresses, then routes to those addresses. Real per-link resolver binding, fallback, caches, encrypted DNS and application-specific DNS require separate evidence."]}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
