"""Offline Snort 3 rule experiment. Contract: README.md; fresh run/NAME outputs only."""
from __future__ import annotations
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import subprocess
import sys

ROOT = Path(__file__).absolute().parent
CASE_IDS = ("positive", "near-miss", "negative", "wrong-port")


def safe_path(path):
    path = Path(os.path.abspath(path))
    for component in (path, *path.parents):
        if component.exists() or component.is_symlink():
            info = component.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("linked or reparse paths are refused")
    return path


def run_path(relative):
    relative = Path(relative)
    if len(relative.parts) != 2 or relative.parts[0] != "run" or not re.fullmatch(
            r"[a-z0-9][a-z0-9_-]{0,63}", relative.parts[1]):
        raise ValueError("use a direct child such as run/attempt-01")
    if relative.parts[1] in {"con", "prn", "aux", "nul", *[f"{p}{i}" for p in ("com", "lpt") for i in range(1, 10)]}:
        raise ValueError("reserved run name")
    return safe_path(ROOT / relative)


def fresh_run(output):
    target = run_path(output)
    if target.exists():
        raise ValueError("output already exists; choose a new run name")
    safe_path(ROOT / "run").mkdir(exist_ok=True)
    target.mkdir()
    return target


def write_new(path, value):
    if isinstance(value, bytes):
        data = value
    elif isinstance(value, str):
        data = value.encode("utf-8")
    else:
        data = (json.dumps(value, indent=2) + "\n").encode("utf-8")
    with safe_path(path).open("xb") as stream:
        stream.write(data)


def read_bytes(path, maximum=1_000_000):
    path = safe_path(path)
    if not path.is_file() or path.stat().st_size > maximum:
        raise ValueError("input must be a regular file under the size limit")
    return path.read_bytes()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_cases():
    value = json.loads(read_bytes(ROOT / "fixtures/cases.json"))
    if not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("synthetic") is not True:
        raise ValueError("unsupported fixture provenance")
    rows = value.get("cases", [])
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows) or [row.get("id") for row in rows] != list(CASE_IDS):
        raise ValueError("fixture case IDs or order differ from the contract")
    for row in rows:
        if set(row) != {"id", "source_ip", "destination_ip", "destination_port", "marker"}:
            raise ValueError("unsupported case fields")
        if row["source_ip"] != "192.0.2.10" or row["destination_ip"] != "198.51.100.20":
            raise ValueError("only the specified documentation addresses are allowed")
        if type(row["destination_port"]) is not int or row["destination_port"] not in (18080, 18081):
            raise ValueError("unsupported fixture port")
        if not isinstance(row["marker"], str) or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", row["marker"]):
            raise ValueError("marker must be 1-64 simple ASCII characters")
    return rows


def checksum(data):
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 65535) + (total >> 16)
    return (~total) & 65535


def frame(source, destination, source_port, destination_port, seq, ack, flags, payload, identifier):
    src = ipaddress.IPv4Address(source).packed
    dst = ipaddress.IPv4Address(destination).packed
    tcp = struct.pack("!HHIIBBHHH", source_port, destination_port, seq, ack, 5 << 4, flags, 32768, 0, 0)
    pseudo = src + dst + struct.pack("!BBH", 0, 6, len(tcp) + len(payload))
    tcp = tcp[:16] + struct.pack("!H", checksum(pseudo + tcp + payload)) + tcp[18:]
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 40 + len(payload), identifier, 0x4000, 64, 6, 0, src, dst)
    ip = ip[:10] + struct.pack("!H", checksum(ip)) + ip[12:]
    # Locally administered fictional Ethernet addresses; no interface is opened.
    ethernet = bytes.fromhex("0200000000020200000000010800") if source == "192.0.2.10" else bytes.fromhex("0200000000010200000000020800")
    return (ethernet + ip + tcp + payload).ljust(60, b"\x00")


def build_pcap(case):
    source, destination = case["source_ip"], case["destination_ip"]
    destination_port = case["destination_port"]
    payload = ("GET /marker HTTP/1.1\r\nHost: orchard.test\r\nX-Lab-Marker: " + case["marker"] +
               "\r\nConnection: close\r\n\r\n").encode("ascii")
    end = 1001 + len(payload)
    # Complete handshake, one client data segment, ACK, orderly two-way FIN.
    conversation = [(False, 1000, 0, 0x02, b""), (True, 9000, 1001, 0x12, b""),
                    (False, 1001, 9001, 0x10, b""), (False, 1001, 9001, 0x18, payload),
                    (True, 9001, end, 0x10, b""), (False, end, 9001, 0x11, b""),
                    (True, 9001, end + 1, 0x10, b""), (True, 9001, end + 1, 0x11, b""),
                    (False, end + 1, 9002, 0x10, b"")]
    content = bytearray(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for index, (reverse, seq, ack, flags, body) in enumerate(conversation, start=1):
        args = (destination, source, destination_port, 45000) if reverse else (source, destination, 45000, destination_port)
        packet = frame(*args, seq, ack, flags, body, index)
        content.extend(struct.pack("<IIII", 1_700_000_000, index * 1000, len(packet), len(packet)))
        content.extend(packet)
    return bytes(content)


def parse_pcap(data):
    """Structural validation only; this is deliberately not a Snort evaluator."""
    header = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    if data[:24] != header:
        raise ValueError("unsupported PCAP header")
    offset, rows = 24, []
    while offset < len(data):
        if len(data) - offset < 16:
            raise ValueError("truncated PCAP record")
        seconds, micros, captured, original = struct.unpack_from("<IIII", data, offset)
        offset += 16
        packet = data[offset:offset + captured]
        offset += captured
        if captured != original or len(packet) != captured or captured < 54 or micros >= 1_000_000:
            raise ValueError("invalid PCAP record length or timestamp")
        if packet[12:14] != b"\x08\x00" or packet[14] != 0x45 or packet[23] != 6:
            raise ValueError("expected Ethernet/IPv4/TCP without options")
        total_length = struct.unpack_from("!H", packet, 16)[0]
        if total_length < 40 or 14 + total_length > len(packet):
            raise ValueError("invalid IP length")
        ip, tcp = packet[14:34], packet[34:14 + total_length]
        if checksum(ip) != 0 or tcp[12] >> 4 != 5:
            raise ValueError("bad IP checksum or unsupported TCP options")
        pseudo = ip[12:20] + struct.pack("!BBH", 0, 6, len(tcp))
        if checksum(pseudo + tcp) != 0:
            raise ValueError("bad TCP checksum")
        sport, dport, seq, ack = struct.unpack_from("!HHII", tcp)
        rows.append({"frame": len(rows) + 1, "source": str(ipaddress.IPv4Address(ip[12:16])),
                     "destination": str(ipaddress.IPv4Address(ip[16:20])), "source_port": sport,
                     "destination_port": dport, "seq": seq, "ack": ack, "flags": tcp[13], "payload": tcp[20:]})
    if not rows:
        raise ValueError("empty PCAP")
    return rows


def verify_sources():
    provenance = json.loads(read_bytes(ROOT / "PROVENANCE.json"))
    if set(provenance["sources_sha256"]) != {"fixtures/cases.json", "reference/expected.json", "local.rules"} or set(provenance["generated_pcap_sha256"]) != set(CASE_IDS):
        raise ValueError("incomplete provenance inventory")
    for name, expected in provenance["sources_sha256"].items():
        if name not in ("fixtures/cases.json", "reference/expected.json", "local.rules"):
            raise ValueError("unsupported provenance source")
        if digest(read_bytes(ROOT / name)) != expected:
            raise ValueError(f"source hash mismatch: {name}")
    cases = load_cases()
    counts = {}
    for case in cases:
        data = build_pcap(case)
        if digest(data) != provenance["generated_pcap_sha256"][case["id"]]:
            raise ValueError(f"generated PCAP differs: {case['id']}")
        counts[case["id"]] = len(parse_pcap(data))
        if counts[case["id"]] != 9:
            raise ValueError("expected nine packets per fixture")
    return {"fixture_integrity": "verified", "packet_counts": counts,
            "snort_execution": "not performed by verify", "learner_completion": "unassessed"}


def prepare(output):
    verify_sources()
    target = fresh_run(output)
    pcaps = {}
    for case in load_cases():
        data = build_pcap(case)
        name = case["id"] + ".pcap"
        write_new(target / name, data)
        pcaps[name] = digest(data)
    write_new(target / "local.rules", read_bytes(ROOT / "local.rules"))
    write_new(target / "provenance.json", {"synthetic": True, "captured_from_network": False,
              "timestamps": "Fixed fictional fixture times; not execution times.", "pcap_sha256": pcaps,
              "fixture_source_sha256": digest(read_bytes(ROOT / "fixtures/cases.json"))})
    write_new(target / "worksheet.txt", "Snort rule experiment\nVersion and platform:\nRule conditions in plain words:\n"
              "Before running: predict SID 1000001 count for positive, near-miss, negative and wrong-port.\n"
              "Observed counts and stdout/stderr evidence:\nExit status for each file:\n"
              "Frame with marker and destination port:\nWhy is this a harmless alert?\n"
              "What does zero alerts fail to prove?\nChange: predicted effect of nocase, then observed effect:\n"
              "One rule limitation:\nHelp used:\nTeach-back:\nLater recall:\n")
    return {"prepared": str(target), "pcaps": list(pcaps), "snort_execution": "not yet performed"}


def validate_attempt(relative):
    attempt = run_path(relative)
    for case in load_cases():
        name = case["id"] + ".pcap"
        if read_bytes(attempt / name) != build_pcap(case):
            raise ValueError(f"fixture differs: {name}; prepare a fresh run")
    rule = read_bytes(attempt / "local.rules", 4096).decode("utf-8")
    active = [line.strip() for line in rule.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    # Permit only the bounded rule experiment, including simple content/port edits.
    pattern = (r'alert tcp 192\.0\.2\.10 any -> 198\.51\.100\.20 (18080|18081) '
               r'\(msg:"[A-Za-z0-9 -]{1,80}"; raw_data; content:"[A-Za-z0-9-]{1,64}"(?:,nocase)?; '
               r'sid:1000001; rev:[1-9][0-9]?;\)')
    if len(active) != 1 or not re.fullmatch(pattern, active[0]):
        raise ValueError("rule exceeds the bounded one-line format; follow the README edit exactly")
    return attempt, rule


def count_alerts(stdout):
    alerts = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if not isinstance(item, dict) or not isinstance(item.get("rule"), str):
            raise ValueError("unexpected Snort JSON output; inspect saved stdout")
        if re.fullmatch(r"1:1000001:[1-9][0-9]?", item["rule"]):
            alerts.append(item)
    return alerts


def run_snort(attempt_name, output, expectation, executable=None):
    verify_sources()
    attempt, rule = validate_attempt(attempt_name)
    target = fresh_run(output)
    executable = executable or shutil.which("snort") or shutil.which("snort3")
    if not executable:
        result = {"status": "unverified", "reason": "Snort executable not found; no detection engine ran."}
        write_new(target / "result.json", result)
        return result, 2
    executable = str(Path(executable).absolute()) if Path(executable).is_file() else shutil.which(executable)
    if not executable:
        raise ValueError("Snort executable not found")
    version = subprocess.run([executable, "-V"], capture_output=True, text=True, errors="replace", cwd=target, timeout=20)
    version_text = version.stdout + version.stderr
    write_new(target / "version.txt", version_text)
    if version.returncode != 0 or not re.search(r"Version\s+3\.", version_text, re.IGNORECASE):
        raise ValueError("Snort 3 is required; inspect version.txt")
    write_new(target / "local.rules", rule)
    expected = json.loads(read_bytes(ROOT / "reference/expected.json"))[expectation]
    result = {"status": "executed", "expectation": expectation, "rule_sha256": digest(rule.encode()),
              "cases": {}, "meaning": "Counts are operational checks for this harmless rule; not mastery or attack findings."}
    failed = False
    for case_id in CASE_IDS:
        destination = target / case_id
        destination.mkdir()
        pcap = read_bytes(attempt / (case_id + ".pcap"))
        write_new(destination / "input.pcap", pcap)
        command = [executable, "-q", "-R", str(target / "local.rules"), "-r", str(destination / "input.pcap"),
                   "-A", "alert_json", "-l", str(destination), "--lua", "search_engine = { detect_raw_tcp = true }"]
        write_new(destination / "command.json", command)
        print(f"Running Snort on {case_id}...", flush=True)
        try:
            process = subprocess.run(command, cwd=destination, capture_output=True, text=True,
                                     errors="replace", timeout=30)
        except subprocess.TimeoutExpired as error:
            write_new(destination / "stdout.txt", error.stdout or b"")
            write_new(destination / "stderr.txt", error.stderr or b"")
            result["cases"][case_id] = {"status": "timeout", "count": None}
            failed = True
            continue
        write_new(destination / "stdout.txt", process.stdout)
        write_new(destination / "stderr.txt", process.stderr)
        row = {"exit_code": process.returncode, "expected_count": expected[case_id], "count": None,
               "pcap_sha256": digest(pcap)}
        if process.returncode == 0:
            try:
                alerts = count_alerts(process.stdout)
                row.update(count=len(alerts), alerts=alerts, status="matched" if len(alerts) == expected[case_id] else "different")
            except (ValueError, json.JSONDecodeError) as error:
                row.update(status="output_unreadable", detail=str(error))
        else:
            row["status"] = "engine_error"
        failed |= row["status"] != "matched"
        result["cases"][case_id] = row
    result["status"] = "needs_review" if failed else "expected_counts_observed"
    write_new(target / "result.json", result)
    return result, 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify", help="check fixture hashes and packet structure; does not run Snort")
    sub.add_parser("cases", help="show fixture inputs; no verdict simulation")
    prepare_parser = sub.add_parser("prepare", help="write deterministic synthetic PCAPs and rule copy")
    prepare_parser.add_argument("--out", required=True)
    run = sub.add_parser("run-snort", help="execute an installed Snort 3 against four offline fixtures")
    run.add_argument("--attempt", required=True, help="existing prepared run/NAME")
    run.add_argument("--out", required=True, help="fresh run/NAME")
    run.add_argument("--expect", choices=("case-sensitive", "case-insensitive"), default="case-sensitive")
    run.add_argument("--snort", help="installed Snort 3 executable path; default searches PATH")
    args = parser.parse_args(argv)
    try:
        code = 0
        if args.command == "verify":
            result = verify_sources()
        elif args.command == "cases":
            result = load_cases()
        elif args.command == "prepare":
            result = prepare(args.out)
        else:
            result, code = run_snort(args.attempt, args.out, args.expect, args.snort)
        print(json.dumps(result, indent=2))
        return code
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
