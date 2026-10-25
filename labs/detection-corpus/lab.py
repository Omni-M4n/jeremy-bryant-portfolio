"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'detection-corpus'

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

LIMITS = ['All events are harmless synthetic examples. Exercise labels are supplied teaching truth, not observed attacks.', 'Fractions describe only their named partition and denominator. This corpus cannot establish production accuracy.', 'Choose a candidate using tune rows before inspecting holdout rows. Reusing holdout to tune removes that independent check.', 'A count threshold is a simplified query, not a tested Snort rule or a complete detection system.']

def analyse(case):
    validate_case(case,LAB_ID); data=case["data"]
    exact(data,["thresholds","events"])
    require(not case["artifacts"],"case data is the only corpus")
    thresholds=data["thresholds"]
    require(isinstance(thresholds,list) and len(thresholds)==2,"compare two thresholds")
    for value in thresholds: number(value,1,20)
    require(thresholds[0]<thresholds[1],"thresholds must increase")
    events=data["events"]
    require(isinstance(events,list) and 2<=len(events)<=100,"provide 2-100 events")
    ids=set()
    for event in events:
        exact(event,["id","failures","label","partition"])
        name(event["id"]); number(event["failures"],0,100)
        require(event["id"] not in ids,"duplicate corpus ID")
        ids.add(event["id"])
        require(event["label"] in ("routine","exercise"),"unsupported truth label")
        require(event["partition"] in ("tune","holdout"),"unsupported partition")
    require({e["partition"] for e in events}=={"tune","holdout"},"both partitions are required")
    decisions,observations={},[]
    for threshold in thresholds:
        for partition in ("tune","holdout"):
            rows=[r for r in events if r["partition"]==partition]
            counts={"tp":0,"fp":0,"fn":0,"tn":0}
            for row in rows:
                alert=row["failures"]>=threshold
                positive=row["label"]=="exercise"
                key=("tp" if positive else "fp") if alert else ("fn" if positive else "tn")
                counts[key]+=1
            key=f"r{threshold}/{partition}"
            tp,fp,fn,tn=(counts[k] for k in ("tp","fp","fn","tn"))
            decisions[key]=f"tp={tp},fp={fp},fn={fn},tn={tn}"
            def fraction(n,d): return f"{n}/{d}" if d else "undefined(0/0)"
            observations.append(f"{key}: labelled={len(rows)}/{len(rows)}; alerts={tp+fp}/{len(rows)}; false alarms={fraction(fp,fp+tn)} routine; misses={fraction(fn,tp+fn)} exercise; false share of alerts={fraction(fp,tp+fp)}.")
    return dict(decisions=decisions,observations=observations,limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
