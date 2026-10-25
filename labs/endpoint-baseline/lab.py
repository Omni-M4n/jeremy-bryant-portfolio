"""Compare a small fictional endpoint baseline with dated observations."""
from datetime import date
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = "endpoint-baseline"
KINDS = {"service-active", "updates-pending", "standard-user", "lock-seconds"}

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def day(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), "ISO date required")
    return date.fromisoformat(value)

def text(value):
    require(isinstance(value, str) and 0 < len(value) <= 200 and value.strip() == value, "bounded nonempty text required")

def control_value(kind, value, required=False):
    if kind in ("service-active", "standard-user"):
        require(type(value) is bool, "boolean control value required")
    else:
        maximum = 86400 if kind == "lock-seconds" else 10000
        require(type(value) is int and 0 <= value <= maximum, "bounded integer control required")
        if required and kind == "lock-seconds":
            require(value > 0, "required lock time must be positive")

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["as_of", "controls", "exceptions", "normal_use"])
    today = day(data["as_of"])
    require(data["normal_use"] in ("pass", "fail", "not-run"), "unsupported normal-use result")
    require(isinstance(data["controls"], list) and len(data["controls"]) == 4, "provide all four controls")
    controls, kinds = {}, set()
    for row in data["controls"]:
        exact(row, ["id", "kind", "required", "observed", "observed_on", "evidence"])
        identity, kind = row["id"], row["kind"]
        require(isinstance(identity, str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", identity) and identity != "u1" and identity not in controls, "unique nonreserved ID required")
        require(isinstance(kind, str) and kind in KINDS and kind not in kinds, "four distinct supported kinds required")
        control_value(kind, row["required"], True)
        if row["observed"] is None:
            require(row["observed_on"] == "" and row["evidence"] == "", "missing observation cannot carry dated evidence")
        else:
            control_value(kind, row["observed"])
            require(day(row["observed_on"]) <= today, "future observation")
            text(row["evidence"])
        controls[identity] = row; kinds.add(kind)
    require(isinstance(data["exceptions"], list) and len(data["exceptions"]) <= 4, "bounded exceptions required")
    exceptions = {}
    for row in data["exceptions"]:
        exact(row, ["control_id", "reason", "approved_by", "expires_on"])
        identity = row["control_id"]
        require(isinstance(identity, str) and identity in controls and identity not in exceptions, "unique known exception control required")
        text(row["reason"]); text(row["approved_by"]); day(row["expires_on"])
        exceptions[identity] = row
    decisions, observations = {}, []
    for identity, row in controls.items():
        observed = row["observed"]
        age = (today - day(row["observed_on"])).days if observed is not None else None
        matches = observed == row["required"]
        if row["kind"] in ("updates-pending", "lock-seconds") and observed is not None:
            matches = observed <= row["required"] and (row["kind"] != "lock-seconds" or observed > 0)
        exception = exceptions.get(identity)
        active = exception is not None and day(exception["expires_on"]) >= today
        if observed is None:
            outcome = "not-observed"
        elif age > 7:
            outcome = "recheck-stale"
        elif matches:
            outcome = "matches-requirement"
        elif active:
            outcome = "exception-active"
        elif exception:
            outcome = "exception-expired"
        else:
            outcome = "change-needed"
        decisions[identity] = outcome
        shown = str(observed).lower() if observed is not None else "none"
        observations.append(f"{identity}: {row['kind']}; observed={shown}; age-days={age if age is not None else 'none'}; active-exception={str(active).lower()}.")
    decisions["u1"] = {"pass":"normal-use-passed", "fail":"normal-use-failed", "not-run":"normal-use-not-tested"}[data["normal_use"]]
    observations.append(f"u1: normal-use={data['normal_use']}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}

LIMITS = ['This is a four-control lab baseline, not a complete hardening standard or a measure of endpoint safety.', 'Supplied observations and approvals need real evidence. Passing controls does not replace a normal-use test or resolve an expired exception.']

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
