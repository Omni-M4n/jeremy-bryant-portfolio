"""Change only toy package files in a temporary directory below this lab's run/."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import require, safe_path, encoded
ROOT = Path(__file__).resolve().parent
DEVICE_NAMES = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}

def receipt_path(name):
    # Check raw components before Path can simplify aliases such as dot segments.
    require(isinstance(name, str) and 0 < len(name) <= 240, "bounded receipt path required")
    parts = name.replace("\\", "/").split("/")
    require(len(parts) >= 2 and parts[0] == "run", "receipt must be below run/")
    for part in parts:
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", part) is not None
                and not part.endswith("."), "use plain path names without spaces, colons or trailing dots")
        require(part.split(".")[0].upper() not in DEVICE_NAMES, "reserved Windows device name")
    target = safe_path(ROOT / Path(*parts))
    require(safe_path(ROOT / "run") in target.parents and target.suffix == ".json"
            and not target.exists(), "use a new JSON receipt below run/")
    return target

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def greet(path):
    package = json.loads(path.read_text(encoding="utf-8"))
    return package["greeting"] + " Sam"

def exercise(regression=False):
    run_root = safe_path(ROOT / "run")
    run_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="patch-files-", dir=run_root) as temporary:
        area = Path(temporary)
        require(run_root in area.resolve().parents, "temporary directory must remain below run/")
        installed, backup, candidate = (area / name for name in ("installed.json", "backup.json", "candidate.json"))
        installed.write_bytes(encoded({"version":"1.0", "greeting":"Hello"}))
        shutil.copyfile(installed, backup)
        before = digest(installed)
        candidate.write_bytes(encoded({"version":"1.1", "greeting":"Goodbye" if regression else "Hello"}))
        shutil.copyfile(candidate, installed)
        applied = digest(installed)
        installed_version = json.loads(installed.read_text())["version"]
        smoke = greet(installed) == "Hello Sam"
        shutil.copyfile(backup, installed)
        restored = digest(installed)
        receipt = {"exercise":"toy-file-update", "installed_version_after_apply":installed_version,
                   "update_smoke_passed":smoke, "before_sha256":before, "applied_sha256":applied,
                   "restored_sha256":restored, "rollback_bytes_match":before == restored,
                   "rollback_smoke_passed":greet(installed) == "Hello Sam"}
    receipt["temporary_directory_removed"] = not area.exists()
    return receipt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regression", action="store_true")
    parser.add_argument("--receipt", required=True, help="new JSON file below run/")
    args = parser.parse_args()
    target = receipt_path(args.receipt)
    target.parent.mkdir(parents=True, exist_ok=True)
    receipt = exercise(args.regression)
    target.write_bytes(encoded(receipt))
    print(encoded(receipt).decode(), end="")

if __name__ == "__main__":
    try: main()
    except (ValueError, OSError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        raise SystemExit(2)
