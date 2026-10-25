"""Bounded fictional evidence; no host commands are executed."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = "patch-rollback"

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["changes"])
    require(isinstance(data["changes"], list) and 1 <= len(data["changes"]) <= 20, "provide 1-20 changes")
    decisions, observations = {}, []
    for row in data["changes"]:
        exact(row, ["id", "baseline_version", "target_version", "installed_version", "source", "install_exit", "smoke", "rollback_version", "rollback_smoke"])
        require(isinstance(row["id"], str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", row["id"]), "plain ID required")
        require(row["id"] not in decisions, "duplicate change ID")
        for field in ("baseline_version", "target_version", "installed_version", "rollback_version"):
            value = row[field]
            require(isinstance(value, str) and (value == "" and field == "rollback_version" or re.fullmatch(r"[0-9][A-Za-z0-9.+:~-]{0,49}", value)), "plain version required")
        require(row["baseline_version"] != row["target_version"], "target must differ from baseline")
        require(row["source"] in ("official", "unverified"), "unknown source status")
        require(type(row["install_exit"]) is int and 0 <= row["install_exit"] <= 255, "exit status must be integer 0-255")
        for field in ("smoke", "rollback_smoke"):
            require(row[field] in ("pass", "fail", "not-run"), "unknown smoke result")
        require(bool(row["rollback_version"]) or row["rollback_smoke"] == "not-run", "rollback smoke needs version evidence")
        restored = row["rollback_version"] == row["baseline_version"] and row["rollback_smoke"] == "pass"
        if row["source"] == "unverified":
            outcome = "source-unverified"
        elif row["install_exit"] != 0:
            outcome = "install-error-investigate"
        elif row["installed_version"] != row["target_version"]:
            outcome = "version-not-confirmed"
        elif row["smoke"] == "not-run":
            outcome = "need-smoke-test"
        elif row["smoke"] == "fail":
            outcome = "regression-rollback-verified" if restored else "regression-recovery-needed"
        elif restored:
            outcome = "update-and-rollback-verified"
        elif row["rollback_version"]:
            outcome = "update-verified-rollback-incomplete"
        else:
            outcome = "update-verified-rollback-untested"
        decisions[row["id"]] = outcome
        observations.append(f"{row['id']}: target={row['target_version']}; installed={row['installed_version']}; exit={row['install_exit']}; smoke={row['smoke']}; rollback={row['rollback_version'] or 'none'}/{row['rollback_smoke']}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}

LIMITS = ['Version strings are compared exactly; this helper does not order versions or prove that a release fixes a vulnerability.', 'Smoke and source fields are supplied evidence summaries. A real package change needs retained tool output and a VM recovery test.']

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
