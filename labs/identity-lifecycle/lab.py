"""Original fictional evidence exercise. No network or host changes."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "identity-lifecycle"


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()),
            f"{label}: missing or unsupported fields")


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 240,
            f"{label}: expected nonempty text up to 240 characters")


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}", value),
            "record IDs must be lowercase letters, digits and hyphens")


def records(value, label):
    require(isinstance(value, list) and 0 < len(value) <= 60,
            f"{label}: expected 1-60 records")
    seen = set()
    for row in value:
        require(isinstance(row, dict) and "id" in row, f"{label}: invalid record")
        identifier(row["id"])
        require(row["id"] not in seen, f"{label}: duplicate ID")
        seen.add(row["id"])
    return value


def boolean(value, label):
    require(type(value) is bool, f"{label}: expected boolean")


def joined(values):
    return ",".join(sorted(values)) or "none"

from datetime import date

LIMITS = [
    "Dates represent whole UTC review days; expiry is inclusive and no timezone or intraday HR feed is modelled.",
    "This produces a proposed access delta only; approvals, session revocation, ownership transfer and actual directory changes need separate checks.",
]


def day(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value), "expected YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("invalid calendar date") from error


def access(values):
    require(isinstance(values, list) and len(values) <= 40, "access must be a bounded list")
    for value in values:
        identifier(value)
        require(value != "none", "none is reserved for an empty access set")
    require(len(values) == len(set(values)), "duplicate access item")
    return set(values)


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "as_of people", "data")
    today = day(data["as_of"])
    decisions, observations = {}, []
    for row in records(data["people"], "people"):
        fields(row, "id event effective_on current required exceptions", "person")
        require(row["event"] in ("joiner", "mover", "leaver"), "unsupported lifecycle event")
        effective = day(row["effective_on"])
        current, required = access(row["current"]), access(row["required"])
        require(isinstance(row["exceptions"], list) and len(row["exceptions"]) <= 40, "exceptions must be a bounded list")
        require(row["event"] == "mover" or not row["exceptions"], "only mover handover exceptions are supported")
        require(row["event"] != "leaver" or not required, "leaver cannot retain required access")
        active, expired, seen = set(), set(), set()
        for exception in row["exceptions"]:
            fields(exception, "access approved_by expires_on", "exception")
            item = exception["access"]
            identifier(item)
            identifier(exception["approved_by"])
            expiry = day(exception["expires_on"])
            require(item in current and item not in required, "exception must cover existing stale access only")
            require(item not in seen, "duplicate exception")
            require(expiry >= effective, "exception expires before the move")
            seen.add(item)
            (active if expiry >= today else expired).add(item)
        due = effective <= today
        if due:
            target = required | active
        elif row["event"] == "joiner":
            target = set()
        else:
            target = current
        added, removed, retained = target - current, current - target, current & target
        decisions[row["id"]] = f"add:{joined(added)};remove:{joined(removed)};retain:{joined(retained)}"
        phase = "due" if due else "future"
        observations.append(f"{row['id']}: {row['event']} {phase} on {row['effective_on']}; active-exceptions={joined(active)}; expired-exceptions={joined(expired)}; target={joined(target)}.")
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
