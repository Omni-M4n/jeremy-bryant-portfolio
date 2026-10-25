"""Compare dummy encodings/digests and reason about supplied recovery evidence."""
import base64
import binascii
import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "encryption-key-recovery"
LIMITS = [
    "Base64 and SHA-256 are computed over dummy UTF-8 bytes; neither operation encrypts data or authenticates its origin.",
    "Encrypted-file and decryption receipts are fictional supplied evidence; only the supplied dummy restored text is hashed, with no encryption or decryption performed.",
    "Recovery uses one exact required key per object, with no alternate plaintext, cached key, wrapping layer or replica path; unavailable means unavailable in this inventory.",
    "A supplied successful comparison is limited to that restore attempt and trusted comparison baseline, not future recoverability or proof of confidentiality.",
]


def fields(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected.split()),
            f"{label}: missing or unsupported fields")


def rows(value, label):
    require(isinstance(value, list) and 1 <= len(value) <= 20,
            f"{label}: expected 1-20 rows")
    seen = set()
    for row in value:
        require(isinstance(row, dict) and isinstance(row.get("id"), str) and
                re.fullmatch(r"[a-z][a-z0-9-]{0,39}", row["id"]), f"{label}: invalid ID")
        require(row["id"] not in seen, f"{label}: duplicate ID")
        seen.add(row["id"])
    return value


def evidence_ref(value):
    require(isinstance(value, str) and 0 < len(value.strip()) <= 160, "evidence reference required")


def sample_result(row):
    fields(row, "id method goal source_text supplied_output evidence_ref", "sample")
    require(row["method"] in ("base64", "sha256"), "unsupported sample method")
    require(row["goal"] in ("transport", "change-detection", "confidentiality"), "unsupported goal")
    require(isinstance(row["source_text"], str) and len(row["source_text"].encode("utf-8")) <= 1024,
            "source_text must be at most 1024 UTF-8 bytes")
    require(isinstance(row["supplied_output"], str) and len(row["supplied_output"]) <= 1400,
            "supplied_output must be bounded text")
    evidence_ref(row["evidence_ref"])
    raw = row["source_text"].encode("utf-8")
    if row["method"] == "base64":
        try:
            decoded = base64.b64decode(row["supplied_output"], validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError("supplied Base64 must use the standard padded alphabet") from error
        require(base64.b64encode(decoded).decode("ascii") == row["supplied_output"],
                "supplied Base64 must be canonical")
        matches = decoded == raw
        suitable = row["goal"] == "transport"
        detail = f"decoded_hex={decoded.hex()}; source_hex={raw.hex()}"
    else:
        require(re.fullmatch(r"[0-9a-f]{64}", row["supplied_output"]),
                "SHA-256 must be 64 lowercase hexadecimal characters")
        digest = hashlib.sha256(raw).hexdigest()
        matches = digest == row["supplied_output"]
        suitable = row["goal"] == "change-detection"
        detail = f"computed_sha256={digest}; supplied_sha256={row['supplied_output']}"
    result = f"{row['method']}:{'matches' if matches else 'differs'}:{'fits-stated-goal' if suitable else 'wrong-purpose'}"
    observation = (f"{row['id']}: {len(raw)} UTF-8 bytes; {detail}; goal={row['goal']}; "
                   f"evidence={row['evidence_ref']}.")
    return result, observation


def recovery_result(row, keys):
    fields(row, "id key_id ciphertext_present ciphertext_check attempt baseline_sha256 restored_text evidence_ref", "backup")
    require(isinstance(row["key_id"], str) and row["key_id"] in keys, "unknown required key")
    require(type(row["ciphertext_present"]) is bool, "ciphertext_present must be boolean")
    require(row["ciphertext_check"] in ("matches", "differs", "not-checked"), "unsupported ciphertext check")
    require(row["attempt"] in ("not-run", "success", "failure"), "unsupported attempt")
    require(isinstance(row["baseline_sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", row["baseline_sha256"]),
            "baseline SHA-256 must be 64 lowercase hexadecimal characters")
    require(row["restored_text"] is None or (isinstance(row["restored_text"], str) and
            len(row["restored_text"].encode("utf-8")) <= 1024), "restored_text must be null or bounded UTF-8 text")
    evidence_ref(row["evidence_ref"])
    key = keys[row["key_id"]]
    if not row["ciphertext_present"]:
        require(row["ciphertext_check"] == "not-checked" and row["attempt"] == "not-run",
                "absent ciphertext cannot have a check or decryption attempt")
    if row["attempt"] != "not-run":
        require(row["ciphertext_present"] and key["state"] == "available" and key["access"] == "allowed",
                "attempt requires present ciphertext and an available authorised key")
    if row["attempt"] != "success":
        require(row["restored_text"] is None, "only successful attempts can supply restored text")
    restored_check = "not-checked"
    if row["restored_text"] is not None:
        restored_digest = hashlib.sha256(row["restored_text"].encode("utf-8")).hexdigest()
        restored_check = "matches" if restored_digest == row["baseline_sha256"] else "differs"
    # the first blocking condition is reported, but the observation preserves every dependency
    if not row["ciphertext_present"]:
        result = "ciphertext-missing"
    elif row["ciphertext_check"] == "differs":
        result = "ciphertext-changed-investigate"
    elif key["state"] == "lost":
        result = "required-key-unavailable"
    elif key["state"] == "disabled":
        result = "key-disabled-review-recovery"
    elif key["state"] == "unknown":
        result = "key-state-unknown"
    elif key["access"] != "allowed":
        result = "key-access-denied" if key["access"] == "denied" else "key-access-unknown"
    elif row["attempt"] == "not-run":
        result = "restore-unproven"
    elif row["attempt"] == "failure":
        result = "decrypt-failed-investigate"
    elif restored_check == "differs":
        result = "restored-content-mismatch"
    elif restored_check == "not-checked":
        result = "restored-content-unverified"
    else:
        result = "restore-verified-in-supplied-evidence"
    observation = (f"{row['id']}: ciphertext_present={str(row['ciphertext_present']).lower()}; "
                   f"ciphertext_check={row['ciphertext_check']}; required_key={row['key_id']}; "
                   f"key_state={key['state']}; access={key['access']}; attempt={row['attempt']}; "
                   f"restored_check={restored_check}; evidence={row['evidence_ref']}; "
                   f"key_evidence={key['evidence_ref']}.")
    return result, observation


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "samples keys backups", "data")
    keys = {}
    for key in rows(data["keys"], "keys"):
        fields(key, "id state access evidence_ref", "key")
        require(key["state"] in ("available", "lost", "disabled", "unknown"), "unsupported key state")
        require(key["access"] in ("allowed", "denied", "unknown"), "unsupported key access")
        evidence_ref(key["evidence_ref"])
        keys[key["id"]] = key
    decisions, observations = {}, []
    for row in rows(data["samples"], "samples"):
        result, observation = sample_result(row)
        decisions[row["id"]] = result
        observations.append(observation)
    for row in rows(data["backups"], "backups"):
        require(row["id"] not in decisions, "sample and backup IDs must be distinct")
        result, observation = recovery_result(row, keys)
        decisions[row["id"]] = result
        observations.append(observation)
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
