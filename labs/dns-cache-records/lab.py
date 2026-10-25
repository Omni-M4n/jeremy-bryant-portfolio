"""Inspect a tiny supplied DNS cache; no network requests."""
from pathlib import Path
import ipaddress
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require

LAB_ID = "dns-cache-records"
ROOT = Path(__file__).resolve().parent
TYPES = {"A", "AAAA", "CNAME", "MX"}


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), "unexpected fields")


def number(value):
    require(type(value) is int and 0 <= value <= 86400, "expected whole seconds from 0 to 86400")


def name(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\.test", value), "use lowercase .test names")


def analyse(case):
    data = case["data"]
    fields(data, "records negatives queries")
    require(all(isinstance(data[k], list) and len(data[k]) <= 30 for k in data), "bounded lists required")
    records, negatives = {}, []
    for row in data["records"]:
        fields(row, "owner type value received ttl")
        name(row["owner"])
        require(row["type"] in TYPES, "unsupported record type")
        number(row["received"])
        number(row["ttl"])
        key = (row["owner"], row["type"])
        require(key not in records, "one value per owner/type in this model")
        if row["type"] in {"A", "AAAA"}:
            require(isinstance(row["value"], str), "address must be text")
            address = ipaddress.ip_address(row["value"])
            net = ipaddress.ip_network("192.0.2.0/24" if row["type"] == "A" else "2001:db8::/32")
            require(address in net, "address outside this model's documentation ranges")
        elif row["type"] == "CNAME":
            name(row["value"])
        else:
            require(isinstance(row["value"], str), "MX must be preference and hostname")
            parts = row["value"].split()
            require(len(parts) == 2 and parts[0].isdigit() and 0 <= int(parts[0]) <= 65535, "invalid MX")
            name(parts[1])
        records[key] = row
    for owner, kind in records:
        if kind == "CNAME":
            require(sum(key[0] == owner for key in records) == 1, "alias cannot have other records here")
            seen, cursor = set(), owner
            while (cursor, "CNAME") in records:
                require(cursor not in seen, "alias loop")
                seen.add(cursor)
                cursor = records[(cursor, "CNAME")]["value"]
    for row in data["negatives"]:
        fields(row, "owner kind qtype received soa_ttl minimum")
        name(row["owner"])
        require(row["kind"] in {"NXDOMAIN", "NODATA"}, "unknown negative kind")
        require(row["qtype"] in TYPES, "unsupported negative question type")
        for key in ("received", "soa_ttl", "minimum"):
            number(row[key])
        require(not any(key[0] == row["owner"] and (row["kind"] == "NXDOMAIN" or key[1] in {row["qtype"], "CNAME"}) for key in records), "conflicting positive and negative evidence")
        require(not any(old["owner"] == row["owner"] and (old["kind"] == "NXDOMAIN" or row["kind"] == "NXDOMAIN" or old["qtype"] == row["qtype"]) for old in negatives), "overlapping negative entries")
        negatives.append(row)
    decisions, observations = {}, []
    require(data["queries"], "at least one query required")
    for query in data["queries"]:
        fields(query, "id name type at")
        name(query["name"])
        number(query["at"])
        key = query["id"]
        require(isinstance(key, str) and re.fullmatch(r"q[0-9]{2}", key) and key not in decisions, "unique neutral qNN ID required")
        require(query["type"] in TYPES, "unsupported query type")
        require(all(query["at"] >= row["received"] for row in list(records.values()) + negatives), "query predates snapshot data")
        cursor, trace = query["name"], []
        while True:
            row = records.get((cursor, query["type"])) or records.get((cursor, "CNAME"))
            negative = next((n for n in negatives if n["owner"] == cursor and (n["kind"] == "NXDOMAIN" or n["qtype"] == query["type"])), None)
            if row:
                left = max(0, row["received"] + row["ttl"] - query["at"])
                trace.append(f"{cursor} {row['type']} remaining={left}s")
                if left == 0:
                    result = "refresh-required"
                    break
                if row["type"] == "CNAME" and query["type"] != "CNAME":
                    cursor = row["value"]
                    continue
                result = "cached-answer:" + row["value"]
            elif negative:
                left = max(0, negative["received"] + min(negative["soa_ttl"], negative["minimum"]) - query["at"])
                trace.append(f"{cursor} {negative['kind']} remaining={left}s")
                result = "cached-negative:" + negative["kind"] if left else "refresh-required"
            else:
                trace.append(f"{cursor} {query['type']} absent")
                result = "refresh-required"
            break
        decisions[key] = result
        observations.append(f"{key}: " + "; ".join(trace) + ".")
    return {"decisions": decisions, "observations": observations, "limitations": ["One value per owner/type, one supplied cache, integer seconds; no live lookup, refresh, prefetch, serve-stale, DNSSEC or resolver failure caching.", "An expired or missing entry requires fresh evidence; it does not prove that a name or service is unavailable."]}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
