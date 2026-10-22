"""Original fictional evidence analysis; no host inspection or network activity."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "scheduled-task-review"

def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": unsupported or missing fields")

def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 300 and value.strip() == value, label + ": bounded nonempty text required")


import re

FIELDS = ["id", "daily_time", "account", "action"]

def tasks(rows, label, approval=False):
    require(isinstance(rows, list) and len(rows) <= 30, label + ": expected at most 30 rows")
    result = {}
    for row in rows:
        exact(row, FIELDS + (["reason"] if approval else []), label)
        for key in ("id", "account", "action"):
            text(row[key], key)
        require(row["id"] not in result, "duplicate task ID in " + label)
        require(isinstance(row["daily_time"], str) and re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", row["daily_time"]), "daily_time must be HH:MM")
        require(row["action"].startswith("C:/Lab/") and ".." not in row["action"] and "\\" not in row["action"], "use a literal fictional C:/Lab/ action")
        if approval:
            text(row["reason"], "approval reason")
        result[row["id"]] = row
    return result

def signature(row):
    return tuple(row[key] for key in ("daily_time", "account", "action"))

def describe(row):
    return f'{row["daily_time"]}|{row["account"]}|{row["action"]}'

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["baseline", "observed", "approvals"], "data")
    baseline = tasks(data["baseline"], "baseline")
    observed = tasks(data["observed"], "observed")
    approvals = tasks(data["approvals"], "approvals", True)
    require(bool(baseline or observed), "at least one task required")
    require(set(approvals) <= set(observed), "approval must refer to an observed task")
    decisions, observations = {}, []
    for task_id in sorted(set(baseline) | set(observed)):
        old, new, approved = baseline.get(task_id), observed.get(task_id), approvals.get(task_id)
        if new is None:
            result = "missing-from-snapshot"
        elif old and signature(old) == signature(new):
            result = "matches-baseline"
        elif approved and signature(approved) == signature(new):
            result = "approved-maintenance-difference"
        elif old is None:
            result = "unregistered-task-review"
        else:
            result = "unapproved-change-review"
        decisions[task_id] = result
        observations.append(f'{task_id}: baseline={describe(old) if old else "absent"}; observed={describe(new) if new else "absent"}; approval={describe(approved) if approved else "none"}.')
    return {"decisions": decisions, "observations": observations, "limitations": [
        "Daily time, account and literal action path are compared exactly; this is not the Windows Task Scheduler XML parser.",
        "A missing task may reflect incomplete collection. A change can be benign maintenance; confirm approval scope before escalation.",
        "Matching an approval or baseline does not verify executable contents, actual execution, permissions or safety. No task was created or run."]}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
