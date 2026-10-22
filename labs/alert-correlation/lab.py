"""Original fictional evidence analysis; no host inspection or network activity."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "alert-correlation"

def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": unsupported or missing fields")

def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 300 and value.strip() == value, label + ": bounded nonempty text required")


from datetime import datetime, timezone
import re

def moment(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value), "alerts require UTC timestamps with seconds")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("invalid alert timestamp") from error

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["window_seconds", "alerts"], "data")
    window = data["window_seconds"]
    require(type(window) is int and 1 <= window <= 3600, "window must be 1-3600 seconds")
    require(isinstance(data["alerts"], list) and 1 <= len(data["alerts"]) <= 100, "provide 1-100 alert deliveries")
    unique, times = {}, {}
    for row in data["alerts"]:
        exact(row, ["id", "host", "account", "kind", "time"], "alert")
        text(row["id"], "alert ID")
        require(isinstance(row["host"], str) and re.fullmatch(r"[a-z0-9-]+\.test", row["host"]), "host must be a fictional .test name")
        require(isinstance(row["account"], str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,30}", row["account"]), "account needs a simple synthetic name")
        require(row["kind"] in ("auth-failure", "auth-success", "process-alert"), "unsupported alert kind")
        time = moment(row["time"])
        if row["id"] in unique:
            require(unique[row["id"]] == row, "same alert ID has conflicting evidence")
        else:
            unique[row["id"]], times[row["id"]] = row, time
    groups = {}
    for row in unique.values():
        groups.setdefault((row["host"], row["account"]), []).append(row)
    decisions = {}
    observations = [f'Deliveries={len(data["alerts"])}; unique alerts={len(unique)}; repeated deliveries={len(data["alerts"]) - len(unique)}.']
    for (host, account), rows in sorted(groups.items()):
        ordered = sorted(rows, key=lambda row: (times[row["id"]], row["id"]))
        sessions = []
        for row in ordered:
            if not sessions or (times[row["id"]] - times[sessions[-1][0]["id"]]).total_seconds() > window:
                sessions.append([])
            sessions[-1].append(row)
        for index, session in enumerate(sessions, 1):
            key = f"{host}/{account}/{index}"
            failures = [times[row["id"]] for row in session if row["kind"] == "auth-failure"]
            successes = [times[row["id"]] for row in session if row["kind"] == "auth-success"]
            kinds = {row["kind"] for row in session}
            sequence = any(sum(failure < success for failure in failures) >= 3 for success in successes)
            result = "review-auth-sequence" if sequence else "review-mixed-signals" if "process-alert" in kinds and len(kinds) > 1 else "retain-context"
            decisions[key] = result
            observations.append(f'{key}: anchor={session[0]["time"]}; IDs={",".join(row["id"] for row in session)}; failures={len(failures)}; successes={len(successes)}; kinds={",".join(sorted(kinds))}.')
    return {"decisions": decisions, "observations": observations, "limitations": [
        "Deduplication uses alert ID and identical full content; different IDs are retained even when text or timestamps match.",
        "Sessions share exact host and account and span at most the window from their first alert, inclusively; this is a teaching rule, not a universal detection rule.",
        "Three earlier failure alerts followed by a success warrant review, as do authentication plus process signals. Alerts and review groups are not counts of confirmed incidents.",
        "Clock accuracy, sensor coverage, account ownership and authorised activity remain unverified; no service or endpoint was contacted."]}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
