"""Offline ordered packet-filter lab. Read README.md for the exact model."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import random
import re
import sys


ROOT = Path(__file__).resolve().parent
CASES = ("shadowed-deny", "narrow-service", "missing-access", "protocol-mix")
RESERVED = tuple(ipaddress.IPv4Network(value) for value in
                 ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
ID = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
MAX_BYTES = 1_000_000
FIELDS = ("protocol", "source", "destination", "source_port", "destination_port")


class InputError(ValueError):
    """Invalid data is an error, never an implicit deny."""


def require(condition, message):
    if not condition:
        raise InputError(message)


def keys(value, fields, where):
    require(isinstance(value, dict), f"{where}: expected an object")
    require(set(value) == set(fields), f"{where}: expected fields {', '.join(fields)}")


def version(value):
    require(type(value) is int and value == 1, "schema_version must be integer 1")


def identifier(value, where):
    require(isinstance(value, str) and ID.fullmatch(value) is not None,
            f"{where}: expected a lowercase ID of 1-64 characters")


def text_value(value, where):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 1500,
            f"{where}: expected nonempty text of at most 1500 characters")


def sequence(value, where, *, maximum=256, empty=False):
    require(isinstance(value, list), f"{where}: expected a list")
    require((empty or bool(value)) and len(value) <= maximum,
            f"{where}: expected {'0' if empty else '1'}-{maximum} entries")


def network(value, where, *, exact=False):
    require(isinstance(value, str), f"{where}: expected an IPv4 string")
    require(not exact or "/" not in value, f"{where}: a packet needs an exact address")
    try:
        parsed = ipaddress.IPv4Network(value, strict=True)
    except (ValueError, TypeError) as exc:
        raise InputError(f"{where}: expected an exact IPv4 address or canonical CIDR") from exc
    canonical = str(parsed) if "/" in value else str(parsed.network_address)
    require(value == canonical, f"{where}: use canonical dotted IPv4 or prefix-length CIDR")
    require(any(parsed.subnet_of(block) for block in RESERVED),
            f"{where}: must stay inside one documentation-only TEST-NET /24")
    return parsed


def port(value, where, *, wildcard=False):
    require((wildcard and value == "*") or (type(value) is int and 1 <= value <= 65535),
            f"{where}: expected port 1-65535" + (' or "*"' if wildcard else ""))


def traffic(value, where, *, rule=False):
    require(isinstance(value["protocol"], str) and value["protocol"] in ("tcp", "udp"),
            f"{where}.protocol: expected tcp or udp")
    for field in ("source", "destination"):
        network(value[field], f"{where}.{field}", exact=not rule)
    for field in ("source_port", "destination_port"):
        port(value[field], f"{where}.{field}", wildcard=rule)


def validate_policy(policy):
    keys(policy, ("schema_version", "rules"), "policy")
    version(policy["schema_version"])
    sequence(policy["rules"], "policy.rules", maximum=64, empty=True)
    seen = set()
    for index, rule in enumerate(policy["rules"], 1):
        where = f"rule {index}"
        keys(rule, ("id", "action", *FIELDS), where)
        identifier(rule["id"], f"{where}.id")
        require(rule["id"] not in seen, f"{where}: duplicate rule ID")
        seen.add(rule["id"])
        require(isinstance(rule["action"], str) and rule["action"] in ("allow", "deny"),
                f"{where}.action: expected allow or deny")
        traffic(rule, where, rule=True)
    return policy


def validate_packets(packet_file):
    keys(packet_file, ("schema_version", "packets"), "packet file")
    version(packet_file["schema_version"])
    sequence(packet_file["packets"], "packets")
    seen = set()
    for packet in packet_file["packets"]:
        keys(packet, ("id", *FIELDS), "packet")
        identifier(packet["id"], "packet.id")
        require(packet["id"] not in seen, "packets: duplicate ID")
        seen.add(packet["id"])
        traffic(packet, f"packet {packet['id']}")
    return packet_file


def validate_scenario(scenario):
    keys(scenario, ("schema_version", "case", "seed", "requirements", "probes"), "scenario")
    version(scenario["schema_version"])
    require(isinstance(scenario["case"], str) and scenario["case"] in CASES,
            "scenario.case: unknown case")
    require(type(scenario["seed"]) is int and 0 <= scenario["seed"] <= 2**32 - 1,
            "scenario.seed: expected integer 0-4294967295")
    sequence(scenario["requirements"], "requirements", maximum=12)
    for value in scenario["requirements"]:
        text_value(value, "requirement")
    sequence(scenario["probes"], "probes")
    packet_rows = []
    tuples = set()
    for probe in scenario["probes"]:
        keys(probe, ("id", *FIELDS, "expected", "reason"), "probe")
        require(isinstance(probe["expected"], str) and probe["expected"] in ("allow", "deny"),
                "probe.expected: expected allow or deny")
        text_value(probe["reason"], "probe.reason")
        packet_rows.append({field: probe[field] for field in ("id", *FIELDS)})
    validate_packets({"schema_version": 1, "packets": packet_rows})
    for packet in packet_rows:
        signature = tuple(packet[field] for field in FIELDS)
        require(signature not in tuples, "probes: duplicate traffic tuple")
        tuples.add(signature)
    require(any(probe["expected"] == "allow" for probe in scenario["probes"]),
            "scenario must include legitimate traffic")
    require(any(probe["expected"] == "deny" for probe in scenario["probes"]),
            "scenario must include unwanted traffic")
    return scenario


def _decide_validated(policy, packet):
    """First matching rule wins; caller has already validated every input row."""
    for position, rule in enumerate(policy["rules"], 1):
        if rule["protocol"] != packet["protocol"]:
            continue
        if any(ipaddress.IPv4Address(packet[field]) not in ipaddress.IPv4Network(rule[field])
               for field in ("source", "destination")):
            continue
        if any(rule[field] != "*" and rule[field] != packet[field]
               for field in ("source_port", "destination_port")):
            continue
        return {"action": rule["action"], "rule_id": rule["id"], "position": position}
    return {"action": "deny", "rule_id": None, "position": None}


def evaluate(policy, packet_file):
    validate_policy(policy)
    validate_packets(packet_file)
    return [{"id": packet["id"], **_decide_validated(policy, packet)}
            for packet in packet_file["packets"]]


def check(policy, scenario):
    validate_policy(policy)
    validate_scenario(scenario)
    rows = []
    for probe in scenario["probes"]:
        result = _decide_validated(policy, probe)
        rows.append({"id": probe["id"], "expected": probe["expected"],
                     **result, "matches": result["action"] == probe["expected"],
                     "reason": probe["reason"]})
    missing = [row["id"] for row in rows if not row["matches"] and row["expected"] == "allow"]
    excess = [row["id"] for row in rows if not row["matches"] and row["expected"] == "deny"]
    return {"passed": not missing and not excess, "checked": len(rows),
            "legitimate_preserved": sum(row["matches"] and row["expected"] == "allow" for row in rows),
            "missing_access": missing, "excess_access": excess, "decisions": rows}


def rule(rule_id, action, protocol, source, destination, destination_port, source_port="*"):
    return {"id": rule_id, "action": action, "protocol": protocol, "source": source,
            "destination": destination, "source_port": source_port,
            "destination_port": destination_port}


def make_case(case="shadowed-deny", seed=17):
    require(case in CASES, "unknown case")
    require(type(seed) is int and 0 <= seed <= 2**32 - 1, "seed must be integer 0-4294967295")
    rng = random.Random(seed)
    client, admin, exporter, backup = [f"192.0.2.{n}" for n in rng.sample(range(10, 81), 4)]
    blocked = f"192.0.2.{rng.randint(150, 220)}"
    portal, manager, telemetry, archive = [f"198.51.100.{n}" for n in rng.sample(range(10, 81), 4)]
    client_net, service_net = "192.0.2.0/24", "198.51.100.0/24"
    requirements = [
        f"Permit TCP from {client_net} to portal {portal} destination port 443, except the restricted host below. Source ports may vary.",
        f"Permit TCP from admin workstation {admin} only to management host {manager} destination port 22. Source ports may vary.",
        f"Permit UDP from exporter {exporter} only to telemetry host {telemetry} destination port 5514. Source ports may vary. TCP to this service is not required in this fictional case.",
        f"Deny all TCP and UDP from restricted host {blocked}, including portal traffic. All other traffic is denied unless a requirement explicitly allows it.",
    ]
    answer_rules = [
        rule("restricted-tcp", "deny", "tcp", blocked, service_net, "*"),
        rule("restricted-udp", "deny", "udp", blocked, service_net, "*"),
        rule("portal", "allow", "tcp", client_net, portal, 443),
        rule("management", "allow", "tcp", admin, manager, 22),
        rule("telemetry", "allow", "udp", exporter, telemetry, 5514),
    ]
    if case == "missing-access":
        requirements.append(f"Permit TCP from backup sender {backup} only to archive {archive} destination port 8443. Source ports may vary.")
        answer_rules.append(rule("archive", "allow", "tcp", backup, archive, 8443))
    probes = []

    def probe(name, protocol, source, destination, destination_port, expected, reason, source_port=49152):
        probes.append({"id": name, "protocol": protocol, "source": source,
                       "destination": destination, "source_port": source_port,
                       "destination_port": destination_port, "expected": expected, "reason": reason})

    probe("portal-client", "tcp", client, portal, 443, "allow", "Ordinary client needs the portal.")
    probe("portal-new-source-port", "tcp", client, portal, 443, "allow", "A source port change must not break the portal.", 65535)
    probe("portal-admin", "tcp", admin, portal, 443, "allow", "Admin remains a client for portal access.", 1)
    probe("portal-near-low-edge", "tcp", "192.0.2.1", portal, 443, "allow", "The requirement covers the client subnet, not just a named sample client.")
    probe("portal-near-high-edge", "tcp", "192.0.2.254", portal, 443, "allow", "Do not accidentally reduce the client subnet to its lower half.")
    probe("restricted-portal", "tcp", blocked, portal, 443, "deny", "The restricted host is inside the broad client subnet.")
    probe("management-admin", "tcp", admin, manager, 22, "allow", "Keep the administrator's stated management access.")
    probe("management-client", "tcp", client, manager, 22, "deny", "Portal clients do not automatically need management access.")
    probe("management-wrong-port", "tcp", admin, manager, 23, "deny", "The management requirement is destination port 22 only.")
    probe("management-udp", "udp", admin, manager, 22, "deny", "TCP permission does not grant UDP at the same number.")
    probe("portal-wrong-destination", "tcp", client, manager, 443, "deny", "The portal permission names one destination, not every server.")
    probe("portal-wrong-port", "tcp", client, portal, 80, "deny", "Port 80 has no stated need.")
    probe("portal-udp", "udp", client, portal, 443, "deny", "Only TCP portal traffic is required by this case.")
    probe("external-source", "tcp", "203.0.113.8", portal, 443, "deny", "A source outside the client subnet has no stated need.")
    probe("external-destination", "tcp", client, "203.0.113.9", 443, "deny", "An unrelated destination has no stated need.")
    probe("telemetry-udp", "udp", exporter, telemetry, 5514, "allow", "The exporter uses the specified UDP telemetry transport.")
    probe("telemetry-new-source-port", "udp", exporter, telemetry, 5514, "allow", "Source ports can vary independently of the destination port.", 32768)
    probe("telemetry-tcp", "tcp", exporter, telemetry, 5514, "deny", "Matching port numbers do not make TCP and UDP interchangeable.")
    probe("telemetry-wrong-source", "udp", client, telemetry, 5514, "deny", "Only the exporter needs telemetry access.")
    probe("telemetry-source-port-trap", "udp", exporter, telemetry, 5515, "deny", "A matching source port does not substitute for the required destination port.", 5514)
    probe("restricted-telemetry", "udp", blocked, telemetry, 5514, "deny", "The restricted host may not send telemetry either.")
    probe("reverse-direction", "tcp", portal, client, 49152, "deny", "This stateless one-way model has no implicit return-traffic permission.", 443)
    if case == "missing-access":
        probe("archive-backup", "tcp", backup, archive, 8443, "allow", "The new backup requirement must be added without opening it to everyone.")
        probe("archive-client", "tcp", client, archive, 8443, "deny", "The archive allowance is restricted to the named backup sender.")
        probe("archive-udp", "udp", backup, archive, 8443, "deny", "The backup requirement specifies TCP.")
    starting = json.loads(json.dumps(answer_rules))
    if case == "shadowed-deny":
        starting.insert(0, starting.pop(2))
    elif case == "narrow-service":
        starting[2]["destination"] = service_net
        starting[2]["destination_port"] = "*"
    elif case == "missing-access":
        starting.pop()
    elif case == "protocol-mix":
        starting[4]["protocol"] = "tcp"
    scenario = {"schema_version": 1, "case": case, "seed": seed,
                "requirements": requirements, "probes": probes}
    before = {"schema_version": 1, "rules": starting}
    solution = {"schema_version": 1, "rules": answer_rules}
    validate_scenario(scenario)
    validate_policy(before)
    validate_policy(solution)
    return scenario, before, solution


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def write_case(destination, case, seed):
    """Create files exclusively in a fresh or empty directory; never replace notes."""
    require(not destination.is_symlink(), "run destination must not be a symlink")
    require(not destination.exists() or (destination.is_dir() and not any(destination.iterdir())),
            "run destination must be absent or empty; choose a new folder to preserve notes")
    scenario, starting, solution = make_case(case, seed)
    destination.mkdir(parents=True, exist_ok=True)
    packet_file = {"schema_version": 1, "packets": [
        {field: row[field] for field in ("id", *FIELDS)} for row in scenario["probes"]]}
    contents = {"scenario.json": scenario, "starting-policy.json": starting,
                "practice-policy.json": starting, "solution-policy.json": solution,
                "packets.json": packet_file}
    for name, value in contents.items():
        with (destination / name).open("xb") as stream:
            stream.write(encode(value))
    instructions = (
        f"Fictional offline firewall case: {case}; seed {seed}.\n"
        "1. Read scenario.json requirements. Predict which probes the starting policy gets wrong.\n"
        "2. Edit only practice-policy.json. Use rule order, exact hosts/CIDRs and transport/port evidence.\n"
        "3. Run lab.py check with --run pointing at this folder. Explain missing and excess access.\n"
        "4. Try an extra packet with evaluate. Explain what the supplied probes cannot prove.\n"
        "The solution-policy.json file is a supplied answer key, not independent learner evidence.\n"
    )
    with (destination / "START-HERE.txt").open("xb") as stream:
        stream.write(instructions.encode("utf-8"))
    return {"created": str(destination), "case": case, "seed": seed, "files": len(contents) + 1}


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"JSON: duplicate key {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise InputError(f"JSON: unsupported constant {value}")


def read_json(path):
    try:
        require(path.stat().st_size <= MAX_BYTES, f"{path}: input exceeds {MAX_BYTES} bytes")
        return json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=reject_duplicates,
                          parse_constant=reject_constant)
    except InputError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError(f"{path}: invalid UTF-8 JSON: {exc}") from exc


def inventory():
    paths = [ROOT / name for name in ("lab.py", "test_lab.py", "README.md", ".gitignore", ".gitattributes")]
    paths += sorted((ROOT / "fixtures").rglob("*"))
    return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths if path.is_file()}


def manifest(write=False):
    path = ROOT / "PROVENANCE.json"
    current = inventory()
    if write:
        value = {"schema_version": 1,
                 "origin": "Standalone fictional exercise created in October 2026; packets and policies are synthetic, not a capture, production policy, or coursework excerpt.",
                 "scope": "SHA-256 checks file identity only; it does not establish global novelty, policy security, or learner competence.",
                 "fixtures": [{"case": case, "seed": 17} for case in CASES], "sha256": current}
        path.write_bytes(encode(value))
        return {"written": str(path), "files": len(current)}
    value = read_json(path)
    keys(value, ("schema_version", "origin", "scope", "fixtures", "sha256"), "provenance")
    version(value["schema_version"])
    text_value(value["origin"], "provenance.origin")
    text_value(value["scope"], "provenance.scope")
    require(value["fixtures"] == [{"case": case, "seed": 17} for case in CASES],
            "provenance: unexpected fixture recipes")
    require(isinstance(value["sha256"], dict) and bool(value["sha256"]), "provenance.sha256: expected nonempty object")
    require(all(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest)
                for digest in value["sha256"].values()), "provenance: invalid SHA-256")
    differences = sorted(name for name in current.keys() | value["sha256"].keys()
                         if current.get(name) != value["sha256"].get(name))
    return {"passed": not differences, "files": len(current), "differences": differences}


def run_path(value):
    return Path(value).absolute()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    generate = sub.add_parser("generate", help="create a fresh practice case; refuse nonempty folders")
    generate.add_argument("--case", choices=CASES, default=CASES[0])
    generate.add_argument("--seed", type=int, default=17)
    generate.add_argument("--run", type=run_path, default=ROOT / "run")
    check_parser = sub.add_parser("check", help="compare the policy with all scenario probes")
    check_parser.add_argument("--run", type=run_path, default=ROOT / "run")
    check_parser.add_argument("--policy", type=run_path)
    evaluation = sub.add_parser("evaluate", help="report first matching rules for a packet JSON file")
    evaluation.add_argument("--policy", type=run_path, required=True)
    evaluation.add_argument("--packets", type=run_path, required=True)
    provenance = sub.add_parser("manifest", help="verify hashes or deliberately refresh them after review")
    mode = provenance.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--write", action="store_true")
    for command in (generate, check_parser, evaluation, provenance):
        command.add_argument("--json", action="store_true", help="print structured output")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            require(not args.run.resolve().is_relative_to((ROOT / "fixtures").resolve()),
                    "generate cannot write inside reference fixtures")
            result = write_case(args.run, args.case, args.seed)
        elif args.command == "check":
            result = check(read_json(args.policy or args.run / "practice-policy.json"),
                           read_json(args.run / "scenario.json"))
        elif args.command == "evaluate":
            result = {"decisions": evaluate(read_json(args.policy), read_json(args.packets))}
        else:
            result = manifest(args.write)
        if args.json:
            print(json.dumps(result, indent=2, allow_nan=False))
        elif args.command in ("check", "evaluate"):
            for row in result["decisions"]:
                matched = f"rule {row['position']} ({row['rule_id']})" if row["rule_id"] else "default deny"
                expected = f"; expected {row['expected']}" if "expected" in row else ""
                print(f"{row['id']}: {row['action']} via {matched}{expected}")
            if args.command == "check":
                print(f"{result['checked']} probes; {result['legitimate_preserved']} legitimate probes preserved; "
                      f"{len(result['missing_access'])} missing; {len(result['excess_access'])} excess")
                print("PASS: supplied probes match." if result["passed"] else "FAIL: revise the policy using the stated requirements.")
        else:
            print(json.dumps(result, indent=2))
        return 0 if result.get("passed", True) else 1
    except (InputError, OSError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
