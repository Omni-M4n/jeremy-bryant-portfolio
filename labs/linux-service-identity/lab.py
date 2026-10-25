"""Bounded fictional evidence; no host commands are executed."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = "linux-service-identity"

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def label(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", value), "use a short plain label")

def rows(value):
    require(isinstance(value, list) and 1 <= len(value) <= 30, "provide 1-30 records")

def command(row, with_id=False):
    fields = ["run_as", "executable", "arguments"] + (["id"] if with_id else [])
    exact(row, fields)
    label(row["run_as"])
    path = row["executable"]
    require(isinstance(path, str) and re.fullmatch(r"/(?:[a-z0-9_-]+/)*[a-z0-9_-]+", path), "plain absolute executable required")
    args = row["arguments"]
    require(isinstance(args, list) and len(args) <= 8 and all(isinstance(x, str) and re.fullmatch(r"[a-zA-Z0-9_./=-]+", x) for x in args), "plain literal arguments required")
    if with_id:
        label(row["id"])
    return (row["run_as"], path, tuple(args))


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["service", "rules", "requests"])
    service = data["service"]
    exact(service, ["id", "configured_user", "observed_user", "state"])
    label(service["id"])
    for field in ("configured_user", "observed_user"):
        require(isinstance(service[field], str), "identity must be text")
        if service[field]: label(service[field])
    require(service["state"] in ("active", "inactive"), "unsupported state")
    require(bool(service["observed_user"]) == (service["state"] == "active"), "active requires observed identity; inactive requires none")
    configured = service["configured_user"] or "root"
    if service["state"] == "inactive":
        result = "not-running"
    else:
        result = "identity-matches" if configured == service["observed_user"] else "identity-mismatch"
    decisions = {service["id"]: result}
    observations = [f"{service['id']}: configured={configured}; observed={service['observed_user'] or 'none'}; state={service['state']}."]
    require(isinstance(data["rules"], list) and len(data["rules"]) <= 30, "bounded rule list required")
    rules = [command(row) for row in data["rules"]]
    require(len(set(rules)) == len(rules), "duplicate rule")
    rows(data["requests"])
    for request in data["requests"]:
        key = command(request, True)
        identity = request["id"]
        require(identity not in decisions, "duplicate ID")
        decisions[identity] = "allowed-by-listed-rule" if key in rules else "not-listed"
        observations.append(f"{identity}: run-as={key[0]}; command={' '.join([key[1], *key[2]])}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}

LIMITS = ['Only a system service and exact listed sudo command tuples are modelled; no shell, wildcard, alias or inherited sudo policy is inferred.', 'A matching identity does not establish safe service code, file permissions or a complete privilege boundary.']

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
