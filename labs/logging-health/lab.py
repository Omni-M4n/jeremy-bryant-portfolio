"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'logging-health'

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

LIMITS = ['Coverage is measured only against the supplied source IDs at the stated cutoff, not all activity on a host.', 'A heartbeat proves only that its small signal was received; it does not prove event collection is complete.', 'Delays may reflect transport, queueing or clock problems. This model assumes the recorded clocks are correct.', 'A complete empty source list supports zero listed events in this interval, not a claim that nothing happened anywhere.']

def analyse(case):
    validate_case(case,LAB_ID); data=case["data"]
    exact(data,["observed_at","delay_budget_seconds","intervals"])
    require(not case["artifacts"],"case data is the only record source")
    cutoff=moment(data["observed_at"]); budget=data["delay_budget_seconds"]; number(budget,0,3600)
    rows=data["intervals"]
    require(isinstance(rows,list) and 1<=len(rows)<=20,"provide 1-20 intervals")
    ids=set(); all_events=set(); intervals=[]; decisions={}; observations=[]
    for row in rows:
        exact(row,["id","start","end","source_ids","received","heartbeat"])
        key=row["id"]; name(key); require(key not in ids,"duplicate interval ID"); ids.add(key)
        start,end=moment(row["start"]),moment(row["end"])
        require(start<end<=cutoff,"interval must end by cutoff")
        require(all(end<=a or start>=b for a,b in intervals),"intervals must not overlap")
        intervals.append((start,end)); flag(row["heartbeat"])
        source=row["source_ids"]
        require(source is None or (isinstance(source,list) and len(source)<=100),"source IDs must be a list or null")
        if source is not None:
            for value in source: name(value)
            require(len(source)==len(set(source)),"duplicate source ID")
        require(isinstance(row["received"],list) and len(row["received"])<=100,"received must be a bounded list")
        received=set(); delays=[]
        for item in row["received"]:
            exact(item,["id","event_at","ingested_at"]); name(item["id"])
            require(item["id"] not in received and item["id"] not in all_events,"duplicate delivery ID")
            event,ingested=moment(item["event_at"]),moment(item["ingested_at"])
            require(start<=event<end and event<=ingested<=cutoff,"event or arrival outside its allowed time")
            require(source is None or item["id"] in source,"collector ID is absent from complete source list")
            received.add(item["id"]); delays.append(int((ingested-event).total_seconds()))
        interval_ids=set(source) if source is not None else received
        require(not interval_ids & all_events,"source event appears in two intervals")
        all_events.update(interval_ids)
        coverage="source-unverified" if source is None else "complete-at-cutoff" if len(received)==len(source) else "gap-at-cutoff"
        delivery="no-deliveries" if not delays else "late-delivery" if max(delays)>budget else "within-budget"
        decisions.update({key+"/coverage":coverage,key+"/delivery":delivery,key+"/heartbeat":"present" if row["heartbeat"] else "absent"})
        expected="unknown" if source is None else str(len(source))
        missing="unknown" if source is None else ",".join(sorted(set(source)-received)) or "none"
        lag=str(max(delays)) if delays else "none"
        observations.append(f"{key}: source={expected}; received={len(received)}; missing={missing}; maximum delay seconds={lag}; budget={budget}.")
    return dict(decisions=decisions,observations=observations,limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
