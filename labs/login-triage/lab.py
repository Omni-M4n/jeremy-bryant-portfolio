#!/usr/bin/env python3
"""Offline synthetic login practice. Read README.md for the command contract."""

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
import ipaddress
import json
from pathlib import Path
import random
import sys
import unittest


# Keep imported local test modules from creating bytecode beside the source.
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
VERSION = "1.0.0"
FIELDS = ("event_id", "timestamp", "user", "source_ip", "outcome", "reason", "synthetic")
NETWORKS = tuple(ipaddress.ip_network(value) for value in
                 ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
SCENARIOS = ("baseline", "late-success", "distributed")
DEFAULTS = {"threshold": 5, "window_seconds": 300, "success_seconds": 120}


def json_text(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stamp(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value):
    # One explicit UTC format avoids ambiguous local times and mixed offsets.
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as error:
        raise ValueError("timestamp must be a real UTC time in YYYY-MM-DDTHH:MM:SSZ form") from error
    if stamp(parsed) != value:
        raise ValueError("timestamp must use zero-padded UTC fields")
    return parsed


def validate_events(rows):
    if not rows:
        raise ValueError("input contains no events")
    seen = set()
    clean = []
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"event {number}: expected exactly these fields: {', '.join(FIELDS)}")
        if any(not isinstance(row[field], str) or not row[field] for field in FIELDS):
            raise ValueError(f"event {number}: all fields must be nonempty strings")
        if row["synthetic"] != "true":
            raise ValueError(f"event {number}: synthetic must be the string 'true'")
        if not row["event_id"].startswith("SYN-") or row["event_id"] in seen:
            raise ValueError(f"event {number}: event_id must start SYN- and be unique")
        seen.add(row["event_id"])
        if not row["user"].startswith("practice-"):
            raise ValueError(f"event {number}: user must start practice-")
        parse_time(row["timestamp"])
        try:
            address = ipaddress.ip_address(row["source_ip"])
        except ValueError as error:
            raise ValueError(f"event {number}: invalid source_ip") from error
        if not any(address in network for network in NETWORKS):
            raise ValueError(f"event {number}: source_ip must be in an IPv4 documentation range")
        if row["outcome"] not in ("failure", "success"):
            raise ValueError(f"event {number}: outcome must be failure or success")
        expected_reason = "invalid_password" if row["outcome"] == "failure" else "accepted"
        if row["reason"] != expected_reason:
            raise ValueError(f"event {number}: reason does not match outcome")
        clean.append(dict(row))
    return sorted(clean, key=lambda row: (row["timestamp"], row["event_id"]))


def unique_fields(pairs):
    """Reject ambiguous evidence instead of silently keeping the last value."""
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError(f"Duplicate JSON field: {key}")
        record[key] = value
    return record


def load_events(path):
    path = Path(path)
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(FIELDS):
                raise ValueError("CSV header must match the documented field order")
            rows = list(reader)
    elif path.suffix.lower() == ".jsonl":
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip():
                    raise ValueError(f"JSONL line {number}: blank lines are not events")
                rows.append(json.loads(line, object_pairs_hook=unique_fields))
    else:
        raise ValueError("input must be a .csv or .jsonl file")
    return validate_events(rows)


def validate_settings(threshold, window_seconds, success_seconds):
    for name, value, lower, upper in (
        ("threshold", threshold, 1, 10000),
        ("window_seconds", window_seconds, 1, 86400),
        ("success_seconds", success_seconds, 0, 86400),
    ):
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f"{name} must be a whole number from {lower} to {upper}")


def analyze(rows, threshold=5, window_seconds=300, success_seconds=120):
    validate_settings(threshold, window_seconds, success_seconds)
    events = validate_events(rows)
    groups = {}
    for event in events:
        groups.setdefault((event["user"], event["source_ip"]), []).append(event)
    candidates = []
    for (user, source_ip), group in sorted(groups.items()):
        failures = []
        successes = [event for event in group if event["outcome"] == "success"]
        failure_events = [event for event in group if event["outcome"] == "failure"]
        for index, event in enumerate(failure_events):
            end = parse_time(event["timestamp"])
            start = end - timedelta(seconds=window_seconds)
            failures = [previous for previous in failures if parse_time(previous["timestamp"]) >= start]
            failures.append(event)
            # Same-second records have no reliable internal time order.
            if index + 1 < len(failure_events) and failure_events[index + 1]["timestamp"] == event["timestamp"]:
                continue
            if len(failures) < threshold:
                continue
            linked = []
            for success in successes:
                delay = int((parse_time(success["timestamp"]) - end).total_seconds())
                # Strictly later only: a shared second does not prove event order.
                if 0 < delay <= success_seconds:
                    linked.append({"event_id": success["event_id"], "timestamp": success["timestamp"],
                                   "seconds_after_window_end": delay})
            candidates.append({
                "candidate_id": "window-ending-" + event["event_id"],
                "user": user, "source_ip": source_ip,
                "window_start_inclusive": stamp(start), "window_end_inclusive": stamp(end),
                "first_failure": failures[0]["timestamp"], "failure_count": len(failures),
                "failure_event_ids": [failure["event_id"] for failure in failures],
                "linked_successes": linked,
            })
    candidates.sort(key=lambda value: (value["window_end_inclusive"], value["candidate_id"]))
    pairs = {(value["user"], value["source_ip"]) for value in candidates}
    return {
        "schema_version": 1, "synthetic": True, "generator_version": VERSION,
        "settings": {"threshold": threshold, "window_seconds": window_seconds, "success_seconds": success_seconds},
        "event_count": len(events),
        "timeline_start": events[0]["timestamp"], "timeline_end": events[-1]["timestamp"],
        "candidate_window_count": len(candidates), "candidate_pair_count": len(pairs),
        "candidates": candidates,
        "interpretation": "Training heuristic only. Overlapping windows may describe one sequence. A later success is a timing link, not proof of a shared actor or compromise.",
    }


def make_report(path, **settings):
    report = analyze(load_events(path), **settings)
    report["input_sha256"] = digest(Path(path).read_bytes())
    return report


def make_case(seed, scenario):
    if type(seed) is not int or not 0 <= seed <= 2147483647:
        raise ValueError("seed must be a whole number from 0 to 2147483647")
    if scenario not in SCENARIOS:
        raise ValueError("unknown scenario")
    rng = random.Random(seed)
    base = datetime(2032, 4, 6, 9, tzinfo=timezone.utc) + timedelta(days=seed % 20, minutes=rng.randrange(40))
    suffix = f"{seed % 1000:03d}"
    staff = "practice-staff-" + suffix
    editor = "practice-editor-" + suffix
    service = "practice-sync-" + suffix
    staff_ip = f"192.0.2.{rng.randrange(10, 80)}"
    alternate_ips = [staff_ip, f"192.0.2.{rng.randrange(90, 160)}", f"192.0.2.{rng.randrange(170, 240)}"]
    editor_ip = f"198.51.100.{rng.randrange(10, 240)}"
    service_ip = f"203.0.113.{rng.randrange(10, 240)}"
    rows = []

    def event(seconds, user, address, outcome):
        rows.append({"event_id": f"SYN-{len(rows) + 1:04d}",
                     "timestamp": stamp(base + timedelta(seconds=seconds)),
                     "user": user, "source_ip": address, "outcome": outcome,
                     "reason": "invalid_password" if outcome == "failure" else "accepted", "synthetic": "true"})

    for index, seconds in enumerate((0, 40, 80, 120, 160, 200)):
        address = alternate_ips[index % 3] if scenario == "distributed" else staff_ip
        event(seconds, staff, address, "failure")
    event(680 if scenario == "late-success" else 260, staff, staff_ip, "success")
    for seconds, outcome in ((70, "failure"), (95, "failure"), (130, "success")):
        event(seconds, editor, editor_ip, outcome)
    for index in range(6):
        event(30 + index * 660, service, service_ip, "failure")
    for seconds in (1000, 1800, 2400):
        event(seconds, editor, editor_ip, "success")
    rng.shuffle(rows)
    context = {
        "synthetic": True, "seed": seed, "scenario": scenario,
        "time_basis": "Invented UTC timestamps in 2032; no relationship to real activity.",
        "organization": "Fictional Cedar Practice Co-op",
        "accounts": [
            {"user": staff, "role": "Fictional human staff account", "note": "No user confirmation or device evidence is supplied for this account."},
            {"user": editor, "role": "Fictional human editor account", "note": "Invented helpdesk note: the editor reported two typing errors before signing in. This is contextual evidence, not independent identity verification."},
            {"user": service, "role": "Fictional automated file-sync account", "note": "Invented change note: its saved password was not updated after a planned password change. The job retries every 11 minutes. No repair is performed in this lab."},
        ],
        "address_note": "All source addresses use IPv4 documentation ranges. An address is a log label, not a verified person or device. Shared internet connections can reuse one source address.",
        "coverage": "Only these invented sign-in records and notes are available. No device logs, multi-factor records, session actions or independent user verification are supplied.",
    }
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    files = {
        "auth.csv": buffer.getvalue().encode("utf-8"),
        "auth.jsonl": ("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n").encode("utf-8"),
        "context.json": json_text(context).encode("utf-8"),
    }
    manifest = {
        "schema_version": 1, "synthetic": True, "seed": seed, "scenario": scenario,
        "generator": "lab.py", "generator_version": VERSION, "event_count": len(rows),
        "provenance": "Original fictional training records produced from a numeric seed. No external logs, coursework, personal records or live systems are inputs.",
        "sha256": {name: digest(data) for name, data in files.items()},
    }
    files["manifest.json"] = json_text(manifest).encode("utf-8")
    return files


def writable_path(value):
    # Outputs are deliberately confined to this lab's ignored practice directory.
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if RUNS.resolve() not in path.parents:
        raise ValueError("output must be a child of this lab's runs directory")
    if RUNS.is_symlink() or RUNS.resolve() != ROOT / "runs":
        raise ValueError("runs must be a real directory inside this lab")
    if path.exists():
        raise ValueError("output already exists; choose a new name to preserve earlier practice")
    return path


def save_case(path, files):
    path.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        (path / name).write_bytes(data)


def verify_case(path, report_path=None):
    path = Path(path)
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("synthetic") is not True or manifest.get("schema_version") != 1:
        raise ValueError("manifest must identify a version 1 synthetic case")
    expected = make_case(manifest.get("seed"), manifest.get("scenario"))
    # Check against regeneration, so editing both a data file and its hash is insufficient.
    for name, data in expected.items():
        if (path / name).read_bytes() != data:
            raise ValueError(f"case mismatch: {name} differs from seeded regeneration")
    csv_events = load_events(path / "auth.csv")
    if csv_events != load_events(path / "auth.jsonl"):
        raise ValueError("CSV and JSONL event sets differ")
    result = {"case": "PASS", "events": len(csv_events), "files_verified": len(expected),
              "scope": "Seeded file integrity and report calculation only; not learner assessment or proof of security."}
    if report_path is not None:
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
        settings = report.get("settings")
        if not isinstance(settings, dict) or set(settings) != set(DEFAULTS):
            raise ValueError("report settings are missing or unexpected")
        matching = [path / name for name in ("auth.csv", "auth.jsonl")
                    if digest((path / name).read_bytes()) == report.get("input_sha256")]
        if not matching or make_report(matching[0], **settings) != report:
            raise ValueError("report does not match recalculation for this case and its settings")
        result["report"] = "PASS"
        result["candidate_windows"] = report["candidate_window_count"]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline, synthetic login-triage practice. Read README.md first.")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="write a seeded practice case under runs/")
    generate.add_argument("--seed", type=int, default=41)
    generate.add_argument("--scenario", choices=SCENARIOS, default="baseline")
    generate.add_argument("--output", help="new directory under runs/; default runs/seed-SEED-SCENARIO")
    timeline = commands.add_parser("timeline", help="sort events by time and optionally filter exact field values")
    timeline.add_argument("--input", type=Path, default=ROOT / "fixture" / "auth.csv")
    timeline.add_argument("--user")
    timeline.add_argument("--source-ip")
    timeline.add_argument("--outcome", choices=("failure", "success"))
    triage = commands.add_parser("triage", help="report qualifying failure windows and timing-linked successes")
    triage.add_argument("--input", type=Path, default=ROOT / "fixture" / "auth.csv")
    triage.add_argument("--threshold", type=int, default=5, help="minimum failures for one account/address pair (default 5)")
    triage.add_argument("--window-seconds", type=int, default=300, help="inclusive failure window (default 300)")
    triage.add_argument("--success-seconds", type=int, default=120, help="link strictly later successes up to this delay; 0 disables links")
    triage.add_argument("--output", default="runs/report.json", help="new report file under runs/")
    verify = commands.add_parser("verify", help="verify seeded files and optionally recalculate a report")
    verify.add_argument("--case", type=Path, default=ROOT / "fixture")
    verify.add_argument("--report", type=Path)
    commands.add_parser("test", help="run boundary, input and fixture checks using the standard library")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            files = make_case(args.seed, args.scenario)
            destination = writable_path(args.output or f"runs/seed-{args.seed}-{args.scenario}")
            save_case(destination, files)
            print(f"PASS generated 19 synthetic events: {destination}")
        elif args.command == "timeline":
            events = load_events(args.input)
            selected = [event for event in events
                        if (args.user is None or event["user"] == args.user)
                        and (args.source_ip is None or event["source_ip"] == args.source_ip)
                        and (args.outcome is None or event["outcome"] == args.outcome)]
            print("event_id | timestamp (UTC) | user | source_ip | outcome")
            for event in selected:
                print(" | ".join(event[field] for field in ("event_id", "timestamp", "user", "source_ip", "outcome")))
            print(f"{len(selected)} of {len(events)} synthetic events selected")
        elif args.command == "triage":
            report = make_report(args.input, threshold=args.threshold,
                                 window_seconds=args.window_seconds, success_seconds=args.success_seconds)
            destination = writable_path(args.output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(json_text(report))
            print(f"PASS read {report['event_count']} events; {report['candidate_window_count']} qualifying windows across {report['candidate_pair_count']} account/address pairs")
            print("Training heuristic only; overlapping windows are not separate proven incidents.")
            print(f"Report: {destination}")
        elif args.command == "verify":
            print(json_text(verify_case(args.case, args.report)), end="")
        else:
            RUNS.mkdir(exist_ok=True)
            suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_lab.py")
            return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
