"""Audit fictional MFA challenge records after a hands-on local exercise."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAB_ID = "mfa-hands-on"
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require

LIMITS = ["This worksheet reviews supplied evidence; it does not execute enrolment or prove possession of two separate devices.", "The local training service uses dummy secrets and a chosen clock. It is not a deployable authenticator or a phishing-resistant login."]


def analyse(case):
    data = case["data"]
    require(isinstance(data, dict) and set(data) == {"records"}, "only records are supported")
    require(isinstance(data["records"], list) and 0 < len(data["records"]) <= 30, "supply 1-30 records")
    decisions, observations = {}, []
    for row in data["records"]:
        require(isinstance(row, dict) and set(row) == {"id", "operation", "password_ok", "enrolled", "proof_matches", "proof_used", "observed"}, "missing or unsupported record fields")
        require(isinstance(row["id"], str) and re.fullmatch(r"q[0-9]+", row["id"]) and row["id"] not in decisions, "unique neutral IDs required")
        require(row["operation"] in ("confirm", "challenge", "recover"), "unknown operation")
        for field in ("password_ok", "enrolled", "proof_matches", "proof_used"):
            require(type(row[field]) is bool, "flags must be boolean")
        require(row["observed"] in ("accept", "reject"), "observed must be accept or reject")
        allowed = row["password_ok"] and row["proof_matches"] and not row["proof_used"]
        if row["operation"] == "confirm":
            allowed = allowed and not row["enrolled"]
        else:
            allowed = allowed and row["enrolled"]
        expected = "accept" if allowed else "reject"
        decisions[row["id"]] = "matches-model" if expected == row["observed"] else "investigate-mismatch"
        observations.append(f"{row['id']}: operation={row['operation']}; expected={expected}; observed={row['observed']}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
