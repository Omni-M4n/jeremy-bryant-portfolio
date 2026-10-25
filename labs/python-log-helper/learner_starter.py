"""Copy into run/attempt-01/my-helper.py and finish the two marked functions.
The supplied scaffold validates a tiny synthetic JSON-lines file. No network use.
"""
import json
from datetime import datetime
from pathlib import Path
import re
import sys

START = "2026-01-15T00:01:00Z"
END = "2026-01-15T00:03:00Z"

def include(row):
    # TODO: include only failures with START <= time < END.
    raise NotImplementedError("Finish include before running the file task")

def add(counts, account):
    # TODO: increase this account's count by one, starting from zero.
    raise NotImplementedError("Finish add before running the file task")

def unique_keys(pairs):
    row = {}
    for key, value in pairs:
        if key in row:
            raise ValueError("duplicate JSON key")
        row[key] = value
    return row

def read_row(text):
    row = json.loads(text, object_pairs_hook=unique_keys)
    if not isinstance(row, dict) or set(row) != {"id", "time", "account", "outcome"}:
        raise ValueError("record fields do not match")
    for key in ("id", "account"):
        if not isinstance(row[key], str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", row[key]):
            raise ValueError("invalid ID or account")
    if not isinstance(row["time"], str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", row["time"]):
        raise ValueError("use UTC time with seconds")
    datetime.strptime(row["time"], "%Y-%m-%dT%H:%M:%SZ")
    if row["outcome"] not in ("success", "failure"):
        raise ValueError("unsupported outcome")
    return row

def process(path):
    if path.stat().st_size > 100000:
        raise ValueError("file exceeds the lesson limit")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not 1 <= len(lines) <= 100:
        raise ValueError("use 1-100 lines")
    counts, seen, rejected, repeats = {}, {}, [], 0
    for line_number, text in enumerate(lines, 1):
        try:
            row = read_row(text)
        except (ValueError, TypeError):
            rejected.append(line_number)
            continue
        if row["id"] in seen:
            if row != seen[row["id"]]:
                raise ValueError("conflicting event ID")
            repeats += 1
            continue
        seen[row["id"]] = row
        if include(row):
            add(counts, row["account"])
    return dict(counts=counts, rejected_lines=rejected, repeats=repeats)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python my-helper.py path/to/events.jsonl")
    try:
        print(json.dumps(process(Path(sys.argv[1])), indent=2))
    except (ValueError, OSError, NotImplementedError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        raise SystemExit(2)
