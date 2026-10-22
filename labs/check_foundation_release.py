"""Validate the 20-lab catalog/inventory; optional isolated tests. See --help."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "FOUNDATION-MANIFEST.json"
COMMON = ("FOUNDATION-CONTRACT.md", "foundation-catalog.json", "foundation_runtime.py", "test_foundation_runtime.py", "check_foundation_release.py")
REQUIRED = ("README.md", "WORKED-EXAMPLE.md", "DRILLS.md", "lab.py", "test_lab.py", ".gitignore")


def inventory():
    catalog = json.loads((ROOT / "foundation-catalog.json").read_text(encoding="utf-8"))
    ids = [lab["id"] for lab in catalog["labs"]]
    if len(ids) != 20 or len(set(ids)) != 20 or any(not re.fullmatch(r"[a-z][a-z0-9-]+", name) for name in ids):
        raise ValueError("expected exactly twenty distinct safe lab IDs")
    names = set(COMMON)
    for lab in ids:
        base = ROOT / lab
        required = list(REQUIRED) + [f"{folder}/{case}.json" for folder in ("fixtures", "reference") for case in ("guided", "changed", "challenge")]
        for name in required:
            if not (base / name).is_file():
                raise ValueError(f"missing required file: {lab}/{name}")
        for path in base.rglob("*"):
            relative = path.relative_to(base)
            if "run" in relative.parts or "__pycache__" in relative.parts or path.suffix == ".pyc":
                continue
            if path.is_symlink():
                raise ValueError(f"linked publication input: {lab}/{relative.as_posix()}")
            if path.is_file():
                names.add(path.relative_to(ROOT).as_posix())
    hashes = {}
    for name in sorted(names):
        data = (ROOT / name).read_bytes()
        if b"\r" in data:
            raise ValueError(f"expected UTF-8/LF source: {name}")
        data.decode("utf-8")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return ids, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true", help="create a missing reviewed inventory; refuses overwrite")
    parser.add_argument("--tests", action="store_true", help="also run shared-runtime tests, each lab's isolated unit suite and reference verification")
    parser.add_argument("--receipt", type=Path, help="save detailed results to a new JSON file; refuses overwrite")
    args = parser.parse_args()
    if args.receipt and args.receipt.exists():
        parser.error("receipt already exists")
    try:
        ids, hashes = inventory()
        current = {"schema_version": 1, "scope": "Twenty original fictional foundation labs; hashes establish file identity, not learner competence or authenticity.", "lab_count": 20, "case_count": 60, "sha256": hashes}
        if args.write_manifest:
            with MANIFEST.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(current, indent=2) + "\n")
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
        errors = []
        if current != expected:
            errors.append("reviewed file inventory differs")
        checks = []
        if args.tests:
            jobs = [("shared-runtime", ROOT, ["-m", "unittest", "discover", "-s", ".", "-p", "test_foundation_runtime.py", "-v"])]
            for lab in ids:
                jobs.extend([(lab + "/unit", ROOT / lab, ["-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"]),
                             (lab + "/reference", ROOT / lab, ["lab.py", "verify"])])
            for name, cwd, arguments in jobs:
                result = subprocess.run([sys.executable, *arguments], cwd=cwd, capture_output=True, text=True, timeout=90)
                checks.append({"name": name, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
                print(json.dumps({"check": name, "exit_code": result.returncode}), flush=True)
                if result.returncode:
                    errors.append(name)
        receipt = {"status": "failed" if errors else "passed", "labs": len(ids), "cases": 60, "files": len(hashes), "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), "checks": checks, "errors": errors}
        if args.receipt:
            with args.receipt.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({key: value for key, value in receipt.items() if key != "checks"}), flush=True)
        return int(bool(errors))
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(f"Release check error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
