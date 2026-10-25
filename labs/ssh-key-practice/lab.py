"""Review fictional SSH observations; no keys or connections are created."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = "ssh-key-practice"

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def label(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", value), "plain short label required")

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["expected_user", "expected_key", "host_fingerprint_match", "recovery_console_tested", "trials"])
    label(data["expected_user"]); label(data["expected_key"])
    for field in ("host_fingerprint_match", "recovery_console_tested"):
        require(type(data[field]) is bool, "verification fields must be booleans")
    require(isinstance(data["trials"], list) and 1 <= len(data["trials"]) <= 20, "provide 1-20 trials")
    decisions = {"r1": "recovery-tested" if data["recovery_console_tested"] else "recovery-not-tested"}
    observations = [f"r1: console-tested={str(data['recovery_console_tested']).lower()}; host-fingerprint-match={str(data['host_fingerprint_match']).lower()}."]
    for trial in data["trials"]:
        exact(trial, ["id", "user", "key", "result", "method"])
        for field in ("id", "user", "key"): label(trial[field])
        require(trial["id"] not in decisions, "duplicate or reserved trial ID")
        require(trial["result"] in ("accepted", "auth-rejected", "transport-error", "not-run"), "unsupported result")
        require(trial["method"] in ("publickey", "password", "none"), "unsupported method")
        require((trial["result"] == "accepted") == (trial["method"] != "none"), "only an accepted login has an authentication method")
        intended = trial["user"] == data["expected_user"] and trial["key"] == data["expected_key"]
        if not data["host_fingerprint_match"]:
            outcome = "host-unverified-stop"
        elif trial["result"] == "not-run":
            outcome = "not-tested"
        elif trial["result"] == "transport-error":
            outcome = "transport-inconclusive"
        elif trial["result"] == "auth-rejected":
            outcome = "intended-key-rejected" if intended else "alternate-key-rejected"
        elif trial["method"] != "publickey":
            outcome = "other-method-accepted"
        else:
            outcome = "intended-key-accepted" if intended else "unexpected-key-access"
        decisions[trial["id"]] = outcome
        observations.append(f"{trial['id']}: user={trial['user']}; offered-key={trial['key']}; result={trial['result']}; method={trial['method']}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}

LIMITS = ['These are supplied authentication observations, not an SSH implementation or proof that a live server has this configuration.', 'A rejection caused by a network error proves no key boundary. Keep a tested console recovery route and verify the server fingerprint.']

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
