"""Disposable plaintext file exercise. This is NOT a password manager."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import encoded, read_json, require, safe_path

FILES = {"store.json", "backup.json", "held-original.json", "export.json"}


def new_store():
    return {"dummy_only": True, "entries": [
        {"account": name + ".test", "password": secrets.token_urlsafe(24)}
        for name in ("library", "garden", "club")]}


def validate(store):
    require(isinstance(store, dict) and set(store) == {"dummy_only", "entries"} and store["dummy_only"] is True, "only this dummy store format is accepted")
    entries = store["entries"]
    require(isinstance(entries, list) and len(entries) == 3, "three dummy entries required")
    require(all(isinstance(row, dict) and set(row) == {"account", "password"} and isinstance(row["password"], str) and 20 <= len(row["password"]) <= 128 for row in entries), "invalid dummy entry")
    require({row["account"] for row in entries} == {"library.test", "garden.test", "club.test"}, "unknown dummy account")
    require(len({row["password"] for row in entries}) == 3, "dummy passwords must be different")


def operate(folder, command):
    folder = safe_path(folder)
    if command == "init":
        require(not folder.exists(), "use a fresh folder")
        store = new_store()
        validate(store)
        folder.mkdir(parents=True)
        (folder / "store.json").write_bytes(encoded(store))
        return {"operation": "init", "entries": 3, "storage": "PLAINTEXT-DUMMY-ONLY"}
    require(folder.is_dir(), "create the exercise first")
    for item in folder.iterdir():
        safe_path(item)
        require(item.is_file() and item.name in FILES, "folder contains an unexpected file")
    if command == "hold":
        require((folder / "backup.json").is_file() and not (folder / "held-original.json").exists(), "make a backup first; hold cannot overwrite")
        validate(read_json(folder / "store.json"))
        (folder / "store.json").rename(folder / "held-original.json")
        return {"operation": "hold", "original": "preserved", "active_store": "absent"}
    if command in ("backup", "export", "restore"):
        source = folder / ("backup.json" if command == "restore" else "store.json")
        target = folder / {"backup": "backup.json", "export": "export.json", "restore": "store.json"}[command]
        validate(read_json(source))
        require(not target.exists(), "refusing to overwrite an existing file")
        with target.open("xb") as handle:
            handle.write(source.read_bytes())
        return {"operation": command, "byte_copy_matches": source.read_bytes() == target.read_bytes(), "storage": "PLAINTEXT-DUMMY-ONLY"}
    if command == "verify":
        store = read_json(folder / "store.json")
        validate(store)
        require((folder / "backup.json").is_file(), "backup is missing")
        same = (folder / "store.json").read_bytes() == (folder / "backup.json").read_bytes()
        return {"operation": "verify", "entries": 3, "unique": True, "matches_backup": same, "store_sha256": hashlib.sha256((folder / "store.json").read_bytes()).hexdigest(), "real_vault_unlock": "not-tested"}
    if command == "clean":
        for item in list(folder.iterdir()):
            item.unlink()
        folder.rmdir()
        return {"operation": "clean", "exercise_files_removed": True}
    raise ValueError("unknown operation")


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "backup", "hold", "restore", "verify", "export", "clean"])
    parser.add_argument("--folder", default="run/vault-01")
    args = parser.parse_args()
    try:
        relative = Path(args.folder)
        require(not relative.is_absolute() and ".." not in relative.parts, "use a relative folder below run/")
        folder = safe_path(ROOT / relative)
        require(safe_path(ROOT / "run") in folder.parents, "folder must be below run/")
        result = operate(folder, args.command)
        print(json.dumps(result, indent=2))
        return 1 if result.get("matches_backup") is False else 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
