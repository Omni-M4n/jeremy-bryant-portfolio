"""Original fictional evidence exercise. No network or host changes."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "dependency-review"


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
    "Only stable three-part numeric versions from 0 to 9999 per part are supported; prereleases, build metadata, ecosystem ranges and backports are rejected or outside scope.",
    "All packages and advisories are fictional. A range match is not proof of exploitability, and no supplied match is not proof that software is secure.",
]


def version(value):
    require(isinstance(value, str) and re.fullmatch(r"(0|[1-9][0-9]{0,3})\.(0|[1-9][0-9]{0,3})\.(0|[1-9][0-9]{0,3})", value), "expected stable X.Y.Z with each part 0-9999 and no leading zeroes")
    return tuple(int(part) for part in value.split("."))


def package(value):
    require(isinstance(value, str) and re.fullmatch(r"demo-[a-z][a-z-]{0,35}", value), "only fictional demo- package names are supported")


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "components advisories", "data")
    require(isinstance(data["advisories"], list) and len(data["advisories"]) <= 60, "invalid advisories")
    advisories, seen = [], set()
    for advisory in data["advisories"]:
        fields(advisory, "id package introduced fixed", "advisory")
        require(isinstance(advisory["id"], str) and re.fullmatch(r"DEMO-ADV-[0-9]{3}", advisory["id"]), "only fictional advisory IDs are supported")
        require(advisory["id"] not in seen, "duplicate advisory ID")
        seen.add(advisory["id"])
        package(advisory["package"])
        low, high = version(advisory["introduced"]), version(advisory["fixed"])
        require(low < high, "advisory range must increase")
        advisories.append((advisory, low, high))
    decisions, observations = {}, []
    for component in records(data["components"], "components"):
        fields(component, "id name version scope reachability evidence", "component")
        package(component["name"])
        installed = version(component["version"])
        require(component["scope"] in ("runtime", "development"), "unsupported scope")
        require(component["reachability"] in ("reachable", "not-demonstrated", "unknown"), "unsupported reachability")
        text(component["evidence"], "reachability evidence")
        supplied = [(a, low, high) for a, low, high in advisories if a["package"] == component["name"]]
        matches = [a for a, low, high in supplied if low <= installed < high]
        if not supplied:
            result = "no-advisory-supplied"
        elif not matches:
            result = "outside-supplied-ranges"
        elif component["scope"] == "development":
            result = "affected-review-build-exposure"
        else:
            result = {"reachable":"affected-prioritise-runtime-path", "not-demonstrated":"affected-validate-path", "unknown":"affected-investigate-path"}[component["reachability"]]
        decisions[component["id"]] = result
        ranges = [f"{a['id']}:[{a['introduced']},{a['fixed']})" for a in matches]
        observations.append(f"{component['id']}: {component['name']} {component['version']}; scope={component['scope']}; reachability={component['reachability']}; matches={joined(ranges)}; evidence={component['evidence']}.")
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
