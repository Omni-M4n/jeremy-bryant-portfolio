"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'incident-case'

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

LIMITS = ['A matching change record is a plausible innocent explanation, not proof of who acted or whether code was safe.', 'The four event kinds are simplified summaries. A DNS lookup and HTTP destination do not prove transferred content.', 'Exact time order assumes accurate UTC clocks. Missing kinds may be collection gaps rather than absent activity.', 'No real incident, endpoint, account, DNS server or website was contacted. Human review still chooses the response.']

def analyse(case):
    validate_case(case,LAB_ID); data=case["data"]
    exact(data,["change","events"]); require(not case["artifacts"],"case data is the evidence source")
    change=data["change"]
    exact(change,["id","host","account","start","end","process","destination","approved"])
    name(change["id"]); host(change["host"]); name(change["account"])
    name(change["process"]); host(change["destination"]); flag(change["approved"])
    start,end=moment(change["start"]),moment(change["end"]); require(start<end,"invalid change window")
    events=data["events"]; require(isinstance(events,list) and 1<=len(events)<=30,"supply 1-30 events")
    ids=set(); kinds=set(); outside=[]; ordered=[]
    for event in events:
        exact(event,["id","time","kind","host","account","value"])
        name(event["id"]); require(event["id"] not in ids and event["id"]!=change["id"],"evidence IDs must be unique")
        ids.add(event["id"]); host(event["host"]); name(event["account"])
        stamp=moment(event["time"]); kind=event["kind"]
        require(kind in ("login","process","dns","http"),"unsupported evidence kind")
        if kind=="login": require(event["value"]=="success","this case supports successful login records only")
        elif kind=="process": name(event["value"])
        else: host(event["value"])
        match=event["host"]==change["host"] and event["account"]==change["account"] and start<=stamp<end
        if kind=="process": match=match and event["value"]==change["process"]
        if kind in ("dns","http"): match=match and event["value"]==change["destination"]
        if not match: outside.append(event["id"])
        kinds.add(kind); ordered.append((stamp,event["id"]))
    missing=sorted({"login","process","dns","http"}-kinds)
    if outside: hypothesis="review-outside-change"
    elif not change["approved"]: hypothesis="request-owner-check"
    elif missing: hypothesis="request-missing-source"
    else: hypothesis="consistent-with-change"
    order=",".join(key for _,key in sorted(ordered))
    return dict(decisions={"working-hypothesis":hypothesis,"coverage":"four-kinds-present" if not missing else "kinds-missing","timeline":order},observations=[
        f"Change={change['id']}; approved={str(change['approved']).lower()}; matching scope uses host, account, time, process and destination.",
        f"Ordered IDs={order}; outside change={','.join(sorted(outside)) or 'none'}; missing kinds={','.join(missing) or 'none'}."],limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
