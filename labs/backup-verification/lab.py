"""Original fictional evidence analysis; no host inspection or network activity."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "backup-verification"

def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": unsupported or missing fields")

def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 300 and value.strip() == value, label + ": bounded nonempty text required")


import base64
import binascii
import hashlib
from datetime import datetime
import re

def moment(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value), "timestamp requires UTC seconds")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("invalid timestamp") from error

def measure_payloads(case):
    """Validate the case and measure embedded bytes without making decisions."""
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["recovery_time", "rpo_hours", "required_sha256", "backups"], "data")
    recovery = moment(data["recovery_time"])
    rpo = data["rpo_hours"]
    require(type(rpo) is int and 0 <= rpo <= 168, "RPO must be 0-168 whole hours")
    expected = data["required_sha256"]
    require(isinstance(expected, dict) and 1 <= len(expected) <= 20, "provide 1-20 required files")
    for name, digest in expected.items():
        require(isinstance(name, str) and re.fullmatch(r"[a-z][a-z0-9_-]*\.(?:txt|csv)", name), "use synthetic text-file basenames")
        require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), "invalid expected SHA-256")
    require(isinstance(data["backups"], list) and 1 <= len(data["backups"]) <= 20, "provide 1-20 backups")
    measurements, seen = [], set()
    for backup in data["backups"]:
        exact(backup, ["id", "captured_at", "retained_until", "payload_base64"], "backup")
        text(backup["id"], "backup ID")
        require(backup["id"] not in seen and backup["id"] != "recovery", "duplicate or reserved backup ID")
        seen.add(backup["id"])
        captured, until = moment(backup["captured_at"]), moment(backup["retained_until"])
        require(captured <= recovery and until > captured, "future capture or invalid retention interval")
        payload = backup["payload_base64"]
        require(isinstance(payload, dict) and set(payload) <= set(expected), "payload has unknown scope")
        for name, encoded in sorted(payload.items()):
            require(isinstance(encoded, str) and len(encoded) <= 16000, "bounded base64 text required")
            try:
                restored = base64.b64decode(encoded, validate=True)
            except (binascii.Error, ValueError) as error:
                raise ValueError("invalid base64 payload") from error
            digest = hashlib.sha256(restored).hexdigest()
            try:
                readable = restored.decode("utf-8")
            except UnicodeDecodeError:
                readable = None
            measurements.append({"backup_id": backup["id"], "file": name,
                                 "byte_length": len(restored), "decoded_bytes_hex": restored.hex(),
                                 "decoded_utf8": readable, "sha256": digest})
    return measurements

def analyse(case):
    measurements = measure_payloads(case)
    data = case["data"]
    expected = data["required_sha256"]
    recovery, rpo = moment(data["recovery_time"]), data["rpo_hours"]
    decisions, observations, qualified = {}, [], []
    for backup in data["backups"]:
        captured, until = moment(backup["captured_at"]), moment(backup["retained_until"])
        payload = backup["payload_base64"]
        mismatches = []
        for measurement in measurements:
            if measurement["backup_id"] != backup["id"]:
                continue
            name, digest = measurement["file"], measurement["sha256"]
            if digest != expected[name]:
                mismatches.append(name)
            observations.append(f'{backup["id"]}/{name}: decoded synthetic bytes={measurement["byte_length"]}; SHA-256={digest}; expected={expected[name]}; match={"yes" if digest == expected[name] else "no"}.')
        age_seconds = int((recovery - captured).total_seconds())
        missing = sorted(set(expected) - set(payload))
        retained = recovery < until
        result = "retention-expired" if not retained else "required-scope-missing" if missing else "restore-bytes-mismatch" if mismatches else "rpo-exceeded" if age_seconds > rpo * 3600 else "qualified-synthetic-copy"
        decisions[backup["id"]] = result
        if result == "qualified-synthetic-copy":
            qualified.append((captured, backup["id"]))
        observations.append(f'{backup["id"]}: age={age_seconds} seconds; RPO={rpo * 3600} seconds; retained={"yes" if retained else "no"}; missing={",".join(missing) or "none"}; mismatches={",".join(mismatches) or "none"}.')
    selected = max(qualified, key=lambda item: (item[0], item[1]))[1] if qualified else None
    decisions["recovery"] = "select:" + selected if selected else "no-qualified-copy"
    observations.append(f'Recovery candidate={selected or "none"}; latest qualifying capture wins, with lexical ID as a tie-break.')
    return {"decisions": decisions, "observations": observations, "limitations": [
        "Only embedded fictional payloads were decoded into memory and hashed. No real backup, disk file or application was restored.",
        "RPO is the permitted age of this synthetic recovery point, not recovery duration. A hash match establishes byte identity against the supplied manifest, not application usability.",
        "Retention is evaluated from supplied metadata; embedded evidence of an expired copy does not establish its real availability. Media health, encryption keys and full recovery procedures are outside scope."]}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
