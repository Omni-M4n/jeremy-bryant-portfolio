"""Review fictional password and recovery evidence, without secret values."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAB_ID = "password-vault-recovery"
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require

LIMITS = ["Labels stand for fake passwords; length and a generated flag do not prove entropy or resistance to attack.", "A copied file is not a tested recovery. The bundled file exercise is unencrypted and must never hold real secrets."]


def keys(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")


def analyse(case):
    data = case["data"]
    keys(data, ["entries", "backup"])
    require(isinstance(data["entries"], list) and 0 < len(data["entries"]) <= 20, "supply 1-20 entries")
    ids, labels = set(), []
    for row in data["entries"]:
        keys(row, ["id", "account", "secret_label", "generated", "length"])
        require(isinstance(row["id"], str) and re.fullmatch(r"e[0-9]+", row["id"]) and row["id"] not in ids, "unique neutral entry IDs required")
        ids.add(row["id"])
        require(isinstance(row["account"], str) and re.fullmatch(r"[a-z]+\.test", row["account"]), "use fictional .test accounts")
        require(isinstance(row["secret_label"], str) and re.fullmatch(r"label-[a-z]+", row["secret_label"]), "supply a label, never a password")
        require(type(row["generated"]) is bool and type(row["length"]) is int and 1 <= row["length"] <= 128, "invalid generator evidence or length")
        labels.append(row["secret_label"])
    require(len({r["account"] for r in data["entries"]}) == len(ids), "duplicate account")
    backup = data["backup"]
    keys(backup, ["format", "copy_exists", "unlock_test", "separate_location", "recovery_in_same_store"])
    require(backup["format"] in ("encrypted", "plaintext"), "unknown backup format")
    for field in ("copy_exists", "unlock_test", "separate_location", "recovery_in_same_store"):
        require(type(backup[field]) is bool, "backup evidence must be boolean")
    require(not backup["unlock_test"] or backup["copy_exists"], "cannot test a missing copy")
    require(not backup["separate_location"] or backup["copy_exists"], "cannot separately store a missing copy")
    decisions, observations = {}, []
    for row in data["entries"]:
        flags = []
        if labels.count(row["secret_label"]) > 1:
            flags.append("reused")
        if not row["generated"]:
            flags.append("generation-unverified")
        if row["length"] < 20:
            flags.append("below-practice-length")
        decisions[row["id"]] = "+".join(flags) or "meets-practice-checks"
        observations.append(f"{row['id']}: label_count={labels.count(row['secret_label'])}; generated={str(row['generated']).lower()}; length={row['length']}.")
    flags = []
    for condition, name in [(not backup["copy_exists"], "copy-missing"), (not backup["unlock_test"], "restore-untested"), (not backup["separate_location"], "same-location-risk"), (backup["format"] == "plaintext", "plaintext-exposure"), (backup["recovery_in_same_store"], "circular-recovery")]:
        if condition:
            flags.append(name)
    decisions["backup"] = "+".join(flags) or "meets-practice-checks"
    observations.append(f"Backup format={backup['format']}; copy={str(backup['copy_exists']).lower()}; tested={str(backup['unlock_test']).lower()}; separate={str(backup['separate_location']).lower()}; recovery_inside={str(backup['recovery_in_same_store']).lower()}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
