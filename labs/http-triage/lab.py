#!/usr/bin/env python3
"""Offline synthetic HTTP access-log practice. Read README.md for the contract."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
import ipaddress
import json
from pathlib import Path
import random
import re
import sys
import unittest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
VERSION = "1.0.0"
SCENARIOS = ("mixed", "soft-200", "logging-gap", "crawler-only")
FIELDS = ("event_id", "timestamp", "source_ip", "host", "method", "target",
          "status", "body_bytes", "user_agent", "synthetic")
NETWORKS = tuple(ipaddress.ip_network(value) for value in
                 ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
WATCH_PATHS = ("/.env", "/admin", "/backup.zip", "/debug")
DEFAULTS = {"volume_threshold": 8, "path_threshold": 3}


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stamp(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value):
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as error:
        raise ValueError("timestamps must be real UTC times in YYYY-MM-DDTHH:MM:SSZ form") from error
    if stamp(parsed) != value:
        raise ValueError("timestamps must use zero-padded UTC fields")
    return parsed


def validate_events(rows):
    if not rows:
        raise ValueError("input contains no events")
    clean, seen = [], set()
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"event {number}: fields must match the documented CSV schema")
        if any(not isinstance(row[field], str) or not row[field] for field in FIELDS):
            raise ValueError(f"event {number}: every field must be a nonempty string")
        if any(any(ord(char) < 32 or ord(char) > 126 for char in value) for value in row.values()):
            raise ValueError(f"event {number}: only printable ASCII field values are supported")
        if row["synthetic"] != "true":
            raise ValueError(f"event {number}: synthetic must be the literal true")
        if not re.fullmatch(r"HTTP-\d{4,8}", row["event_id"]) or row["event_id"] in seen:
            raise ValueError(f"event {number}: event ID must be a unique HTTP- number")
        seen.add(row["event_id"])
        parse_time(row["timestamp"])
        address = ipaddress.ip_address(row["source_ip"])
        if not any(address in network for network in NETWORKS):
            raise ValueError(f"event {number}: source address must be in an IPv4 documentation range")
        if not re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+test", row["host"]):
            raise ValueError(f"event {number}: host must be a lowercase name ending .test")
        if row["method"] not in ("GET", "HEAD", "POST"):
            raise ValueError(f"event {number}: this lab supports only GET, HEAD and POST")
        if not re.fullmatch(r"/(?:[A-Za-z0-9._~/-]*)(?:\?[A-Za-z0-9._~=&-]+)?", row["target"]):
            raise ValueError(f"event {number}: target must be a simple local path with an optional query")
        target_path = row["target"].split("?", 1)[0]
        if target_path.startswith("//") or ".." in target_path.split("/"):
            raise ValueError(f"event {number}: network-path and traversal forms are outside this lab")
        if not re.fullmatch(r"[1-5]\d\d", row["status"]):
            raise ValueError(f"event {number}: status must be a three-digit value from 100 to 599")
        if not re.fullmatch(r"0|[1-9]\d{0,9}", row["body_bytes"]):
            raise ValueError(f"event {number}: body_bytes must be a nonnegative whole number")
        if row["method"] == "HEAD" and row["body_bytes"] != "0":
            raise ValueError(f"event {number}: HEAD has no response body in this export")
        if not row["user_agent"].startswith("Practice"):
            raise ValueError(f"event {number}: user_agent must start Practice")
        clean.append(dict(row))
    return sorted(clean, key=lambda row: (row["timestamp"], row["event_id"]))


def load_events(path):
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(FIELDS):
            raise ValueError("CSV header must match the documented field order")
        return validate_events(list(reader))


def validate_context(context, events):
    fields = {"synthetic", "host", "collection_start", "collection_end", "coverage", "gaps", "notes"}
    if not isinstance(context, dict) or set(context) != fields or context["synthetic"] is not True:
        raise ValueError("context must match the documented synthetic context schema")
    start, end = parse_time(context["collection_start"]), parse_time(context["collection_end"])
    if start >= end:
        raise ValueError("collection_start must be before collection_end")
    if any(row["host"] != context["host"] or not start <= parse_time(row["timestamp"]) <= end for row in events):
        raise ValueError("events must match the context host and inclusive collection interval")
    if context["coverage"] not in ("complete-for-fixture", "known-gap"):
        raise ValueError("coverage must be complete-for-fixture or known-gap")
    if not isinstance(context["gaps"], list) or bool(context["gaps"]) != (context["coverage"] == "known-gap"):
        raise ValueError("known-gap context requires at least one gap; complete context requires none")
    previous_end = None
    for gap in context["gaps"]:
        if not isinstance(gap, dict) or set(gap) != {"start", "end", "reason"}:
            raise ValueError("each gap requires start, end and reason")
        gap_start, gap_end = parse_time(gap["start"]), parse_time(gap["end"])
        if not start <= gap_start <= gap_end <= end or (previous_end is not None and gap_start <= previous_end):
            raise ValueError("gaps must be ordered, nonoverlapping and within the collection interval")
        if any(gap_start <= parse_time(row["timestamp"]) <= gap_end for row in events):
            raise ValueError("this export defines gaps as intervals containing no retained records")
        if not isinstance(gap["reason"], str) or not gap["reason"].strip():
            raise ValueError("gap reason must be nonempty text")
        previous_end = gap_end
    if not isinstance(context["notes"], list) or not context["notes"] or any(
            not isinstance(note, str) or not note.strip() for note in context["notes"]):
        raise ValueError("context notes must be a nonempty list of text")
    return context


def validate_settings(volume_threshold, path_threshold):
    for name, value in (("volume_threshold", volume_threshold), ("path_threshold", path_threshold)):
        if type(value) is not int or not 1 <= value <= 10000:
            raise ValueError(f"{name} must be a whole number from 1 to 10000")


def analyze(rows, context, volume_threshold=8, path_threshold=3):
    validate_settings(volume_threshold, path_threshold)
    events = validate_events(rows)
    context = validate_context(context, events)
    groups = {}
    for event in events:
        groups.setdefault((event["host"], event["source_ip"]), []).append(event)
    sources, review_items = [], []
    for (host, source_ip), group in sorted(groups.items()):
        # Only the query is removed: no decoding, case folding or path normalisation.
        watched = [row for row in group if row["target"].split("?", 1)[0] in WATCH_PATHS]
        paths = sorted({row["target"].split("?", 1)[0] for row in watched})
        sensitive_200 = [row["event_id"] for row in watched if row["status"] == "200"]
        summary = {
            "host": host, "source_ip": source_ip, "request_count": len(group),
            "first_seen": group[0]["timestamp"], "last_seen": group[-1]["timestamp"],
            "method_counts": dict(sorted(Counter(row["method"] for row in group).items())),
            "status_counts": dict(sorted(Counter(row["status"] for row in group).items())),
            "distinct_targets": len({row["target"] for row in group}),
            "watched_paths": paths, "watched_event_ids": [row["event_id"] for row in watched],
            "user_agent_values": sorted({row["user_agent"] for row in group}),
            "event_ids": [row["event_id"] for row in group],
        }
        sources.append(summary)
        for rule, matched, evidence, meaning in (
            ("request-volume", len(group) >= volume_threshold, summary["event_ids"],
             "Volume is a review prompt; ordinary crawlers can match. This is a count over the whole export, not a rate."),
            ("watched-path-variety", len(paths) >= path_threshold, summary["watched_event_ids"],
             "Several exact watched paths were requested. Probing is plausible; authorisation and impact are unknown."),
            ("watched-path-200", bool(sensitive_200), sensitive_200,
             "A watched path returned 200. The logged status does not establish the response content or compromise."),
        ):
            if matched:
                review_items.append({"rule": rule, "host": host, "source_ip": source_ip,
                                     "event_ids": evidence, "meaning": meaning})
    return {
        "schema_version": 1, "synthetic": True, "tool_version": VERSION,
        "settings": {"volume_threshold": volume_threshold, "path_threshold": path_threshold},
        "watch_paths": list(WATCH_PATHS), "event_count": len(events),
        "collection_start": context["collection_start"], "collection_end": context["collection_end"],
        "coverage": context["coverage"], "gaps": context["gaps"],
        "coverage_warning": ("Known missing interval: counts are lower bounds for the collection period. No rule match is not reassurance."
                             if context["gaps"] else
                             "Complete only for this generated fixture; no claim about real-world logging completeness."),
        "sources": sources, "review_items": review_items, "review_item_count": len(review_items),
        "context_notes": context["notes"], "compromise_assessed": False,
        "limitation": "Review prompts can overlap. Request counts are not incident counts. Identity, intent, authentication outcome and response content are not established.",
    }


def make_report(case, **settings):
    case = Path(case)
    events = load_events(case / "access.csv")
    context = json.loads((case / "context.json").read_text(encoding="utf-8"))
    report = analyze(events, context, **settings)
    report["inputs_sha256"] = {name: digest((case / name).read_bytes()) for name in ("access.csv", "context.json")}
    return report


def make_case(seed, scenario):
    if type(seed) is not int or not 0 <= seed <= 2147483647:
        raise ValueError("seed must be a whole number from 0 to 2147483647")
    if scenario not in SCENARIOS:
        raise ValueError("unknown scenario")
    rng = random.Random(seed)
    base = datetime(2032, 6, 1, 9, tzinfo=timezone.utc) + timedelta(days=seed % 20, minutes=rng.randrange(40))
    host = f"practice-library-{seed % 1000:03d}.test"
    visitor = f"192.0.2.{rng.randrange(10, 200)}"
    crawler = f"198.51.100.{rng.randrange(10, 200)}"
    probe = f"203.0.113.{rng.randrange(10, 200)}"
    rows = []

    def add(second, source, method, target, status, size, agent):
        rows.append({"event_id": f"HTTP-{len(rows) + 1:04d}", "timestamp": stamp(base + timedelta(seconds=second)),
                     "source_ip": source, "host": host, "method": method, "target": target,
                     "status": str(status), "body_bytes": str(size), "user_agent": agent, "synthetic": "true"})

    for second, method, target, status, size in (
        (0, "GET", "/", 200, 900), (1, "GET", "/assets/site.css", 200, 1400),
        (2, "GET", "/assets/logo.svg", 200, 780), (120, "POST", "/contact", 303, 0),
    ):
        add(second, visitor, method, target, status, size, "PracticeBrowser/1.0")
    for index, (method, target, status, size) in enumerate((
        ("GET", "/robots.txt", 200, 60), ("GET", "/", 200, 900), ("GET", "/guides", 200, 1200),
        ("GET", "/guides/networking", 200, 1800), ("GET", "/guides/logs", 200, 1700),
        ("GET", "/guides/retired", 404, 150), ("GET", "/guides/old", 404, 150),
        ("HEAD", "/guides", 200, 0), ("GET", "/about", 200, 800), ("GET", "/contact", 200, 700),
        ("GET", "/guides/tools", 200, 1100), ("GET", "/guides/archive", 404, 150),
    )):
        add(180 + index, crawler, method, target, status, size, "PracticeCrawler/1.0")
    if scenario != "crawler-only":
        for second, method, target, status, size in (
            (240, "GET", "/.env", 200 if scenario == "soft-200" else 404, 128 if scenario == "soft-200" else 150),
            (245, "GET", "/admin", 403, 120), (250, "GET", "/backup.zip", 404, 150),
            (255, "GET", "/debug", 404, 150), (260, "POST", "/login", 200, 470),
        ):
            # Matching user-agent text deliberately does not establish a shared identity.
            add(second, probe, method, target, status, size, "PracticeCrawler/1.0")
    gaps = []
    if scenario == "logging-gap":
        gap_start, gap_end = stamp(base + timedelta(seconds=245)), stamp(base + timedelta(seconds=255))
        rows = [row for row in rows if not gap_start <= row["timestamp"] <= gap_end]
        gaps.append({"start": gap_start, "end": gap_end,
                     "reason": "Synthetic export interruption; records in this interval were not retained."})
    notes = [
        f"The fictional site owner scheduled a public-page index refresh from {crawler} during this interval. Confirm the job records before closing a real case.",
        "The owner note lists ordinary public pages and stale guide links. It does not authorise requests for configuration, backups or administration paths.",
        "User-agent strings are client-supplied labels. The same text can appear on unrelated requests.",
        "Request bodies, response bodies, cookies, authentication results, application audit records and proxy chains are absent.",
        "A status 200 on POST /login can be an ordinary login page or validation response; this export records no authentication outcome.",
    ]
    if scenario == "soft-200":
        notes.append("The site owner reports that a fallback route sometimes returns status 200 for unknown paths. This note does not identify which response body was returned here.")
    context = {"synthetic": True, "host": host, "collection_start": stamp(base),
               "collection_end": stamp(base + timedelta(seconds=300)),
               "coverage": "known-gap" if gaps else "complete-for-fixture", "gaps": gaps, "notes": notes}
    validate_context(context, validate_events(rows))
    rng.shuffle(rows)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    files = {"access.csv": output.getvalue().encode("utf-8"), "context.json": json_bytes(context)}
    manifest = {"schema_version": 1, "synthetic": True, "generator_version": VERSION,
                "seed": seed, "scenario": scenario, "event_count": len(rows),
                "provenance": "Original fictional HTTP access-log exercise created in October 2026. Generated records, not a capture or a university submission.",
                "encoding": "UTF-8 with LF line endings", "sha256": {name: digest(data) for name, data in files.items()}}
    files["manifest.json"] = json_bytes(manifest)
    return files


def writable_path(value):
    path = Path(value)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    # Resolving nested links also prevents them from redirecting writes outside runs.
    allowed = ROOT / "runs"
    if path == allowed or not path.is_relative_to(allowed):
        raise ValueError("outputs must be a new file or directory strictly inside this lab's runs/ folder")
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    return path


def save_case(path, files):
    destination = writable_path(path)
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        with (destination / name).open("xb") as handle:
            handle.write(data)


def save_report(path, report):
    destination = writable_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle:
        handle.write(json_bytes(report))
    return destination


def check_case(case, report_path=None):
    case = Path(case)
    manifest = json.loads((case / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("synthetic") is not True or manifest.get("schema_version") != 1:
        raise ValueError("manifest must identify a version 1 synthetic case")
    expected = make_case(manifest.get("seed"), manifest.get("scenario"))
    for name, data in expected.items():
        if (case / name).read_bytes() != data:
            raise ValueError(f"case mismatch: {name} differs from seeded regeneration")
    result = {"case": "PASS", "events": manifest["event_count"], "files_verified": len(expected),
              "scope": "File integrity and optional report recalculation only; not learner assessment or proof of security."}
    if report_path is not None:
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
        if not isinstance(report, dict) or not isinstance(report.get("settings"), dict) or set(report["settings"]) != set(DEFAULTS):
            raise ValueError("report must contain the expected settings")
        if report != make_report(case, **report["settings"]):
            raise ValueError("report differs from recalculation for this case and its settings")
        result["report"] = "PASS"
        result["review_items"] = report["review_item_count"]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline synthetic HTTP access-log practice. Read README.md first.")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="write a reproducible new case under runs/")
    generate.add_argument("--seed", type=int, default=53)
    generate.add_argument("--scenario", choices=SCENARIOS, default="mixed")
    generate.add_argument("--output", help="new directory inside runs/; default runs/seed-SEED-SCENARIO")
    timeline = commands.add_parser("timeline", help="print sorted requests, optionally filtered by source")
    timeline.add_argument("--case", type=Path, default=ROOT / "fixture")
    timeline.add_argument("--source-ip")
    triage = commands.add_parser("triage", help="summarise sources and explain review prompts")
    triage.add_argument("--case", type=Path, default=ROOT / "fixture")
    triage.add_argument("--volume-threshold", type=int, default=8)
    triage.add_argument("--path-threshold", type=int, default=3)
    triage.add_argument("--output", default="runs/report.json", help="new JSON file inside runs/")
    check = commands.add_parser("check", help="compare a case with seeded regeneration; optionally recalculate a report")
    check.add_argument("--case", type=Path, default=ROOT / "fixture")
    check.add_argument("--report", type=Path)
    commands.add_parser("test", help="run meaningful standard-library unit and fixture checks")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            files = make_case(args.seed, args.scenario)
            destination = writable_path(args.output or f"runs/seed-{args.seed}-{args.scenario}")
            save_case(destination, files)
            count = json.loads(files["manifest.json"])["event_count"]
            print(f"PASS generated {count} synthetic requests: {destination}")
        elif args.command == "timeline":
            report = make_report(args.case)
            rows = load_events(args.case / "access.csv")
            selected = [row for row in rows if args.source_ip is None or row["source_ip"] == args.source_ip]
            print("event_id | timestamp UTC | source_ip | method | target | status | body_bytes")
            for row in selected:
                print(" | ".join(row[field] for field in ("event_id", "timestamp", "source_ip", "method", "target", "status", "body_bytes")))
            print(f"{len(selected)} of {len(rows)} requests selected. {report['coverage_warning']}")
        elif args.command == "triage":
            report = make_report(args.case, volume_threshold=args.volume_threshold, path_threshold=args.path_threshold)
            destination = save_report(args.output, report)
            print(f"PASS read {report['event_count']} requests; {report['review_item_count']} review prompts across {len(report['sources'])} sources")
            print(report["coverage_warning"])
            print("Review prompts are not proven incidents. Compromise is not assessed.")
            print(f"Report: {destination}")
        elif args.command == "check":
            print(json_bytes(check_case(args.case, args.report)).decode("utf-8"), end="")
        else:
            RUNS.mkdir(exist_ok=True)
            suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_lab.py")
            return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
