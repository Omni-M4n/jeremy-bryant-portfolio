"""Small AWS identity-policy subset, never a provider policy validator."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAB_ID = "iam-explicit-deny"
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require

ACTIONS = {"s3:GetObject", "s3:PutObject", "s3:DeleteObject"}
LIMITS = ["Only identity statements for three S3 object actions are modelled; conditions, resource policies, boundaries, session policies and organization policies are excluded.", "This offline subset cannot approve an AWS deployment."]


def keys(value, wanted):
    require(isinstance(value, dict) and set(value) == set(wanted), "missing or unsupported fields")


def resource(value, pattern=False):
    require(isinstance(value, str) and re.fullmatch(r"arn:aws:s3:::practice-[a-z0-9-]+/[a-zA-Z0-9/_.*-]+", value), "use a fictional practice bucket object ARN")
    require("*" not in value or (pattern and value.count("*") == 1 and value.endswith("*")), "only one terminal resource wildcard is supported")
    return value


def matches(pattern, value):
    return value.startswith(pattern[:-1]) if pattern.endswith("*") else pattern == value


def analyse(case):
    data = case["data"]
    keys(data, ["statements", "requests"])
    require(isinstance(data["statements"], list) and len(data["statements"]) <= 20, "statements must be a list of at most 20")
    require(isinstance(data["requests"], list) and 0 < len(data["requests"]) <= 30, "supply 1-30 requests")
    seen = set()
    for statement in data["statements"]:
        keys(statement, ["id", "effect", "actions", "resource"])
        require(isinstance(statement["id"], str) and re.fullmatch(r"s[0-9]+", statement["id"]) and statement["id"] not in seen, "unique neutral statement IDs required")
        seen.add(statement["id"])
        require(statement["effect"] in ("Allow", "Deny"), "effect must be Allow or Deny")
        actions = statement["actions"]
        require(isinstance(actions, list) and actions and all(isinstance(a, str) and a in ACTIONS for a in actions) and len(set(actions)) == len(actions), "unsupported or duplicate action")
        resource(statement["resource"], True)
    decisions, observations, seen = {}, [], set()
    for row in data["requests"]:
        keys(row, ["id", "action", "resource"])
        require(isinstance(row["id"], str) and re.fullmatch(r"q[0-9]+", row["id"]) and row["id"] not in seen, "unique neutral request IDs required")
        seen.add(row["id"])
        require(isinstance(row["action"], str) and row["action"] in ACTIONS, "unsupported request action")
        resource(row["resource"])
        hit = [s for s in data["statements"] if row["action"] in s["actions"] and matches(s["resource"], row["resource"])]
        effects = {s["effect"] for s in hit}
        outcome = "explicit-deny" if "Deny" in effects else "allow" if "Allow" in effects else "implicit-deny"
        decisions[row["id"]] = outcome
        observations.append(f"{row['id']}: matching statements={','.join(s['id'] for s in hit) or 'none'}; result={outcome}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
