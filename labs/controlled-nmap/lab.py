"""Compare supplied scan rows with a listener snapshot; never runs Nmap."""
from pathlib import Path
import ipaddress
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require

LAB_ID = "controlled-nmap"
ROOT = Path(__file__).resolve().parent


def fields(row, keys):
    require(isinstance(row, dict) and set(row) == set(keys.split()), "unexpected fields")


def port(value):
    require(type(value) is int and 1 <= value <= 65535, "invalid TCP port")


def address(value):
    require(isinstance(value, str) and ipaddress.ip_address(value) in ipaddress.ip_network("192.0.2.0/24"), "use a documentation IPv4 address")


def analyse(case):
    data = case["data"]
    fields(data, "targets ports listeners scans")
    require(all(isinstance(value, list) and len(value) <= 12 for value in data.values()), "bounded lists required")
    require(data["targets"] and data["ports"] and data["scans"], "scope and scan rows required")
    for target in data["targets"]:
        address(target)
    for value in data["ports"]:
        port(value)
    require(len(set(data["targets"])) == len(data["targets"]) and len(set(data["ports"])) == len(data["ports"]), "duplicate scope")
    listeners = {}
    for row in data["listeners"]:
        fields(row, "target port bind service")
        port(row["port"])
        require(row["target"] in data["targets"] and row["port"] in data["ports"], "listener outside scope")
        require(row["bind"] in {"target", "loopback"}, "unsupported bind")
        require(isinstance(row["service"], str) and re.fullmatch(r"[a-z][a-z0-9-]{0,30}", row["service"]), "invalid service name")
        key = (row["target"], row["port"])
        require(key not in listeners, "duplicate listener")
        listeners[key] = row
    decisions, observations, seen = {}, [], set()
    for row in data["scans"]:
        fields(row, "id target port state method label")
        port(row["port"])
        require(row["target"] in data["targets"] and row["port"] in data["ports"], "scan outside explicit scope")
        key = (row["target"], row["port"])
        ident = row["id"]
        require(isinstance(ident, str) and re.fullmatch(r"s[0-9]{2}", ident) and ident not in decisions and key not in seen, "duplicate scan or invalid neutral ID")
        seen.add(key)
        require(row["state"] in {"open", "closed", "filtered"}, "unsupported TCP connect state")
        require(row["method"] in {"none", "table", "probe"} and isinstance(row["label"], str), "invalid service evidence")
        require((row["method"] == "none") == (row["label"] == ""), "label and evidence method conflict")
        require(row["state"] == "open" or row["method"] == "none", "non-open service identification unsupported here")
        require(not row["label"] or re.fullmatch(r"[a-z][a-z0-9-]{0,30}", row["label"]), "invalid service label")
        listener = listeners.get(key)
        reachable_listener = listener is not None and listener["bind"] == "target"
        if row["state"] == "filtered":
            result = "inconclusive-filtered"
        elif row["state"] == "closed":
            result = "snapshot-disagreement" if reachable_listener else "closed-consistent-with-snapshot"
        else:
            result = "open-listener-corroborated" if reachable_listener else "open-needs-listener-review"
            if row["method"] == "probe" and reachable_listener:
                result += ";label-probe-consistent" if row["label"] == listener["service"] else ";label-disagreement"
            else:
                result += ";label-unconfirmed"
        decisions[ident] = result
        local = listener["bind"] + "/" + listener["service"] if listener else "none"
        observations.append(f"{ident}: {row['target']}:{row['port']} {row['state']}; local={local}; label={row['method']}/{row['label'] or '-'}.")
    return {"decisions": decisions, "observations": observations, "limitations": ["Supplied TCP connect scan rows and local listener notes are separate observations; timing, filtering and forwarding can explain disagreement.", "Port-name guesses and service probes do not establish a precise product version, vulnerability or ownership. No scan is executed by this helper."]}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
