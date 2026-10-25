"""Trace fictional short-lived role sessions on a small integer clock."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAB_ID = "temporary-credentials"
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require

LIMITS = ["Times are fictional seconds. Revocation is a model rule applied at revoke_at to sessions issued strictly before it; provider propagation is excluded.", "An attributed human is a recorded issuer, not proof of who held a token. No real credentials or AWS calls are used."]


def keys(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")


def number(value):
    require(type(value) is int and 0 <= value <= 100000, "time must be an integer from 0 to 100000")


def rows(value, fields):
    require(isinstance(value, list) and 0 < len(value) <= 30, "supply 1-30 records")
    result = {}
    for row in value:
        keys(row, fields)
        ident = row["id"]
        require(isinstance(ident, str) and re.fullmatch(r"[a-z][a-z0-9-]*", ident) and ident not in result, "unique IDs required")
        result[ident] = row
    return result


def analyse(case):
    data = case["data"]
    keys(data, ["humans", "roles", "sessions", "requests"])
    humans = rows(data["humans"], ["id", "disabled_at"])
    for h in humans.values():
        if h["disabled_at"] is not None:
            number(h["disabled_at"])
    roles = rows(data["roles"], ["id", "trusted_humans", "actions", "revoke_at"])
    for role in roles.values():
        require(isinstance(role["trusted_humans"], list) and role["trusted_humans"] and all(isinstance(h, str) and h in humans for h in role["trusted_humans"]) and len(set(role["trusted_humans"])) == len(role["trusted_humans"]), "invalid trusted humans")
        require(isinstance(role["actions"], list) and all(isinstance(a, str) and a in ("read", "write") for a in role["actions"]) and len(set(role["actions"])) == len(role["actions"]), "invalid role actions")
        if role["revoke_at"] is not None:
            number(role["revoke_at"])
    sessions = rows(data["sessions"], ["id", "human", "role", "issued", "expires"])
    for session in sessions.values():
        require(isinstance(session["human"], str) and session["human"] in humans and isinstance(session["role"], str) and session["role"] in roles, "unknown issuer or role")
        number(session["issued"])
        number(session["expires"])
        require(session["expires"] > session["issued"], "expiry must follow issue")
        require(session["human"] in roles[session["role"]]["trusted_humans"], "session issuer was not trusted")
        disabled = humans[session["human"]]["disabled_at"]
        require(disabled is None or session["issued"] < disabled, "a disabled human cannot issue a new session in this model")
    requests = rows(data["requests"], ["id", "session", "at", "action"])
    decisions, observations = {}, []
    for row in requests.values():
        require(isinstance(row["session"], str) and row["session"] in sessions, "unknown session")
        require(row["action"] in ("read", "write"), "unsupported action")
        number(row["at"])
        session = sessions[row["session"]]
        role = roles[session["role"]]
        cut = role["revoke_at"]
        if row["at"] < session["issued"]:
            verdict = "not-yet-issued"
        elif row["at"] >= session["expires"]:
            verdict = "expired"
        elif cut is not None and row["at"] >= cut and session["issued"] < cut:
            verdict = "revoked"
        elif row["action"] not in role["actions"]:
            verdict = "action-not-granted"
        else:
            verdict = "allowed-in-model"
        decisions[row["id"]] = verdict
        observations.append(f"{row['id']}: human={session['human']}; role={session['role']}; session={session['id']}; interval=[{session['issued']},{session['expires']}); at={row['at']}; result={verdict}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
