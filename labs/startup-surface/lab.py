"""Bounded fictional inventory; no programs or settings are changed."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = "startup-surface"
FIELDS = ["mechanism", "command", "identity", "owner", "sha256"]

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def entry(row):
    exact(row, ["id", *FIELDS])
    require(isinstance(row["id"], str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", row["id"]), "plain ID required")
    require(row["mechanism"] in ("windows-service", "startup-folder", "run-key", "systemd-unit"), "unknown mechanism")
    for field in ("command", "identity", "owner"):
        require(isinstance(row[field], str) and 0 < len(row[field]) <= 200
                and row[field].strip() == row[field] and row[field].isprintable(),
                "bounded printable single-line evidence required")
    require(isinstance(row["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), "full lowercase SHA-256 required")
    return tuple(row[field] for field in FIELDS)

def indexed(value):
    require(isinstance(value, list) and len(value) <= 30, "bounded inventory list required")
    result = {}
    for row in value:
        key = entry(row)
        require(row["id"] not in result, "duplicate startup ID")
        result[row["id"]] = key
    return result

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["baseline", "observed", "approvals"])
    baseline, observed, approvals = (indexed(data[field]) for field in ("baseline", "observed", "approvals"))
    require(bool(baseline or observed), "inventory cannot be empty on both sides")
    require(set(approvals) <= set(observed), "approval needs an observed record")
    for identity in approvals:
        require(approvals[identity] == observed[identity], "approval must describe exact observed state")
    decisions, observations = {}, []
    for identity in sorted(set(baseline) | set(observed)):
        if identity not in observed:
            result = "missing-follow-up"
        elif identity not in baseline:
            result = "approved-addition" if identity in approvals else "unexplained-addition"
        elif baseline[identity] == observed[identity]:
            result = "matches-baseline"
        else:
            result = "approved-change" if identity in approvals else "unexplained-change"
        decisions[identity] = result
        before, after = baseline.get(identity), observed.get(identity)
        changed = [field for index,field in enumerate(FIELDS) if before and after and before[index] != after[index]]
        observations.append(f"{identity}: before={str(before is not None).lower()}; after={str(after is not None).lower()}; changed={','.join(changed) or 'none'}; exact-approval={str(identity in approvals).lower()}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}

LIMITS = ['This comparison covers only the listed startup records and exact approved configurations; it does not detect every persistence method.', 'Approval and an unchanged digest do not prove that a program is harmless. Missing or unexplained records need investigation, not automatic removal.']

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
