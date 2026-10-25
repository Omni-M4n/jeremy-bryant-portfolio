"""Bounded fictional evidence; no host commands are executed."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = "windows-acl"

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def label(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", value), "use a short plain label")

def rows(value):
    require(isinstance(value, list) and 1 <= len(value) <= 30, "provide 1-30 records")

def check_aces(entries, rights):
    require(isinstance(entries, list) and len(entries) <= 30, "bounded ACE list required; empty means empty DACL")
    ranks = []
    for ace in entries:
        exact(ace, ["trustee", "kind", "inherited", "rights"])
        label(ace["trustee"])
        require(ace["kind"] in ("allow", "deny") and type(ace["inherited"]) is bool, "bad ACE type")
        mask = ace["rights"]
        require(isinstance(mask, list) and mask and all(isinstance(x, str) and x in rights for x in mask), "unsupported right")
        require(len(mask) == len(set(mask)), "duplicate right")
        ranks.append(2 * ace["inherited"] + (ace["kind"] == "allow"))
    require(ranks == sorted(ranks), "use canonical explicit-deny/allow then inherited-deny/allow order")


def grants(entries, token, right):
    # One right is requested, so the first matching entry settles this check.
    for ace in entries:
        if ace["trustee"] in token and right in ace["rights"]:
            return ace["kind"] == "allow"
    return False


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["token", "file_aces", "parent_aces", "requests"])
    rows(data["token"])
    for identity in data["token"]:
        label(identity)
    require(len(set(data["token"])) == len(data["token"]), "duplicate token identity")
    check_aces(data["file_aces"], {"read", "write", "delete"})
    check_aces(data["parent_aces"], {"delete-child"})
    rows(data["requests"])
    decisions, observations = {}, []
    for request in data["requests"]:
        exact(request, ["id", "right"])
        label(request["id"])
        require(request["id"] not in decisions, "duplicate request ID")
        right = request["right"]
        require(right in ("read", "write", "delete"), "unsupported request")
        file_grant = grants(data["file_aces"], data["token"], right)
        parent_grant = right == "delete" and grants(data["parent_aces"], data["token"], "delete-child")
        decisions[request["id"]] = "allow" if file_grant or parent_grant else "deny"
        observations.append(f"{request['id']}: {right}; file={str(file_grant).lower()}; parent-delete-route={str(parent_grant).lower()}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}

LIMITS = ['Only ordered allow/deny entries for enabled identities are modelled; no privileges, share permissions, integrity levels, owner rights or file locks.', 'Delete can use file delete OR parent delete-child. Read/write here mean one data right, not every right requested by a real application.']

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
