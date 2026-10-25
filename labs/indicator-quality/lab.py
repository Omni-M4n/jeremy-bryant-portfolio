"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'indicator-quality'

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

from datetime import timedelta
import ipaddress
LIMITS = ['All indicators and reports are fictional. No lookup, reputation check, block or external submission is performed.', 'A supplied confidence number is the report author opinion, not a measured probability or proof.', 'A repeated report is not independent corroboration. A shared service can serve unrelated users.', 'The seven-day review rule and 70 threshold are local teaching choices, not STIX requirements. This is not a STIX implementation.']

def indicator(value, kind):
    if kind=="domain": host(value)
    else:
        require(kind=="ipv4","indicator type must be domain or ipv4")
        require(isinstance(value,str),"address must be text")
        ip=ipaddress.IPv4Address(value)
        require(any(ip in ipaddress.IPv4Network(net) for net in ("192.0.2.0/24","198.51.100.0/24","203.0.113.0/24")),"use a reserved documentation address")

def analyse(case):
    validate_case(case,LAB_ID); data=case["data"]
    exact(data,["as_of","records"]); require(not case["artifacts"],"case data is the report register")
    now=moment(data["as_of"]); rows=data["records"]
    require(isinstance(rows,list) and 1<=len(rows)<=30,"provide 1-30 indicator records")
    ids=set(); decisions={}; observations=[]
    for row in rows:
        exact(row,["id","value","type","source","confidence","observed_at","reported_at","valid_until","scope","contradicted","evidence_id"])
        key=row["id"]; name(key); name(row["evidence_id"])
        require(key not in ids,"duplicate register ID"); ids.add(key)
        indicator(row["value"],row["type"])
        require(row["source"] in ("direct","copied"),"unsupported provenance")
        if row["confidence"] is not None: number(row["confidence"],0,100)
        require(row["scope"] in ("single-host","shared-service"),"unsupported scope")
        flag(row["contradicted"])
        observed,reported,expiry=(moment(row[k]) for k in ("observed_at","reported_at","valid_until"))
        require(observed<=reported<=now and observed<expiry,"contradictory report dates")
        if now>=expiry: action="review-expiry"
        elif row["contradicted"]: action="resolve-conflict"
        elif row["source"]=="copied" or row["confidence"] is None or row["confidence"]<70: action="seek-origin"
        elif row["scope"]=="shared-service": action="narrow-scope"
        else: action="context-only-use"
        review=now
        if action=="context-only-use":
            # Add seven days only when that date is known to fit before expiry.
            review=expiry if expiry-now<=timedelta(days=7) else now+timedelta(days=7)
        review_text=review.isoformat(timespec="seconds").replace("+00:00", "Z")
        decisions[key]=action
        confidence="unspecified" if row["confidence"] is None else str(row["confidence"])
        observations.append(f"{key}: report={row['evidence_id']}; source={row['source']}; stated confidence={confidence}; scope={row['scope']}; review={review_text}.")
    return dict(decisions=decisions,observations=observations,limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
