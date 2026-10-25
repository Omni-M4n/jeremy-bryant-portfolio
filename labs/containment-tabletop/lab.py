"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'containment-tabletop'

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

LIMITS = ['This is a written non-emergency exercise. It executes no account restriction, host isolation, backup restore or service change.', 'The emergency card means use an authorised emergency path; evidence collection must not create unsafe delay.', 'Restored bytes alone do not prove that dependencies, secure access, business work or queued tasks are ready.', 'The small gate model checks supplied claims and references. People must verify the evidence and approve any real action.']

def analyse(case):
    validate_case(case,LAB_ID); data=case["data"]
    exact(data,["incident","service","dependencies","fallback","roles","checks","evidence"])
    require(not case["artifacts"],"case data contains all action cards")
    evidence=data["evidence"]
    require(isinstance(evidence,dict) and 1<=len(evidence)<=30,"provide a bounded evidence register")
    for key,text in evidence.items():
        name(key); require(isinstance(text,str) and 1<=len(text)<=700,"evidence note must be bounded text")
    def evidence_id(value):
        name(value); require(value in evidence,"missing evidence reference")
    incident=data["incident"]
    exact(incident,["scope","active","urgent","preserved","authority","evidence_id"])
    require(incident["scope"] in ("account","host","uncertain"),"unsupported scope")
    for key in ("active","urgent","preserved"): flag(incident[key])
    require(incident["authority"] in ("approved","pending"),"unsupported authority status")
    require(not incident["urgent"] or incident["active"],"urgent requires active evidence in this model")
    evidence_id(incident["evidence_id"])
    service=data["service"]
    exact(service,["name","available","bytes_restored","evidence_id"])
    name(service["name"]); flag(service["available"]); flag(service["bytes_restored"]); evidence_id(service["evidence_id"])
    roles=data["roles"]; exact(roles,["incident_lead","service_owner"])
    for value in roles.values(): name(value)
    dependencies=data["dependencies"]
    require(isinstance(dependencies,list) and 1<=len(dependencies)<=8,"name 1-8 dependencies")
    names=set()
    for dep in dependencies:
        exact(dep,["name","available","owner","evidence_id"])
        name(dep["name"]); name(dep["owner"]); flag(dep["available"]); evidence_id(dep["evidence_id"])
        require(dep["name"] not in names,"duplicate dependency"); names.add(dep["name"])
    fallback=data["fallback"]
    exact(fallback,["ready","owner","capacity_per_hour","need_per_hour","evidence_id"])
    flag(fallback["ready"]); name(fallback["owner"]); evidence_id(fallback["evidence_id"])
    number(fallback["capacity_per_hour"],0,100); number(fallback["need_per_hour"],1,100)
    checks=data["checks"]; exact(checks,["security","workflow","queue","owner_release"])
    for check in checks.values():
        exact(check,["passed","evidence_id"]); flag(check["passed"]); evidence_id(check["evidence_id"])
    if not incident["active"]: action="monitor-and-check"
    elif incident["urgent"]: action="emergency-escalation"
    elif incident["authority"]=="pending": action="request-authority"
    elif incident["scope"]=="uncertain": action="clarify-scope"
    elif not incident["preserved"]: action="preserve-evidence"
    else: action="account-card" if incident["scope"]=="account" else "host-card"
    if service["available"]: continuity="keep-service-under-review"
    elif not fallback["ready"]: continuity="prepare-fallback"
    elif fallback["capacity_per_hour"]<fallback["need_per_hour"]: continuity="escalate-capacity"
    else: continuity="use-manual-fallback"
    blocked=[d["name"] for d in dependencies if not d["available"]]
    failed=[key for key,value in checks.items() if not value["passed"]]
    ready=service["available"] and service["bytes_restored"] and not blocked and not failed and not incident["active"]
    resume="resume-with-owner-release" if ready else "hold-service-resumption"
    gap=max(0,fallback["need_per_hour"]-fallback["capacity_per_hour"]) if fallback["ready"] else fallback["need_per_hour"]
    return dict(decisions={"action-card":action,"continuity":continuity,"resumption":resume},observations=[
        f"Incident lead={roles['incident_lead']}; service owner={roles['service_owner']}; incident evidence={incident['evidence_id']}; service evidence={service['evidence_id']}.",
        f"Unavailable dependencies={','.join(blocked) or 'none'}; unpassed checks={','.join(failed) or 'none'}.",
        f"Fallback owner={fallback['owner']}; ready={str(fallback['ready']).lower()}; capacity={fallback['capacity_per_hour']}/hour; demand={fallback['need_per_hour']}/hour; uncovered demand={gap}/hour; evidence={fallback['evidence_id']}."],limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
