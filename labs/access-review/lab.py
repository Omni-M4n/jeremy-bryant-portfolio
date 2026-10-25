"""Offline, allow-only permission lab. See README.md for the exact model."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import sys


ROOT = Path(__file__).resolve().parent
ACTIONS = ("read", "write", "delete")
FILES = (
    "scenario.json", "expected-access.json", "starting-policy.json",
    "practice-policy.json", "solution-policy.json", "START-HERE.txt",
)
ID_PATTERN = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
MAX_INPUT_BYTES = 2_000_000


class InputError(ValueError):
    """A supplied file is not valid input for this model."""


def require(condition, message):
    if not condition:
        raise InputError(message)


def keys(value, fields, where):
    require(isinstance(value, dict), f"{where}: expected an object")
    require(set(value) == set(fields), f"{where}: expected fields {', '.join(fields)}")


def version(value, where):
    require(type(value) is int and value == 1, f"{where}: schema_version must be integer 1")


def identifier(value, where):
    require(isinstance(value, str) and ID_PATTERN.fullmatch(value) is not None,
            f"{where}: expected a lowercase ID of 1-64 characters")
    return value


def nonempty_text(value, where):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 1000,
            f"{where}: expected nonempty text, at most 1000 characters")


def list_value(value, where, *, empty=False):
    require(isinstance(value, list), f"{where}: expected a list")
    require(empty or bool(value), f"{where}: must not be empty")
    require(len(value) <= 1000, f"{where}: too many entries")


def action_list(value, where):
    list_value(value, where)
    require(all(isinstance(action, str) and action in ACTIONS for action in value),
            f"{where}: actions must be read, write, or delete")
    require(len(value) == len(set(value)), f"{where}: duplicate action")


def validate_scenario(scenario):
    keys(scenario, ("schema_version", "title", "variant", "seed", "resources",
                    "roles", "identities", "business_rules"), "scenario")
    version(scenario["schema_version"], "scenario")
    nonempty_text(scenario["title"], "scenario.title")
    require(isinstance(scenario["variant"], str)
            and scenario["variant"] in ("guided", "hints", "unfamiliar"), "scenario: unknown variant")
    require(type(scenario["seed"]) is int and 0 <= scenario["seed"] <= 2**32 - 1,
            "scenario.seed: expected an integer between 0 and 4294967295")
    known = {}
    for collection in ("resources", "roles"):
        entries = scenario[collection]
        list_value(entries, f"scenario.{collection}")
        require(len(entries) <= 20, f"scenario.{collection}: maximum is 20")
        ids = set()
        for entry in entries:
            keys(entry, ("id", "purpose"), f"scenario.{collection} entry")
            item_id = identifier(entry["id"], f"scenario.{collection}.id")
            require(item_id not in ids, f"scenario.{collection}: duplicate ID {item_id}")
            nonempty_text(entry["purpose"], f"scenario.{collection}.purpose")
            ids.add(item_id)
        known[collection] = ids
    identities = scenario["identities"]
    list_value(identities, "scenario.identities")
    require(len(identities) <= 20, "scenario.identities: maximum is 20")
    seen = set()
    for entry in identities:
        keys(entry, ("id", "role"), "scenario.identities entry")
        item_id = identifier(entry["id"], "scenario.identities.id")
        role = identifier(entry["role"], "scenario.identities.role")
        require(item_id not in seen, f"scenario.identities: duplicate ID {item_id}")
        require(role in known["roles"], f"scenario.identities: unknown role {role}")
        seen.add(item_id)
    list_value(scenario["business_rules"], "scenario.business_rules")
    pairs = set()
    for rule in scenario["business_rules"]:
        keys(rule, ("role", "resource", "actions", "reason"), "business rule")
        role = identifier(rule["role"], "business rule.role")
        resource = identifier(rule["resource"], "business rule.resource")
        require(role in known["roles"], f"business rule: unknown role {role}")
        require(resource in known["resources"], f"business rule: unknown resource {resource}")
        require((role, resource) not in pairs, "business rules: duplicate role/resource pair")
        action_list(rule["actions"], "business rule.actions")
        nonempty_text(rule["reason"], "business rule.reason")
        pairs.add((role, resource))
    return scenario


def validate_policy(policy, scenario):
    keys(policy, ("schema_version", "grants"), "policy")
    version(policy["schema_version"], "policy")
    list_value(policy["grants"], "policy.grants", empty=True)
    roles = {entry["id"] for entry in scenario["roles"]}
    resources = {entry["id"] for entry in scenario["resources"]}
    pairs = set()
    for grant in policy["grants"]:
        keys(grant, ("role", "resource", "actions"), "grant")
        role = identifier(grant["role"], "grant.role")
        resource = identifier(grant["resource"], "grant.resource")
        require(role in roles, f"grant: unknown role {role}")
        require(resource in resources, f"grant: unknown resource {resource}")
        require((role, resource) not in pairs, "policy: duplicate role/resource pair")
        action_list(grant["actions"], "grant.actions")
        pairs.add((role, resource))
    return policy


def decisions(scenario):
    return itertools.product(
        (entry["id"] for entry in scenario["identities"]),
        (entry["id"] for entry in scenario["resources"]), ACTIONS,
    )


def rules_index(scenario):
    return {(rule["role"], rule["resource"], action)
            for rule in scenario["business_rules"] for action in rule["actions"]}


def expected_from_rules(scenario):
    roles = {entry["id"]: entry["role"] for entry in scenario["identities"]}
    required = rules_index(scenario)
    return {"schema_version": 1, "decisions": [
        {"identity": identity, "resource": resource, "action": action,
         "allowed": (roles[identity], resource, action) in required}
        for identity, resource, action in decisions(scenario)
    ]}


def validate_expected(expected, scenario):
    keys(expected, ("schema_version", "decisions"), "expected matrix")
    version(expected["schema_version"], "expected matrix")
    require(isinstance(expected["decisions"], list), "expected matrix.decisions: expected a list")
    complete = set(decisions(scenario))
    require(len(expected["decisions"]) == len(complete), "expected matrix: wrong decision count")
    seen = set()
    authority = {(row["identity"], row["resource"], row["action"]): row["allowed"]
                 for row in expected_from_rules(scenario)["decisions"]}
    for row in expected["decisions"]:
        keys(row, ("identity", "resource", "action", "allowed"), "expected decision")
        identifier(row["identity"], "expected decision.identity")
        identifier(row["resource"], "expected decision.resource")
        require(isinstance(row["action"], str) and row["action"] in ACTIONS,
                "expected decision: unknown action")
        require(type(row["allowed"]) is bool, "expected decision.allowed: must be a boolean")
        key = (row["identity"], row["resource"], row["action"])
        require(key in complete, "expected matrix: unknown identity/resource/action")
        require(key not in seen, "expected matrix: duplicate decision")
        require(row["allowed"] == authority[key], "expected matrix contradicts business rules")
        seen.add(key)
    require(seen == complete, "expected matrix: incomplete coverage")
    return expected


def permission_index(policy):
    return {(grant["role"], grant["resource"], action)
            for grant in policy["grants"] for action in grant["actions"]}


def allowed(scenario, policy, identity, resource, action):
    """Evaluate one decision after rejecting invalid scenario/policy/query input."""
    validate_scenario(scenario)
    validate_policy(policy, scenario)
    roles = {entry["id"]: entry["role"] for entry in scenario["identities"]}
    identifier(identity, "query.identity")
    identifier(resource, "query.resource")
    require(identity in roles, f"query: unknown identity {identity}")
    require(resource in {entry["id"] for entry in scenario["resources"]},
            f"query: unknown resource {resource}")
    require(isinstance(action, str) and action in ACTIONS, "query: unknown action")
    return (roles[identity], resource, action) in permission_index(policy)


def evaluated_rows(scenario, policy, expected):
    validate_scenario(scenario)
    validate_policy(policy, scenario)
    validate_expected(expected, scenario)
    roles = {entry["id"]: entry["role"] for entry in scenario["identities"]}
    permissions = permission_index(policy)
    return [dict(row, actual=(roles[row["identity"]], row["resource"], row["action"]) in permissions)
            for row in expected["decisions"]]


def check_policy(scenario, policy, expected):
    rows = evaluated_rows(scenario, policy, expected)
    mismatches = [row for row in rows if row["actual"] != row["allowed"]]
    required = rules_index(scenario)
    permissions = permission_index(policy)
    # A role still needs review when no current identity is assigned to it.
    role_mismatches = [
        {"role": role, "resource": resource, "action": action,
         "allowed": (role, resource, action) in required,
         "actual": (role, resource, action) in permissions}
        for role, resource, action in sorted(required ^ permissions)
    ]
    return {"command": "check", "passed": not mismatches and not role_mismatches, "total_decisions": len(rows),
            "allowed": sum(row["actual"] for row in rows),
            "denied": sum(not row["actual"] for row in rows),
            "required_allowed": sum(row["allowed"] and row["actual"] for row in rows),
            "missing_required": sum(row["allowed"] and not row["actual"] for row in rows),
            "excess_allowed": sum(not row["allowed"] and row["actual"] for row in rows),
            "mismatches": mismatches,
            "role_mismatches": role_mismatches,
            "role_missing_required": len(required - permissions),
            "role_excess_allowed": len(permissions - required)}


def review_policies(scenario, before, after, expected):
    old_rows = evaluated_rows(scenario, before, expected)
    new_rows = evaluated_rows(scenario, after, expected)
    pairs = list(zip(old_rows, new_rows))
    check = check_policy(scenario, after, expected)
    return {"command": "review", "passed": check["passed"],
            "total_decisions": len(pairs),
            "required_retained": sum(new["allowed"] and old["actual"] and new["actual"]
                                     for old, new in pairs),
            "required_restored": sum(new["allowed"] and not old["actual"] and new["actual"]
                                     for old, new in pairs),
            "required_removed": sum(new["allowed"] and old["actual"] and not new["actual"]
                                    for old, new in pairs),
            "unwanted_removed": sum(not new["allowed"] and old["actual"] and not new["actual"]
                                    for old, new in pairs),
            "unwanted_introduced": sum(not new["allowed"] and not old["actual"] and new["actual"]
                                       for old, new in pairs),
            "missing_required": check["missing_required"],
            "excess_allowed": check["excess_allowed"], "mismatches": check["mismatches"],
            "role_mismatches": check["role_mismatches"],
            "role_missing_required": check["role_missing_required"],
            "role_excess_allowed": check["role_excess_allowed"]}


def make_case(variant="guided", seed=17):
    require(variant in ("guided", "hints", "unfamiliar"), "unknown variant")
    require(type(seed) is int and 0 <= seed <= 2**32 - 1,
            "seed must be an integer between 0 and 4294967295")
    rng = random.Random(seed)
    names = [rng.choice(options) for options in (
        ("daily-reports", "published-reports", "weekly-reports"),
        ("incoming-orders", "supplier-uploads", "incoming-forms"),
        ("archive-snapshots", "retention-snapshots", "monthly-snapshots"),
        ("quarantined-items", "isolated-items", "held-items"),
    )]
    report, intake, archive, quarantine = names
    resource_purposes = (
        "Published reports used for business review.",
        "Incoming submissions that need to be recorded.",
        "Snapshots held for retention and later removal.",
        "Items held separately for manual handling.",
    )
    if variant == "unfamiliar":
        role_specs = [
            ("case-reviewer", "Inspect published reports and incoming submissions."),
            ("submitter", "Add incoming submissions without viewing existing submissions."),
            ("expiry-operator", "Inspect and remove expired snapshots; never create or replace them."),
            ("quarantine-manager", "Inspect, add, replace, and remove quarantined items."),
        ]
        rules = [
            ("case-reviewer", report, ["read"], "Read published reports to review a case."),
            ("case-reviewer", intake, ["read"], "Read incoming submissions to review a case."),
            ("submitter", intake, ["write"], "Record a new submission without reading stored submissions."),
            ("expiry-operator", archive, ["read", "delete"], "Inspect snapshots and remove expired ones."),
            ("quarantine-manager", quarantine, list(ACTIONS), "Manage the complete quarantine lifecycle."),
        ]
    else:
        names = names[:3]
        role_specs = [
            ("report-reader", "Read published reports."),
            ("intake-operator", "Read and record incoming uploads without deleting them."),
            ("archive-custodian", "Read reports and manage archive snapshots."),
        ]
        rules = [
            ("report-reader", report, ["read"], "Read the published reports for daily planning."),
            ("intake-operator", intake, ["read", "write"], "Inspect and record incoming uploads."),
            ("archive-custodian", report, ["read"], "Read reports to choose what to archive."),
            ("archive-custodian", archive, list(ACTIONS), "Inspect, create, replace, and remove archive snapshots."),
        ]
    people = rng.sample(("alex", "blair", "casey", "devon", "ellis", "frankie", "gray", "harper"), len(role_specs))
    rng.shuffle(rules)
    scenario = {"schema_version": 1, "title": "Harbour Lantern Supplies: fictional access review",
                "variant": variant, "seed": seed,
                "resources": [{"id": name, "purpose": purpose}
                              for name, purpose in zip(names, resource_purposes)],
                "roles": [{"id": role, "purpose": purpose} for role, purpose in role_specs],
                "identities": [{"id": person, "role": role}
                               for person, (role, _) in zip(people, role_specs)],
                "business_rules": [{"role": role, "resource": resource, "actions": actions,
                                    "reason": reason} for role, resource, actions, reason in rules]}
    validate_scenario(scenario)
    starting = {"schema_version": 1, "grants": [
        {"role": role, "resource": resource, "actions": list(ACTIONS)}
        for role, _ in role_specs for resource in names]}
    solution = {"schema_version": 1, "grants": [
        {"role": rule["role"], "resource": rule["resource"], "actions": list(rule["actions"])}
        for rule in scenario["business_rules"]]}
    expected = expected_from_rules(scenario)
    validate_policy(starting, scenario)
    validate_policy(solution, scenario)
    validate_expected(expected, scenario)
    return scenario, expected, starting, solution


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=True) + "\n"


def duplicate_safe_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"JSON contains duplicate key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise InputError(f"JSON contains nonstandard number: {value}")


def read_json(path):
    path = Path(path)
    require(path.stat().st_size <= MAX_INPUT_BYTES, f"{path}: input exceeds 2 MB limit")
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=duplicate_safe_object,
                          parse_constant=reject_constant)
    except (ValueError, RecursionError) as exc:
        raise InputError(f"{path}: {exc}") from exc


def generate(run, variant, seed):
    run = Path(run)
    scenario, expected, starting, solution = make_case(variant, seed)
    existing = [name for name in FILES if (run / name).exists()]
    require(not existing, f"refusing to overwrite {', '.join(existing)}; choose a new --run folder")
    run.mkdir(parents=True, exist_ok=True)
    outputs = {"scenario.json": scenario, "expected-access.json": expected,
               "starting-policy.json": starting, "practice-policy.json": starting,
               "solution-policy.json": solution}
    for name, value in outputs.items():
        with (run / name).open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json_text(value))
    instructions = {
        "guided": "Read each business rule. Remove unrelated grants and trim action lists. Keep required delete access.",
        "hints": "Make one list per role and store. Hint: do not assume every role needs delete.",
        "unfamiliar": "Build your own access table from the business rules before checking the answer key.",
    }
    with (run / "START-HERE.txt").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"Fictional offline practice: {variant}; seed {seed}.\n"
                     "Edit practice-policy.json. Keep scenario, expected matrix, and starting policy intact.\n"
                     f"{instructions[variant]}\n"
                     "Use lab.py check and lab.py review with --run pointing to this folder.\n"
                     "solution-policy.json is a supplied answer key. Independent practice is not assessed.\n")
    return {"command": "generate", "run": str(run.resolve()), "variant": variant, "seed": seed,
            "files": list(FILES), "expected_allowed": sum(row["allowed"] for row in expected["decisions"]),
            "expected_denied": sum(not row["allowed"] for row in expected["decisions"])}


def manifest_payload():
    paths = [ROOT / name for name in (".gitignore", "README.md", "lab.py", "test_lab.py")]
    fixture_dir = ROOT / "fixtures" / "worked-example"
    paths.extend(fixture_dir / name for name in FILES)
    return {
        "schema_version": 1,
        "origin": "Original fictional lab created as guided portfolio training materials.",
        "source_inputs": "Synthetic names, scenarios, permissions, and examples; no coursework or production data.",
        "authorship_scope": "Supplied scaffolding and answer keys; no claim of independent learner implementation.",
        "learner_status": "Independent practice and understanding have not been assessed.",
        "cloud_scope": "Offline toy allow-only model; no provider IAM implementation or deployed cloud environment.",
        "fixture_recipe": "python lab.py generate --variant guided --seed 17 --run fixtures/worked-example",
        "integrity_scope": "SHA-256 checks file integrity only, not factual acceptance or learner competence.",
        "sha256_files": {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in sorted(paths)},
    }


def manifest_command(write):
    expected = manifest_payload()
    path = ROOT / "PROVENANCE.json"
    if write:
        path.write_text(json_text(expected), encoding="utf-8", newline="\n")
        return {"command": "manifest", "passed": True, "operation": "write", "files": len(expected["sha256_files"])}
    actual = read_json(path)
    require(isinstance(actual, dict), "manifest must be an object")
    changed = [name for name, digest in expected["sha256_files"].items()
               if not isinstance(actual.get("sha256_files"), dict)
               or actual["sha256_files"].get(name) != digest]
    return {"command": "manifest", "passed": actual == expected, "operation": "verify",
            "files": len(expected["sha256_files"]), "changed_files": changed,
            "metadata_matches": {key: value for key, value in actual.items() if key != "sha256_files"}
            == {key: value for key, value in expected.items() if key != "sha256_files"}}


def render(result, as_json):
    if as_json:
        print(json_text(result), end="")
        return
    print(f"{result['command']}: " + ("PASS" if result.get("passed", True) else "NEEDS CHANGES"))
    for key, value in result.items():
        if key not in ("command", "passed", "mismatches"):
            print(f"  {key}: {value}")
    for row in result.get("mismatches", []):
        expected = "allow" if row["allowed"] else "deny"
        actual = "allow" if row["actual"] else "deny"
        print(f"  {row['identity']} / {row['resource']} / {row['action']}: expected {expected}, got {actual}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "check", "review"):
        command = commands.add_parser(name)
        command.add_argument("--run", type=Path, default=ROOT / "run")
        command.add_argument("--json", action="store_true", help="print a JSON result")
        if name == "generate":
            command.add_argument("--variant", choices=("guided", "hints", "unfamiliar"), default="guided")
            command.add_argument("--seed", type=int, default=17)
        if name == "check":
            command.add_argument("--policy", type=Path)
        if name == "review":
            command.add_argument("--before", type=Path)
            command.add_argument("--after", type=Path)
    manifest = commands.add_parser("manifest")
    mode = manifest.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--verify", action="store_true")
    manifest.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            result = generate(args.run, args.variant, args.seed)
        elif args.command == "manifest":
            result = manifest_command(args.write)
        else:
            scenario = validate_scenario(read_json(args.run / "scenario.json"))
            expected = validate_expected(read_json(args.run / "expected-access.json"), scenario)
            if args.command == "check":
                policy = read_json(args.policy or args.run / "practice-policy.json")
                result = check_policy(scenario, policy, expected)
            else:
                before = read_json(args.before or args.run / "starting-policy.json")
                after = read_json(args.after or args.run / "practice-policy.json")
                result = review_policies(scenario, before, after, expected)
        render(result, args.json)
        return 0 if result.get("passed", True) else 1
    except (InputError, OSError, UnicodeError) as exc:
        if args.json:
            print(json_text({"command": args.command, "error": str(exc)}), file=sys.stderr, end="")
        else:
            print(f"Input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
