"""Review a supplied before/during/after matrix; never changes a firewall."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require

LAB_ID = "firewall-enforcement"
ROOT = Path(__file__).resolve().parent


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), "unexpected fields")


def analyse(case):
    data = case["data"]
    fields(data, "baseline_hash restored_hash rule_removed probes")
    for key in ("baseline_hash", "restored_hash"):
        require(isinstance(data[key], str) and re.fullmatch(r"[0-9a-f]{64}", data[key]), "expected SHA-256 text")
    require(type(data["rule_removed"]) is bool, "rule_removed must be boolean")
    require(isinstance(data["probes"], list) and 2 <= len(data["probes"]) <= 8, "two to eight probes required")
    seen, ports = set(), set()
    for row in data["probes"]:
        fields(row, "id port expected before during after hits")
        require(isinstance(row["id"], str) and re.fullmatch(r"p[0-9]{2}", row["id"]) and row["id"] not in seen, "unique neutral probe ID required")
        seen.add(row["id"])
        require(type(row["port"]) is int and 1 <= row["port"] <= 65535 and row["port"] not in ports, "invalid or duplicate port")
        ports.add(row["port"])
        require(row["expected"] in {"allow", "deny"}, "expected must be allow or deny")
        require(type(row["hits"]) is int and 0 <= row["hits"] <= 10000, "invalid rule counter delta")
        for phase in ("before", "during", "after"):
            snapshot = row[phase]
            fields(snapshot, "listener outcome")
            require(type(snapshot["listener"]) is bool and snapshot["outcome"] in {"connect", "refused", "timeout"}, "invalid connection snapshot")
            require(snapshot["outcome"] != "connect" or snapshot["listener"], "connection without a listener is outside this no-forwarding model")
        require(row["during"]["outcome"] != "connect" or row["hits"] == 0, "successful isolated probe conflicts with matching drop hits")
    require({r["expected"] for r in data["probes"]} == {"allow", "deny"}, "one allow and one deny control required")
    control_ok = all(r["before"]["outcome"] == "connect" and r["during"]["outcome"] == "connect" for r in data["probes"] if r["expected"] == "allow")
    decisions, observations = {}, []
    for row in data["probes"]:
        if row["before"]["outcome"] != "connect":
            result = "baseline-not-established"
        elif row["expected"] == "allow":
            result = "permitted-supported" if row["during"]["outcome"] == "connect" else "permitted-path-failed"
        elif row["during"]["outcome"] == "connect":
            result = "deny-not-enforced"
        elif row["during"]["listener"] and row["during"]["outcome"] == "timeout" and row["hits"] > 0 and control_ok:
            result = "deny-supported-by-control-and-counter"
        else:
            result = "failure-needs-cause-check"
        decisions[row["id"]] = result
        observations.append(f"{row['id']}: port={row['port']}; intended={row['expected']}; before={row['before']['outcome']}; during={row['during']['outcome']}; listener-during={str(row['during']['listener']).lower()}; drop-hits={row['hits']}; after={row['after']['outcome']}.")
    restored = data["baseline_hash"] == data["restored_hash"] and data["rule_removed"] and all(r["before"]["outcome"] == "connect" and r["after"]["outcome"] == "connect" for r in data["probes"])
    decisions["rollback"] = "rollback-supported" if restored else "rollback-not-confirmed"
    observations.append(f"rollback: export-match={str(data['baseline_hash'] == data['restored_hash']).lower()}; temporary-rule-removed={str(data['rule_removed']).lower()}.")
    return {"decisions": decisions, "observations": observations, "limitations": ["Synthetic snapshots assume one client, fresh TCP attempts, no forwarding and counter deltas isolated to each attempted connection; packet counts need not equal connection counts.", "A timeout alone does not identify a firewall. Export equality and restored connectivity support only this temporary-rule rollback, not the whole system's security."]}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
