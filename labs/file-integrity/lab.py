"""Offline file-integrity practice. See README.md for the command and trust contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys


ROOT = Path(__file__).resolve().parent
VARIANTS = ("approved", "mixed", "replacement", "suspect-baseline")
MAX_BYTES = 1_000_000
MAX_FILES = 100
MAX_TOTAL = 10_000_000
COMPONENT = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
RESERVED = {"con", "prn", "aux", "nul"} | {
    f"{prefix}{n}" for prefix in ("com", "lpt") for n in range(1, 10)
}


class InputError(ValueError):
    """An input is malformed or outside this lab's bounded file model."""


def require(condition, message):
    if not condition:
        raise InputError(message)


def exact_keys(value, names, where):
    require(isinstance(value, dict) and set(value) == set(names),
            f"{where}: expected exactly these fields: {', '.join(names)}")


def version(value):
    require(type(value) is int and value == 1, "schema_version must be integer 1")


def relative_name(value):
    require(isinstance(value, str) and len(value) <= 240, "invalid relative file name")
    parts = value.split("/")
    require(1 <= len(parts) <= 8, "relative file path is too deep")
    for part in parts:
        require(COMPONENT.fullmatch(part) is not None and not part.endswith(".")
                and part.split(".")[0] not in RESERVED,
                f"unsafe relative file name: {value!r}")
    return value


def json_name(value):
    relative_name(value)
    require("/" not in value and value.endswith(".json"), "use one lowercase .json file name")
    return value


def digest(value):
    require(isinstance(value, str) and DIGEST.fullmatch(value) is not None, "invalid SHA-256 digest")
    return value


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def safe_path(path, *, exists=True):
    """Reject links/reparse points in the leaf and every existing ancestor."""
    path = Path(path)
    require(".." not in path.parts, "parent traversal is not allowed")
    path = Path(os.path.abspath(path))
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
        except FileNotFoundError:
            require(part == path and not exists, f"missing path: {part}")
            continue
        require(not stat.S_ISLNK(info.st_mode)
                and not (getattr(info, "st_file_attributes", 0)
                         & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)),
                f"links and reparse points are not allowed: {part}")
    return path


def read_bytes(path):
    path = safe_path(path)
    info = path.stat()
    require(stat.S_ISREG(info.st_mode), f"not a regular file: {path}")
    require(info.st_nlink == 1, f"hard-linked files are not allowed: {path}")
    require(info.st_size <= MAX_BYTES, f"file exceeds {MAX_BYTES} bytes: {path}")
    with path.open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, f"file exceeds {MAX_BYTES} bytes: {path}")
    return data


def write_new(path, data):
    path = safe_path(path, exists=False)
    require(not path.exists(), f"refusing to overwrite: {path}")
    with path.open("xb") as handle:
        handle.write(data)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def reject_constant(value):
    raise InputError(f"nonstandard JSON number: {value}")


def load_json(path):
    try:
        return json.loads(read_bytes(path).decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (ValueError, RecursionError) as exc:
        raise InputError(f"{path}: {exc}") from exc


def inventory_tree(root, *, allow_empty=False):
    root = safe_path(root)
    require(root.is_dir(), f"not a directory: {root}")
    found = {}
    total = 0
    directory_count = 0

    def visit(folder, depth):
        nonlocal total, directory_count
        require(depth <= 8, "tree exceeds eight directory levels")
        directory_count += 1
        require(directory_count <= MAX_FILES, "too many directories")
        # Inspect each entry before following it; directory links are not traversed.
        with os.scandir(folder) as entries:
            entries = sorted(entries, key=lambda entry: entry.name)
        require(len(entries) <= MAX_FILES, "too many entries in a directory")
        for entry in entries:
            path = safe_path(Path(folder) / entry.name)
            name = relative_name(path.relative_to(root).as_posix())
            info = path.lstat()
            if stat.S_ISDIR(info.st_mode):
                visit(path, depth + 1)
            else:
                data = read_bytes(path)
                total += len(data)
                require(total <= MAX_TOTAL, "tree exceeds 10 MB")
                found[name] = {"sha256": sha(data), "bytes": len(data)}
                require(len(found) <= MAX_FILES, "too many files")

    visit(root, 0)
    require(bool(found) or allow_empty, "cannot baseline an empty tree")
    return {"schema_version": 1, "files": dict(sorted(found.items()))}


def validate_inventory(value, *, allow_empty=False):
    exact_keys(value, ("schema_version", "files"), "baseline")
    version(value["schema_version"])
    files = value["files"]
    require(isinstance(files, dict) and (0 if allow_empty else 1) <= len(files) <= MAX_FILES,
            "invalid baseline file count")
    for name, row in files.items():
        relative_name(name)
        exact_keys(row, ("sha256", "bytes"), f"baseline entry {name}")
        digest(row["sha256"])
        require(type(row["bytes"]) is int and 0 <= row["bytes"] <= MAX_BYTES, "invalid file size")
        parent = Path(name).parent
        while parent.as_posix() != ".":
            require(parent.as_posix() not in files, "baseline path is both a file and a directory")
            parent = parent.parent
    require(sum(row["bytes"] for row in files.values()) <= MAX_TOTAL, "baseline exceeds 10 MB")
    return value


def validate_scenario(value):
    exact_keys(value, ("schema_version", "format", "variant", "seed", "brief",
                       "baseline_context", "reference_anchor_sha256"), "scenario")
    version(value["schema_version"])
    require(value["format"] == "fictional-file-integrity-sandbox", "not a generated lab sandbox")
    require(isinstance(value["variant"], str) and value["variant"] in VARIANTS, "unknown variant")
    require(type(value["seed"]) is int and 0 <= value["seed"] <= 999999, "invalid seed")
    for key in ("brief", "baseline_context"):
        require(isinstance(value[key], str) and 0 < len(value[key]) <= 2000, f"invalid {key}")
    if value["reference_anchor_sha256"] is not None:
        digest(value["reference_anchor_sha256"])
    return value


def validate_approvals(value):
    exact_keys(value, ("schema_version", "changes"), "approvals")
    version(value["schema_version"])
    require(isinstance(value["changes"], list) and len(value["changes"]) <= MAX_FILES, "invalid approvals list")
    seen = set()
    for row in value["changes"]:
        exact_keys(row, ("path", "before_sha256", "after_sha256", "ticket", "reason"), "approval")
        name = relative_name(row["path"])
        require(name not in seen, "duplicate approval path")
        seen.add(name)
        for key in ("before_sha256", "after_sha256"):
            if row[key] is not None:
                digest(row[key])
        require(row["before_sha256"] != row["after_sha256"], "approval must describe a change")
        for key in ("ticket", "reason"):
            require(isinstance(row[key], str) and 0 < len(row[key]) <= 1000, f"invalid approval {key}")
    return value


def sandbox(run):
    run = safe_path(run)
    require(run.is_dir(), "run must be a directory")
    scenario = validate_scenario(load_json(run / "scenario.json"))
    return run, scenario


def compare(before, after, approvals):
    """Compare names/hashes from independently scanned maps; never follow baseline paths."""
    validate_inventory(before)
    validate_inventory(after, allow_empty=True)
    validate_approvals(approvals)
    permitted = {row["path"]: row for row in approvals["changes"]}
    used = set()
    rows = []
    for name in sorted(before["files"].keys() | after["files"].keys()):
        old = before["files"].get(name)
        new = after["files"].get(name)
        old_hash = old["sha256"] if old else None
        new_hash = new["sha256"] if new else None
        change = "added" if old is None else "deleted" if new is None else "unchanged" if old == new else "modified"
        approval = permitted.get(name)
        approved = bool(change != "unchanged" and approval
                        and approval["before_sha256"] == old_hash
                        and approval["after_sha256"] == new_hash)
        if approved:
            used.add(name)
        rows.append({"path": name, "change": change,
                     "assessment": "unchanged" if change == "unchanged" else "approved" if approved else "unexpected",
                     "before_sha256": old_hash, "after_sha256": new_hash,
                     "ticket": approval["ticket"] if approved else None})
    return rows, sorted(permitted.keys() - used)


def make_case(variant, seed):
    require(variant in VARIANTS, "unknown variant")
    require(type(seed) is int and 0 <= seed <= 999999, "seed must be 0 to 999999")
    label = f"harbour-{seed:06d}"
    clean = {
        "config/service.txt": f"service={label}\nremote_access=disabled\n".encode(),
        "docs/contact.txt": b"Owner: fictional lab help desk\nReview interval: 30 days\n",
        "docs/notice.txt": f"Training notice {seed}\nOpening time: 09:00\n".encode(),
        "reports/archive.txt": f"Synthetic archive {seed}\nItems: {10 + seed % 13}\n".encode(),
    }
    reference = dict(clean)
    current = dict(clean)
    current["docs/notice.txt"] = f"Training notice {seed}\nOpening time: 10:00\n".encode()
    approval_rows = []

    def approve(name, reason):
        approval_rows.append({"path": name, "before_sha256": sha(clean[name]) if name in clean else None,
                              "after_sha256": sha(current[name]) if name in current else None,
                              "ticket": f"CHANGE-{seed:06d}", "reason": reason})

    approve("docs/notice.txt", "The fictional owner approved the opening-time update to 10:00.")
    if variant == "mixed":
        current["config/service.txt"] = f"service={label}\nremote_access=enabled\n".encode()
        current["docs/temporary-note.txt"] = b"Synthetic draft: source and purpose not recorded.\n"
        del current["reports/archive.txt"]
    elif variant == "replacement":
        del current["reports/archive.txt"]
        current["reports/current.txt"] = f"Synthetic current report {seed}\nItems: {11 + seed % 13}\n".encode()
        approve("reports/archive.txt", "The fictional owner approved removal of this obsolete dummy report.")
        approve("reports/current.txt", "The fictional owner approved this exact replacement report.")
    elif variant == "suspect-baseline":
        reference["config/service.txt"] = f"service={label}\nremote_access=enabled\n".encode()
        current["config/service.txt"] = reference["config/service.txt"]
    reference_inventory = {"schema_version": 1, "files": {
        name: {"sha256": sha(data), "bytes": len(data)} for name, data in sorted(reference.items())}}
    anchor = None if variant == "suspect-baseline" else sha(encoded(reference_inventory))
    scenario = {
        "schema_version": 1, "format": "fictional-file-integrity-sandbox", "variant": variant, "seed": seed,
        "brief": "Review changes to a fictional community workshop's small folder. The change list is supplied training authority. Record evidence, uncertainty, and a next action; do not repair files automatically.",
        "baseline_context": (
            "The reference folder arrived after the reported change window. Nobody verified its earlier state, and there is no independent baseline anchor. An older written requirement says remote_access should be disabled. Compare that requirement with reference/config/service.txt and current/config/service.txt."
            if anchor is None else
            "For this exercise, the scenario records the hash of a checked reference inventory from before the change window. Treat this supplied scenario and approvals as training authority. They are editable local files, not authenticated production evidence."
        ),
        "reference_anchor_sha256": anchor,
    }
    expected = {
        "schema_version": 1,
        "answer_key_only": True,
        "baseline_status": "unverified-no-anchor" if anchor is None else "matches-exercise-anchor",
        "approved": ["docs/notice.txt"] + (["reports/archive.txt", "reports/current.txt"] if variant == "replacement" else []),
        "unexpected": ["config/service.txt", "docs/temporary-note.txt", "reports/archive.txt"] if variant == "mixed" else [],
        "check_exit_code": 1 if variant in ("mixed", "suspect-baseline") else 0,
        "reasoning": (
            "No config difference appears because both supplied trees already contain the same changed bytes. The written disabled requirement conflicts with both. Baseline provenance must be investigated before claiming the folder is clean."
            if anchor is None else
            "Explain each difference using exact before/after hashes and the supplied change list. An unexplained difference needs investigation; its hash alone does not establish malicious intent."
        ),
    }
    return reference, current, scenario, {"schema_version": 1, "changes": approval_rows}, expected


def generate(run, variant, seed):
    run = safe_path(run, exists=False)
    require(not run.exists(), "run folder already exists; choose a fresh --run name")
    reference, current, scenario, approvals, expected = make_case(variant, seed)
    run.mkdir()
    for folder, files in (("reference", reference), ("current", current)):
        for name, data in files.items():
            path = run / folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            write_new(path, data)
    for name, value in (("scenario.json", scenario), ("approvals.json", approvals), ("expected-findings.json", expected)):
        write_new(run / name, encoded(value))
    write_new(run / "start-here.txt", (
        f"Fictional offline file-integrity practice: {variant}; seed {seed}.\n"
        "Read scenario.json and approvals.json. Keep reference/ intact.\n"
        "Create a baseline from reference/, then check current/.\n"
        "Explain differences and baseline confidence before opening expected-findings.json.\n"
        "Generated files are dummy text; no execution, networking, or automatic repair occurs.\n"
    ).encode())
    return {"command": "generate", "run": str(run), "variant": variant, "seed": seed,
            "next": "Run baseline and check with this same --run folder."}


def baseline(run, source, name):
    run, _ = sandbox(run)
    json_name(name)
    require(source in ("reference", "current"), "source must be reference or current")
    payload = encoded(inventory_tree(run / source))
    write_new(run / name, payload)
    return {"command": "baseline", "file": str(run / name), "source": source, "sha256": sha(payload),
            "note": "An inventory records bytes at this moment; creating it does not establish their trustworthiness."}


def check(run, name):
    run, scenario = sandbox(run)
    json_name(name)
    before = validate_inventory(load_json(run / name))
    after = inventory_tree(run / "current", allow_empty=True)
    approvals = validate_approvals(load_json(run / "approvals.json"))
    rows, unused = compare(before, after, approvals)
    anchor = scenario["reference_anchor_sha256"]
    # Compare canonical content so harmless JSON indentation does not change the anchor.
    actual_hash = sha(encoded(before))
    status = "unverified-no-anchor" if anchor is None else (
        "matches-exercise-anchor" if actual_hash == anchor else "does-not-match-exercise-anchor")
    counts = {key: sum(row["assessment"] == key for row in rows)
              for key in ("unchanged", "approved", "unexpected")}
    passed = counts["unexpected"] == 0 and status == "matches-exercise-anchor"
    return {"command": "check", "passed": passed, "baseline_status": status,
            "baseline_sha256": actual_hash, "counts": counts, "observations": rows,
            "unused_approvals": unused,
            "conclusion": "All observed differences match supplied approvals and the exercise anchor matches."
            if passed else "Review unexplained differences or baseline confidence before making a clean-state claim.",
            "limit": "SHA-256 comparison describes bytes, not intent, authorship, authenticity, or learner competence."}


def manifest_payload():
    names = (".gitattributes", ".gitignore", "README.md", "WORKED-EXAMPLE.md", "DRILLS.md", "lab.py", "test_lab.py")
    paths = [ROOT / name for name in names]
    fixtures = ROOT / "fixtures" / "worked-example"
    # The bounded scanner checks links and sizes even for the shipped fixture inventory.
    fixture_inventory = inventory_tree(fixtures)
    paths.extend(fixtures / name for name in fixture_inventory["files"])
    return {"schema_version": 1,
            "origin": "Original fictional offline training lab, created October 2026; no coursework or production inputs.",
            "authorship_scope": "Supplied guided utility, scenarios and answer key; independent learner completion has not been assessed.",
            "fixture_recipe": "python lab.py generate --variant mixed --seed 23 --run fixtures/worked-example; python lab.py baseline --run fixtures/worked-example",
            "scope": "SHA-256 inventory verifies file identity only, not origin, authenticity, factual acceptance or competence.",
            "sha256_files": {path.relative_to(ROOT).as_posix(): sha(read_bytes(path)) for path in sorted(paths)}}


def manifest(write):
    expected = manifest_payload()
    if write:
        write_new(ROOT / "PROVENANCE.json", encoded(expected))
        return {"command": "manifest", "passed": True, "operation": "write", "files": len(expected["sha256_files"])}
    actual = load_json(ROOT / "PROVENANCE.json")
    require(isinstance(actual, dict) and isinstance(actual.get("sha256_files"), dict), "invalid provenance inventory")
    changed = sorted(name for name in expected["sha256_files"].keys() | actual["sha256_files"].keys()
                     if expected["sha256_files"].get(name) != actual["sha256_files"].get(name))
    return {"command": "manifest", "passed": actual == expected, "operation": "verify",
            "files": len(expected["sha256_files"]), "changed_files": changed,
            "metadata_matches": {key: value for key, value in actual.items() if key != "sha256_files"}
            == {key: value for key, value in expected.items() if key != "sha256_files"}}


def render(result, as_json):
    if as_json:
        print(encoded(result).decode(), end="")
        return
    print(f"{result['command']}: " + ("OK" if result.get("passed", True) else "REVIEW NEEDED"))
    for key, value in result.items():
        if key not in ("command", "passed", "observations"):
            print(f"  {key}: {value}")
    for row in result.get("observations", []):
        print(f"  {row['path']}: {row['change']} / {row['assessment']}"
              + (f" / {row['ticket']}" if row["ticket"] else ""))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "baseline", "check"):
        command = commands.add_parser(name)
        command.add_argument("--run", type=Path, default=ROOT / "run")
        command.add_argument("--json", action="store_true")
        if name == "generate":
            command.add_argument("--variant", choices=VARIANTS, default="mixed")
            command.add_argument("--seed", type=int, default=23)
        elif name == "baseline":
            command.add_argument("--source", choices=("reference", "current"), default="reference")
            command.add_argument("--name", default="baseline.json", help="new JSON file name within the run")
        else:
            command.add_argument("--baseline", default="baseline.json", help="JSON file name within the run")
    command = commands.add_parser("manifest")
    mode = command.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="create missing provenance inventory; refuses overwrite")
    mode.add_argument("--verify", action="store_true")
    command.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            result = generate(args.run, args.variant, args.seed)
        elif args.command == "baseline":
            result = baseline(args.run, args.source, args.name)
        elif args.command == "check":
            result = check(args.run, args.baseline)
        else:
            result = manifest(args.write)
        render(result, args.json)
        return 0 if result.get("passed", True) else 1
    except (InputError, OSError, UnicodeError, RecursionError) as exc:
        error = {"command": args.command, "error": str(exc)}
        print(encoded(error).decode().strip() if args.json else f"Input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
