"""Original fictional evidence exercise. No network or host changes."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "secret-handling"


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()),
            f"{label}: missing or unsupported fields")


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 240,
            f"{label}: expected nonempty text up to 240 characters")


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}", value),
            "record IDs must be lowercase letters, digits and hyphens")


def records(value, label):
    require(isinstance(value, list) and 0 < len(value) <= 60,
            f"{label}: expected 1-60 records")
    seen = set()
    for row in value:
        require(isinstance(row, dict) and "id" in row, f"{label}: invalid record")
        identifier(row["id"])
        require(row["id"] not in seen, f"{label}: duplicate ID")
        seen.add(row["id"])
    return value


def boolean(value, label):
    require(type(value) is bool, f"{label}: expected boolean")


def joined(values):
    return ",".join(sorted(values)) or "none"

LIMITS = [
    "Only exact listed DEMO_ONLY_TOKEN markers are matched; absence is not proof that an artifact contains no secrets.",
    "All values are deliberately fake. No credentials are tested, revoked, uploaded or changed; real response needs owner-led containment and service continuity planning.",
]


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "secrets files", "data")
    secrets = records(data["secrets"], "secrets")
    markers = set()
    for secret in secrets:
        fields(secret, "id marker state", "secret")
        require(isinstance(secret["marker"], str) and re.fullmatch(r"DEMO_ONLY_TOKEN_[A-Z][A-Z0-9_]{0,39}", secret["marker"]), "only explicit dummy markers are supported")
        require(secret["marker"] not in markers, "duplicate dummy marker")
        markers.add(secret["marker"])
        require(secret["state"] in ("active", "revoked"), "unknown dummy credential state")
    files = records(data["files"], "files")
    artifacts = {}
    for file in files:
        fields(file, "id kind audience lines", "artifact record")
        require(file["kind"] in ("config", "diff", "log"), "unsupported artifact kind")
        require(file["audience"] in ("local", "shared", "public"), "unsupported audience")
        lines = file["lines"]
        require(isinstance(lines, list) and 0 < len(lines) <= 100 and all(isinstance(line, str) and len(line) <= 400 and "\n" not in line and "\r" not in line for line in lines), "artifact lines must be bounded single lines")
        artifacts[file["id"] + ".txt"] = "\n".join(lines) + "\n"
    require(case["artifacts"] == artifacts, "readable artifacts must exactly match data.files")
    decisions, observations = {}, []
    for secret in secrets:
        pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(secret["marker"]) + r"(?![A-Za-z0-9_])")
        locations, audiences = [], set()
        for file in files:
            for number, line in enumerate(file["lines"], 1):
                if pattern.search(line):
                    locations.append(f"{file['id']}.txt:L{number}({file['kind']},{file['audience']})")
                    audiences.add(file["audience"])
        if not locations:
            decision = "not-seen-in-supplied-artifacts"
        elif secret["state"] == "revoked":
            decision = "confirm-revocation;clean-copies;review-use"
        elif audiences & {"shared", "public"}:
            decision = "contain;revoke-and-replace;clean-copies;review-use"
        else:
            decision = "relocate-before-sharing"
        decisions[secret["id"]] = decision
        observations.append(f"{secret['id']}: state={secret['state']}; locations={';'.join(locations) or 'none'}; audiences={joined(audiences)}.")
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
