"""Original fictional evidence exercise. No network or host changes."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "cloud-audit-triage"


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

from datetime import datetime, timedelta

LIMITS = [
    "This fictional schema is not a CloudTrail parser; identity/session equality and a 15-minute window support correlation, not attribution to a person.",
    "Configured logging and supplied events do not prove complete delivery; absent records cannot prove that no activity occurred.",
]
ACTIONS = {"sign-in", "read-object", "change-policy", "disable-logging"}


def instant(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value), "expected UTC YYYY-MM-DDTHH:MM:SSZ")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise ValueError("invalid timestamp") from error


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "window_start window_end logging approved_changes events", "data")
    start, end = instant(data["window_start"]), instant(data["window_end"])
    require(start < end, "window must increase")
    fields(data["logging"], "management data", "logging")
    for key, value in data["logging"].items():
        boolean(value, key)
    require(isinstance(data["approved_changes"], list) and len(data["approved_changes"]) <= 60, "invalid approvals")
    approvals = []
    for approval in data["approved_changes"]:
        fields(approval, "identity action resource from to", "approval")
        for key in ("identity", "resource"):
            identifier(approval[key])
        require(approval["action"] in ("change-policy", "disable-logging"), "only change actions can be approved")
        low, high = instant(approval["from"]), instant(approval["to"])
        require(low <= high, "approval window is reversed")
        signature = (approval["identity"], approval["action"], approval["resource"], low, high)
        require(signature not in approvals, "duplicate approval")
        approvals.append(signature)
    events = records(data["events"], "events")
    parsed = []
    for event in events:
        fields(event, "id at identity session action result resource", "event")
        for key in ("identity", "session", "resource"):
            identifier(event[key])
        require(event["id"] != "logging", "logging is a reserved decision ID")
        require(isinstance(event["action"], str) and event["action"] in ACTIONS
                and event["result"] in ("success", "denied"), "unsupported action/result")
        timestamp = instant(event["at"])
        require(start <= timestamp <= end, "event outside evidence window")
        require(event["action"] != "sign-in" or event["resource"] == "identity-service", "sign-in resource must be identity-service")
        parsed.append((timestamp, event))
    # Sorting a new list preserves supplied input order and data.
    parsed.sort(key=lambda pair: (pair[0], pair[1]["id"]))
    decisions, observations = {}, []
    interrupted = False
    for timestamp, event in parsed:
        correlated = [other["id"] for other_time, other in parsed
                      if other["action"] == "sign-in" and other["result"] == "success"
                      and other["identity"] == event["identity"] and other["session"] == event["session"]
                      and timedelta(0) <= timestamp - other_time <= timedelta(minutes=15)
                      and other["id"] != event["id"]]
        approved = any(identity == event["identity"] and action == event["action"] and resource == event["resource"] and low <= timestamp <= high
                       for identity, action, resource, low, high in approvals)
        if event["result"] == "denied":
            decision = "denied-no-success-evidence"
        elif event["action"] == "sign-in":
            decision = "authentication-only"
        elif not correlated:
            decision = "successful-action-unattributed"
        elif event["action"] == "read-object":
            decision = "successful-read-correlated"
        else:
            decision = "approved-change-correlated" if approved else "unapproved-change-correlated"
        interrupted |= event["action"] == "disable-logging" and event["result"] == "success"
        decisions[event["id"]] = decision
        observations.append(f"{event['id']}: {event['at']} identity={event['identity']} session={event['session']} action={event['action']} result={event['result']} resource={event['resource']}; sign-ins={joined(correlated)}; approved={str(approved).lower()}.")
    gaps = sorted(key for key, enabled in data["logging"].items() if not enabled)
    coverage = "coverage-gap:" + ",".join(gaps) if gaps else "coverage-configured"
    if interrupted:
        coverage += ";interruption-observed"
    decisions["logging"] = coverage
    observations.append(f"logging: disabled-categories={joined(gaps)}; successful-disable={str(interrupted).lower()}.")
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
