"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'log-ingestion'

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def name(value):
    import re
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", value), "use a short fictional ID")

def number(value, low=0, high=10000):
    require(type(value) is int and low <= value <= high, "integer outside the lesson range")

def flag(value):
    require(type(value) is bool, "true or false required")

def moment(value):
    from datetime import datetime
    import re
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value), "use a UTC timestamp with seconds and Z")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def host(value):
    import re
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9-]+\.test", value), "use a fictional .test host")

import csv
import io
import json
import re
from datetime import datetime, timezone
from foundation_runtime import unique_object

LIMITS = ['Rows describe fictional login records, not confirmed incidents.', 'UTC conversion needs an explicit offset; clock accuracy remains unverified.', 'A rejected row is retained as evidence and is not evidence of a safe event.']

def normalise(row):
    exact(row, ["id", "time", "account", "outcome"])
    name(row["id"])
    name(row["account"])
    require(row["outcome"] in ("success", "failure"), "unsupported outcome")
    value = row["time"]
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-5][0-9])", value), "timestamp needs seconds and a valid offset")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(abs(stamp.utcoffset().total_seconds()) <= 14 * 3600, "offset outside lesson range")
    try:
        utc = stamp.astimezone(timezone.utc)
    except OverflowError as error:
        raise ValueError("UTC time is outside years 0001-9999") from error
    return dict(id=row["id"], time=utc.isoformat(timespec="seconds").replace("+00:00", "Z"), account=row["account"], outcome=row["outcome"])

def parse_records(raw, format_name):
    require(isinstance(raw, str) and len(raw.encode("utf-8")) <= 100000, "source must be bounded text")
    require(format_name in ("csv", "json"), "format must be csv or json")
    if format_name == "csv":
        reader = csv.DictReader(io.StringIO(raw, newline=""), strict=True)
        require(reader.fieldnames == ["event_id", "timestamp", "user", "status"], "CSV header does not match the field map")
        try:
            rows = list(reader)
        except csv.Error as error:
            raise ValueError("invalid CSV structure") from error
        mapped = []
        for row in rows:
            if set(row) == {"event_id", "timestamp", "user", "status"} and all(v is not None for v in row.values()):
                mapped.append(dict(zip(["id", "time", "account", "outcome"], [row[k] for k in reader.fieldnames])))
            else:
                mapped.append(row)
    else:
        try:
            mapped = json.loads(raw, object_pairs_hook=unique_object,
                                parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonstandard JSON number")))
        except json.JSONDecodeError as error:
            raise ValueError("invalid JSON structure") from error
    require(isinstance(mapped, list) and 1 <= len(mapped) <= 100, "supply 1-100 records")
    accepted, seen, states, rejected = [], {}, {}, []
    for index, row in enumerate(mapped, 1):
        key = f"row-{index}"
        try:
            record = normalise(row)
        except (ValueError, TypeError) as error:
            states[key] = "reject"
            rejected.append(dict(row=index, reason=str(error), raw=row))
            continue
        if record["id"] in seen:
            require(seen[record["id"]] == record, "conflicting content under one event ID; stop import")
            states[key] = "repeat"
        else:
            states[key] = "import"
            seen[record["id"]] = record
            accepted.append(record)
    return accepted, states, rejected

def analyse(case):
    validate_case(case, LAB_ID)
    exact(case["data"], ["format"])
    exact(case["artifacts"], ["records.txt"])
    records, states, rejects = parse_records(case["artifacts"]["records.txt"], case["data"]["format"])
    observations = [f"Source rows={len(states)}; imported={len(records)}; repeats={list(states.values()).count('repeat')}; rejected={len(rejects)}."]
    observations += [f"{r['id']}: {r['time']} {r['account']} {r['outcome']}." for r in records]
    return dict(decisions=states, observations=observations, limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
