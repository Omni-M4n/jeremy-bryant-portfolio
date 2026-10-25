"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'python-log-helper'

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

import json
from foundation_runtime import unique_object
LIMITS = ['The helper counts unique valid failure records in a half-open UTC window; it makes no incident decision.', 'Malformed lines are retained by line number; skipped lines can change the conclusion.', 'No network, host log or live account is read. A successful run does not show script mastery.']

def count_lines(raw, start, end):
    first,last=moment(start),moment(end)
    require(first<last,"window start must precede end")
    require(isinstance(raw,str) and len(raw.encode("utf-8"))<=100000,"bounded text required")
    lines=raw.splitlines()
    require(1<=len(lines)<=100,"provide 1-100 physical lines")
    states,seen,counts,rejected={}, {}, {}, []
    for index,line in enumerate(lines,1):
        key=f"line-{index}"
        try:
            row=json.loads(line,object_pairs_hook=unique_object,
                           parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonstandard number")))
            exact(row,["id","time","account","outcome"])
            name(row["id"]); name(row["account"])
            stamp=moment(row["time"])
            require(row["outcome"] in ("success","failure"),"unsupported outcome")
        except (ValueError,TypeError) as error:
            states[key]="reject"
            rejected.append(dict(line=index,reason=str(error),text=line))
            continue
        require(row["id"] not in seen or seen[row["id"]]==row,"conflicting event ID; stop counting")
        if row["id"] in seen:
            states[key]="repeat"; continue
        seen[row["id"]]=row
        if not first<=stamp<last: states[key]="outside"
        elif row["outcome"]=="success": states[key]="other-outcome"
        else:
            states[key]="count"
            counts[row["account"]]=counts.get(row["account"],0)+1
    return states,dict(sorted(counts.items())),rejected

def analyse(case):
    validate_case(case,LAB_ID)
    exact(case["data"],["start","end"]); exact(case["artifacts"],["events.jsonl"])
    states,counts,rejected=count_lines(case["artifacts"]["events.jsonl"],**case["data"])
    summary=",".join(f"{key}:{value}" for key,value in counts.items()) or "none"
    return dict(decisions=states, observations=[f"Lines={len(states)}; counted failures={sum(counts.values())}; rejected={len(rejected)}.",f"Counts by account={summary}."],limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
