"""Bounded, offline Sysmon Event 1 XML inspection. Python 3.10+, stdlib only."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).absolute().parent
MAX_BYTES = 5 * 1024 * 1024
MAX_EVENTS = 5000
NS = "{http://schemas.microsoft.com/win/2004/08/events/event}"
PROVIDER = "Microsoft-Windows-Sysmon"
CHANNEL = "Microsoft-Windows-Sysmon/Operational"
REQUIRED = ("UtcTime", "ProcessGuid", "ProcessId", "Image", "CommandLine",
            "ParentProcessGuid", "ParentProcessId", "ParentImage", "ParentCommandLine")
ZERO_GUID = "{00000000-0000-0000-0000-000000000000}"


def safe_path(value):
    """Inspect every existing component before resolving; refuse links/junctions."""
    path = Path(os.path.abspath(value))
    if os.name == "nt" and (str(path).startswith("\\\\") or ":" in str(path)[2:]):
        raise ValueError("Use a local ordinary path, without alternate data streams.")
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Linked/reparse paths are not supported.")
    return path


def read_source(path):
    path = safe_path(path)
    if path.suffix.lower() != ".xml" or not path.is_file():
        raise ValueError("Supply an existing ordinary .xml event export.")
    with path.open("rb") as source:
        data = source.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("XML exceeds the 5 MiB limit; export a smaller window.")
    return data


def timestamp(value, utc_field=False):
    """Use integer 100 ns ticks; do not lose a Windows timestamp's seventh digit."""
    match = re.fullmatch(
        r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?(Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)?",
        value,
    )
    if not match or (not utc_field and not match[4]):
        raise ValueError("Invalid timestamp, or SystemTime is missing its timezone.")
    if utc_field and match[4] not in (None, "Z", "+00:00"):
        raise ValueError("UtcTime must represent UTC.")
    zone = match[4] or "+00:00"
    base = datetime.fromisoformat(f"{match[1]}T{match[2]}{zone.replace('Z', '+00:00')}")
    try:
        base = base.astimezone(timezone.utc)
    except OverflowError as error:
        raise ValueError("Timestamp is outside the supported UTC date range.") from error
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = base - epoch
    fraction = (match[3] or "").ljust(7, "0")
    ticks = (delta.days * 86400 + delta.seconds) * 10000000 + int(fraction)
    return ticks, base.strftime("%Y-%m-%dT%H:%M:%S") + "." + fraction + "Z"


def guid(value):
    if not re.fullmatch(r"\{[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\}", value):
        raise ValueError("GUID must use the braced Sysmon format.")
    return "{" + str(uuid.UUID(value[1:-1])) + "}"


def integer(value, name, allow_zero=True, maximum=4294967295):
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError(f"{name} must be a decimal integer.")
    number = int(value)
    if number > maximum or (not allow_zero and number == 0):
        raise ValueError(f"{name} is outside the supported range.")
    return number


def one(element, tag):
    found = element.findall(NS + tag)
    if len(found) != 1:
        raise ValueError(f"Expected exactly one {tag} element.")
    return found[0]


def parse_xml(data):
    if not data or len(data) > MAX_BYTES:
        raise ValueError("Input must contain 1 byte to 5 MiB.")
    try:
        encoding = "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        text = data.decode(encoding)
    except UnicodeError as exc:
        raise ValueError("Use UTF-8 or UTF-16 with a byte order mark.") from exc
    if "\x00" in text or re.search(r"<!\s*(DOCTYPE|ENTITY)", text, re.I):
        raise ValueError("NUL bytes, DTDs and entity declarations are refused.")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML: {exc}") from exc
    if root.tag == NS + "Event":
        events = [root]
    elif root.tag in ("Events", NS + "Events"):
        events = list(root)
    else:
        raise ValueError("Expected Event/Events XML, not EVTX, CLIXML or an XML query.")
    if not events or len(events) > MAX_EVENTS:
        raise ValueError("Export must contain 1 to 5000 event elements.")
    rows, skipped, record_ids, process_ids = [], 0, set(), set()
    for event in events:
        if event.tag != NS + "Event":
            raise ValueError("Every Events child must be a namespaced Event.")
        system = one(event, "System")
        provider = one(system, "Provider").get("Name")
        event_id = one(system, "EventID").text
        if provider != PROVIDER or event_id != "1":
            skipped += 1
            continue
        computer = (one(system, "Computer").text or "").strip()
        if not computer or one(system, "Channel").text != CHANNEL:
            raise ValueError("Event 1 needs Computer and the Sysmon Operational channel.")
        record = integer(one(system, "EventRecordID").text or "", "EventRecordID", False, 2**64 - 1)
        record_key = (computer.casefold(), record)
        if record_key in record_ids:
            raise ValueError("Repeated Computer/EventRecordID; do not merge overlapping exports.")
        record_ids.add(record_key)
        system_time = one(system, "TimeCreated").get("SystemTime", "")
        _, system_utc = timestamp(system_time)
        fields = {}
        for child in one(event, "EventData"):
            name = child.get("Name")
            if child.tag != NS + "Data" or not name or name in fields or len(child):
                raise ValueError("EventData requires unique named scalar Data fields.")
            fields[name] = child.text or ""
        if any(key not in fields for key in REQUIRED):
            raise ValueError("Event 1 is missing a required process field.")
        if not fields["Image"] or not fields["ParentImage"]:
            raise ValueError("Image and ParentImage must be present.")
        process_guid = guid(fields["ProcessGuid"])
        parent_guid = guid(fields["ParentProcessGuid"])
        process_key = (computer.casefold(), process_guid)
        if process_guid == ZERO_GUID or process_key in process_ids:
            raise ValueError("A process needs a unique, nonzero ProcessGuid per Computer.")
        process_ids.add(process_key)
        ticks, utc = timestamp(fields["UtcTime"], utc_field=True)
        rows.append({
            "record_id": record, "computer": computer,
            "utc_time": utc, "utc_time_raw": fields["UtcTime"],
            "system_time_utc": system_utc, "system_time_raw": system_time,
            "process_guid": process_guid, "pid": integer(fields["ProcessId"], "ProcessId", False),
            "image": fields["Image"], "command_line": fields["CommandLine"],
            "parent_guid": parent_guid, "parent_pid": integer(fields["ParentProcessId"], "ParentProcessId"),
            "parent_image": fields["ParentImage"], "parent_command_line": fields["ParentCommandLine"],
            "_ticks": ticks,
        })
    if not rows:
        raise ValueError("No supported Sysmon Event 1 records in this export.")
    return rows, skipped


def analyse(data):
    rows, skipped = parse_xml(data)
    index = {(r["computer"].casefold(), r["process_guid"]): r for r in rows}
    for row in rows:
        parent = index.get((row["computer"].casefold(), row["parent_guid"]))
        row["parent_record_id"] = parent["record_id"] if parent else None
        row["relationship"] = "parent-present" if parent else "parent-not-in-export"
        row["consistency_notes"] = []
        if parent:
            if parent is row or parent["_ticks"] > row["_ticks"]:
                row["consistency_notes"].append("Recorded parent is self or later than child; inspect evidence/clock.")
            if parent["pid"] != row["parent_pid"]:
                row["consistency_notes"].append("GUID matches but parent PID disagrees.")
            if parent["image"].casefold() != row["parent_image"].casefold():
                row["consistency_notes"].append("GUID matches but parent image disagrees.")
        row["pid_only_other_candidates"] = sorted(
            r["record_id"] for r in rows
            if r["computer"].casefold() == row["computer"].casefold()
            and r["pid"] == row["parent_pid"] and r["process_guid"] != row["parent_guid"]
        )
    rows.sort(key=lambda r: (r["_ticks"], r["computer"].casefold(), r["record_id"]))
    for row in rows:
        del row["_ticks"]
    return {"schema_version": 1, "event_1_count": len(rows), "skipped_other_events": skipped,
            "timeline": rows, "limitations": [
                "Parent links use Computer plus ProcessGuid, never PID alone.",
                "Missing parent means absent from this export; it is not a malware verdict.",
                "Equal timestamps do not establish execution order; record ID breaks display ties only.",
                "This is recorded process-creation evidence, not command success or trusted provenance.",
                "No host, network, file content or running process has been inspected.",
            ]}


def fresh_run(name, root=ROOT):
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", name):
        raise ValueError("Run name: 1-48 lowercase letters/digits/hyphens; start with a letter.")
    if name in {"con", "prn", "aux", "nul"} or re.fullmatch(r"(?:com|lpt)[0-9]", name):
        raise ValueError("Reserved device name.")
    base = safe_path(Path(root) / "run")
    target = safe_path(base / name)
    if target.exists():
        raise ValueError("Run already exists; choose a fresh name.")
    base.mkdir(exist_ok=True)
    target.mkdir(exist_ok=False)
    return target


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, indent=2, ensure_ascii=True)
        output.write("\n")


def worksheet():
    return {"evidence_kind": "", "vm_description": "", "capture_window_utc": "",
            "sysmon_version_and_config": "", "source_sha256": "", "records_used": [],
            "process_chain_with_guids": [], "near_miss_explanation": "",
            "missing_parent_explanation": "", "timestamp_limits": "",
            "finding": "", "next_check": "", "help_used": "", "completion_claim": ""}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Create a fresh private run and blank worksheet.")
    prepare.add_argument("--name", required=True, help="New child name under this lab's run/.")
    inspect = commands.add_parser("inspect", help="Read supplied XML and create a fresh analysis run.")
    inspect.add_argument("--xml", required=True, type=Path, help="Input .xml, relative to your terminal directory.")
    inspect.add_argument("--name", required=True, help="New child name under this lab's run/.")
    inspect.add_argument("--evidence-kind", choices=("synthetic", "vm-export"), required=True,
                         help="Your declared provenance; the tool cannot authenticate it.")
    args = parser.parse_args(argv)
    try:
        report = None
        if args.command == "inspect":
            data = read_source(args.xml)
            report = analyse(data)
        destination = fresh_run(args.name, ROOT)
        answers = worksheet()
        if report is not None:
            digest = hashlib.sha256(data).hexdigest()
            answers["evidence_kind"] = args.evidence_kind
            answers["source_sha256"] = digest
            write_json(destination / "analysis.json", report)
            write_json(destination / "receipt.json", {
                "input_name": args.xml.name, "sha256": digest, "bytes_read": len(data),
                "evidence_kind_declared_by_user": args.evidence_kind,
                "source_copied": False, "source_modified": False,
                "real_capture_verified": False,
            })
        write_json(destination / "worksheet.json", answers)
        with (destination / "notes.txt").open("x", encoding="utf-8", newline="\n") as output:
            output.write("Question:\nObservation and record IDs:\nInterpretation:\nUncertainty:\nNext check:\nHelp used:\n")
        print(json.dumps({"status": "created", "run": str(destination),
                          "event_1_count": report["event_1_count"] if report else None}))
        return 0
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
