#!/usr/bin/env python3
"""Offline SYNTHETIC DNS lab. Run `python lab.py --help` for the compact contract.

Python 3.9+, standard library only. Never opens a socket or captures traffic.
Output paths are relative to this lab; generated files live under run/ by default.
"""

import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import random
import struct
import sys


ROOT = Path(__file__).resolve().parent
DEFAULT_SEED = 37
PCAP_NAME = "SYNTHETIC-dns.pcap"
BASE_SECONDS = 1700000000
DOC_NETWORKS = tuple(ipaddress.ip_network(net) for net in (
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"
))
OUTCOMES = ("answer", "nxdomain", "unanswered")
ANSWER_FIELDS = ("request_frames", "response_frames", "outcome", "first_response_ms")


class LabError(ValueError):
    """The case is malformed, inconsistent, or outside this lab's narrow format."""


def need(condition, message):
    if not condition:
        raise LabError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def checksum(data):
    if len(data) % 2:
        data += b"\0"
    total = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    while total >> 16:
        total = (total & 0xffff) + (total >> 16)
    return (~total) & 0xffff


def documentation_ip(value):
    try:
        address = ipaddress.ip_address(value)
    except ValueError as error:
        raise LabError("Invalid IP address") from error
    need(any(address in network for network in DOC_NETWORKS),
         "Only documentation IPv4 addresses are allowed")
    return address.packed


def encode_name(name):
    need(name.startswith("synthetic-") and name.endswith(".test"),
         "Names must be visibly synthetic and end in .test")
    labels = [part.encode("ascii") for part in name.split(".")]
    need(all(0 < len(label) <= 63 for label in labels), "Invalid DNS label length")
    encoded = b"".join(bytes([len(label)]) + label for label in labels) + b"\0"
    need(len(encoded) <= 255, "DNS name is too long")
    return encoded


def decode_name(data, start):
    labels, seen, cursor, end = [], set(), start, None
    while True:
        need(cursor < len(data), "Truncated DNS name")
        need(cursor not in seen, "DNS compression pointer loop")
        seen.add(cursor)
        size = data[cursor]
        if size & 0xc0 == 0xc0:
            need(cursor + 1 < len(data), "Truncated DNS compression pointer")
            pointer = ((size & 0x3f) << 8) | data[cursor + 1]
            need(pointer < len(data), "DNS compression pointer outside message")
            if end is None:
                end = cursor + 2
            cursor = pointer
            continue
        need(size & 0xc0 == 0, "Unsupported DNS label encoding")
        cursor += 1
        if size == 0:
            if end is None:
                end = cursor
            break
        need(cursor + size <= len(data), "Truncated DNS label")
        try:
            labels.append(data[cursor:cursor + size].decode("ascii"))
        except UnicodeDecodeError as error:
            raise LabError("Non-ASCII name outside this lab's format") from error
        cursor += size
        need(sum(len(label) + 1 for label in labels) < 255, "DNS name is too long")
    name = ".".join(labels)
    encode_name(name)
    return name, end


def dns_message(dns_id, name, outcome=None, answer_ip=None):
    answer = outcome == "answer"
    flags = 0x0100 if outcome is None else (0x8183 if outcome == "nxdomain" else 0x8180)
    header = struct.pack("!6H", dns_id, flags, 1, int(answer), 0, 0)
    question = encode_name(name) + struct.pack("!HH", 1, 1)
    resource = b""
    if answer:
        resource = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 60, 4) + documentation_ip(answer_ip)
    return header + question + resource


def packet(src, dst, src_port, dst_port, payload, identification):
    src_bytes, dst_bytes = documentation_ip(src), documentation_ip(dst)
    udp_length = 8 + len(payload)
    udp = struct.pack("!HHHH", src_port, dst_port, udp_length, 0) + payload
    pseudo = src_bytes + dst_bytes + struct.pack("!BBH", 0, 17, udp_length)
    udp_check = checksum(pseudo + udp) or 0xffff
    udp = struct.pack("!HHHH", src_port, dst_port, udp_length, udp_check) + payload
    header = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), identification,
                         0, 64, 17, 0, src_bytes, dst_bytes)
    header = header[:10] + struct.pack("!H", checksum(header)) + header[12:]
    # Locally administered unicast MACs, constructed rather than captured.
    source_mac = b"\x02\x00\x00\x00\x00" + src_bytes[-1:]
    destination_mac = b"\x02\x00\x00\x00\x00" + dst_bytes[-1:]
    return destination_mac + source_mac + b"\x08\x00" + header + udp


def read_dns(data):
    need(len(data) >= 12, "Truncated DNS header")
    dns_id, flags, questions, answers, authorities, additionals = struct.unpack("!6H", data[:12])
    need(questions == 1 and authorities == 0 and additionals == 0,
         "Unexpected DNS section counts")
    need(flags in (0x0100, 0x8180, 0x8183), "Unexpected DNS flags")
    is_response = bool(flags & 0x8000)
    need(answers in (0, 1) and (is_response or answers == 0), "Unexpected DNS answers")
    name, offset = decode_name(data, 12)
    need(offset + 4 <= len(data), "Truncated DNS question")
    qtype, qclass = struct.unpack("!HH", data[offset:offset + 4])
    need((qtype, qclass) == (1, 1), "Only A/IN questions belong in this fixture")
    offset += 4
    answer_ip = None
    if answers:
        owner, offset = decode_name(data, offset)
        need(offset + 10 <= len(data), "Truncated DNS answer")
        rrtype, rrclass, ttl, length = struct.unpack("!HHIH", data[offset:offset + 10])
        offset += 10
        need((rrtype, rrclass, ttl, length) == (1, 1, 60, 4) and owner == name,
             "Unexpected A answer fields")
        need(offset + length <= len(data), "Truncated A address")
        answer_ip = str(ipaddress.ip_address(data[offset:offset + length]))
        documentation_ip(answer_ip)
        offset += length
    need(offset == len(data), "Trailing DNS bytes")
    need(flags != 0x8183 or answers == 0, "NXDOMAIN must not include an A answer here")
    need(not is_response or flags == 0x8183 or answers == 1,
         "This narrow fixture does not include NOERROR without an A answer")
    return dict(dns_id=dns_id, qname=name, qtype="A", is_response=is_response,
                rcode=flags & 15, answer_ip=answer_ip)


def read_packet(frame):
    need(len(frame) >= 42, "Truncated Ethernet/IPv4/UDP packet")
    need(frame[12:14] == b"\x08\x00", "Expected Ethernet IPv4")
    need(frame[0] == 2 and frame[6] == 2, "Expected synthetic locally administered MACs")
    ip = frame[14:34]
    version, tos, length, ident, fragment, ttl, protocol, check, src, dst = struct.unpack("!BBHHHBBH4s4s", ip)
    need(version == 0x45 and tos == 0 and fragment == 0 and ttl == 64 and protocol == 17,
         "Unexpected IPv4 format")
    need(length == len(frame) - 14 and checksum(ip) == 0, "Invalid IPv4 length or checksum")
    src, dst = str(ipaddress.ip_address(src)), str(ipaddress.ip_address(dst))
    documentation_ip(src)
    documentation_ip(dst)
    udp = frame[34:]
    src_port, dst_port, udp_length, udp_check = struct.unpack("!4H", udp[:8])
    need(udp_length == len(udp) and udp_check != 0, "Invalid UDP length or missing checksum")
    pseudo = documentation_ip(src) + documentation_ip(dst) + struct.pack("!BBH", 0, 17, udp_length)
    need(checksum(pseudo + udp) == 0, "Invalid UDP checksum")
    dns = read_dns(udp[8:])
    if dns["is_response"]:
        need(src_port == 53 and 49152 <= dst_port <= 65535, "Invalid DNS response ports")
        client, resolver, client_port = dst, src, dst_port
    else:
        need(dst_port == 53 and 49152 <= src_port <= 65535, "Invalid DNS request ports")
        client, resolver, client_port = src, dst, src_port
    return dict(dns, client=client, resolver=resolver, client_port=client_port)


def read_pcap(data):
    need(len(data) >= 24, "Truncated PCAP header")
    header = struct.unpack("<IHHIIII", data[:24])
    need(header == (0xa1b2c3d4, 2, 4, 0, 0, 65535, 1), "Unexpected PCAP global header")
    frames, offset, previous = [], 24, -1
    while offset < len(data):
        need(offset + 16 <= len(data), "Truncated PCAP record header")
        seconds, micros, included, original = struct.unpack("<IIII", data[offset:offset + 16])
        offset += 16
        need(0 < included == original <= 65535 and micros < 1000000,
             "Invalid PCAP record lengths or time")
        need(offset + included <= len(data), "Truncated PCAP record data")
        timestamp = seconds * 1000000 + micros
        need(timestamp >= previous, "PCAP timestamps are out of order")
        decoded = read_packet(data[offset:offset + included])
        frames.append(dict(decoded, frame=len(frames) + 1, timestamp_us=timestamp))
        offset += included
        previous = timestamp
    need(bool(frames), "Empty PCAP")
    return frames


def relationships(frames):
    sessions = {}
    for frame in frames:
        key = tuple(frame[field] for field in ("client", "resolver", "client_port", "dns_id", "qname", "qtype"))
        if not frame["is_response"]:
            if key not in sessions:
                sessions[key] = {field: frame[field] for field in
                                 ("client", "resolver", "client_port", "dns_id", "qname", "qtype")}
                sessions[key].update(request_frames=[], response_frames=[], outcome="unanswered",
                                     first_response_ms=None, first_request_us=frame["timestamp_us"])
            need(not sessions[key]["response_frames"], "Unexpected request after a completed episode")
            sessions[key]["request_frames"].append(frame["frame"])
        else:
            need(key in sessions, "Response without an earlier matching request")
            session = sessions[key]
            need(not session["response_frames"], "Multiple responses outside this lab's format")
            delta = frame["timestamp_us"] - session["first_request_us"]
            need(delta >= 0, "Response predates request")
            session["response_frames"].append(frame["frame"])
            session["outcome"] = "nxdomain" if frame["rcode"] == 3 else "answer"
            session["first_response_ms"] = delta / 1000
    result = []
    for session in sessions.values():
        del session["first_request_us"]
        result.append(session)
    return sorted(result, key=lambda item: (item["qname"], item["client"]))


def build_case(seed):
    need(type(seed) is int and 0 <= seed <= 2147483647, "Seed must be an integer from 0 to 2147483647")
    rng = random.Random(seed)
    words = ["maple", "harbor", "orchard", "violet", "copper", "willow", "lantern", "meadow"]
    rng.shuffle(words)
    names = ["synthetic-" + word + ".test" for word in words[:5]]
    resolver = "192.0.2.53"
    ids = rng.sample(range(4096, 60000), 4)
    ports = rng.sample(range(49152, 65000), 5)
    outcomes = ["answer", "nxdomain", "unanswered", "answer", "answer"]
    events, expected = [], []
    for index, outcome in enumerate(outcomes):
        client = "192.0.2.10" if index % 2 == 0 else "192.0.2.11"
        dns_id = ids[0] if index == 3 else ids[index if index < 3 else 3]
        at = index * 200000
        request_times = [at]
        if index in (2, 4):
            request_times.append(at + 1000000)
        reply_time = None
        if outcome != "unanswered":
            reply_time = at + (rng.randint(1300, 1700) if index == 4 else rng.randint(21, 65)) * 1000
        answer_ip = "203.0.113." + str(rng.randint(20, 220))
        session = dict(client=client, resolver=resolver, client_port=ports[index], dns_id=dns_id,
                       qname=names[index], qtype="A", request_frames=[], response_frames=[],
                       outcome=outcome, first_response_ms=None if reply_time is None else (reply_time - at) / 1000)
        expected.append(session)
        for request_at in request_times:
            events.append((request_at, index, False,
                           packet(client, resolver, ports[index], 53,
                                  dns_message(dns_id, names[index]), len(events) + 1)))
        if reply_time is not None:
            events.append((reply_time, index, True,
                           packet(resolver, client, 53, ports[index],
                                  dns_message(dns_id, names[index], outcome, answer_ip), len(events) + 1)))
    events.sort(key=lambda event: event[0])
    pcap = struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    for number, (micros, index, is_response, data) in enumerate(events, 1):
        seconds, remainder = divmod(micros, 1000000)
        pcap += struct.pack("<IIII", BASE_SECONDS + seconds, remainder, len(data), len(data)) + data
        expected[index]["response_frames" if is_response else "request_frames"].append(number)
    expected.sort(key=lambda item: (item["qname"], item["client"]))
    case = dict(title="SYNTHETIC DNS troubleshooting practice", seed=seed, synthetic=True,
                capture=PCAP_NAME, clients=["192.0.2.10", "192.0.2.11"], resolver=resolver,
                questions=sorted(names), question_type="A", packet_count=len(events),
                context="Constructed observation of two clients asking one resolver. No live capture.",
                observation_limit="Only the packets in this file are observable; no evidence after its final packet.")
    files = {PCAP_NAME: pcap, "case.json": json_bytes(case)}
    manifest = dict(schema_version=1, algorithm="dns-triage-v1", synthetic=True, seed=seed,
                    provenance={"source": "Constructed from scratch by lab.py; no capture or coursework input.",
                                "addresses": "RFC 5737 documentation IPv4 ranges only.",
                                "names": "Synthetic names under reserved .test (RFC 2606).",
                                "time": "Fixed invented timestamps; not an observation date.",
                                "mac_addresses": "Constructed locally administered unicast values.",
                                "personal_data": "None; no third-party traffic, secrets, or real hosts."},
                    files={name: {"bytes": len(content), "sha256": sha256(content)} for name, content in files.items()},
                    expected={"packet_count": len(events), "episodes": expected})
    files["manifest.json"] = json_bytes(manifest)
    return files


def lab_path(value, output=False):
    path = (ROOT / value).resolve()
    try:
        relative = path.relative_to(ROOT)
    except ValueError as error:
        raise LabError("Paths must stay inside this lab") from error
    need(bool(relative.parts), "Choose a child path inside this lab")
    if output:
        need(relative.parts[0] in ("run", "fixtures") and len(relative.parts) >= 2,
             "Outputs must be below run/ or fixtures/")
    return path


def write_case(directory, files):
    if directory.exists():
        need(directory.is_dir(), "Output path is not a directory")
        for name, data in files.items():
            target = directory / name
            need(not target.exists() or (target.is_file() and target.read_bytes() == data),
                 "Output differs from existing files; choose a fresh output directory")
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (directory / name).write_bytes(data)


def verify_case(directory):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    need(isinstance(manifest, dict), "Manifest must be an object")
    files = build_case(manifest.get("seed"))
    expected_manifest = json.loads(files["manifest.json"])
    need(manifest == expected_manifest, "Manifest differs from the deterministic synthetic specification")
    for name, specification in manifest["files"].items():
        actual = (directory / name).read_bytes()
        need(len(actual) == specification["bytes"] and sha256(actual) == specification["sha256"],
             "File integrity mismatch: " + name)
        need(actual == files[name], "File differs from deterministic generated bytes: " + name)
    decoded = read_pcap((directory / PCAP_NAME).read_bytes())
    observed = relationships(decoded)
    need(len(decoded) == manifest["expected"]["packet_count"], "Wrong packet count")
    need(observed == manifest["expected"]["episodes"], "Packet relationships differ from expected evidence")
    need(len(observed) == 5 and sum(x["outcome"] == "answer" for x in observed) == 3
         and sum(x["outcome"] == "nxdomain" for x in observed) == 1
         and sum(x["outcome"] == "unanswered" for x in observed) == 1,
         "Scenario learning relationships are missing")
    reused_ids = {episode["dns_id"] for episode in observed}
    need(len(reused_ids) == 4, "Expected a DNS ID collision across distinct client flows")
    return manifest, observed


def worksheet(manifest, episodes):
    return dict(title="SYNTHETIC DNS evidence worksheet", seed=manifest["seed"],
                capture_sha256=manifest["files"][PCAP_NAME]["sha256"],
                independent_mastery="NOT assessed", explanation_review="Human review required",
                episodes=[dict(client=episode["client"], qname=episode["qname"], request_frames=[],
                               response_frames=[], outcome="", first_response_ms=None,
                               explanation="") for episode in episodes],
                limits="Write what this capture cannot tell you.")


def check_answers(answers, manifest, expected):
    need(isinstance(answers, dict), "Worksheet must be an object")
    need(type(answers.get("seed")) is int and answers["seed"] == manifest["seed"] and
         answers.get("capture_sha256") == manifest["files"][PCAP_NAME]["sha256"],
         "Worksheet belongs to a different case")
    submitted = answers.get("episodes")
    need(isinstance(submitted, list), "Worksheet episodes must be a list")
    indexed = {}
    for item in submitted:
        need(isinstance(item, dict), "Worksheet episode must be an object")
        key = (item.get("qname"), item.get("client"))
        need(all(isinstance(part, str) for part in key), "Episode needs a question and client")
        need(key not in indexed, "Duplicate worksheet episode")
        indexed[key] = item
    need(set(indexed) == {(item["qname"], item["client"]) for item in expected},
         "Worksheet must contain exactly the case's five episodes")
    problems = []
    for episode in expected:
        entry = indexed[(episode["qname"], episode["client"])]
        for field in ANSWER_FIELDS:
            actual, wanted = entry.get(field), episode[field]
            valid = actual == wanted
            if field in ("request_frames", "response_frames"):
                valid = valid and isinstance(actual, list) and all(type(x) is int for x in actual)
            if field == "first_response_ms":
                valid = valid and (actual is None or type(actual) in (int, float))
            if not valid:
                problems.append(episode["qname"] + ": revisit " + field)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="Construct a deterministic synthetic case; no network activity")
    generate.add_argument("--seed", type=int, default=DEFAULT_SEED, help="0..2147483647; default 37")
    generate.add_argument("--out", help="Lab-relative directory; default run/case-SEED; existing different files are refused")
    for name in ("verify", "exercise", "check"):
        subparser = commands.add_parser(name, help={"verify": "Verify hashes, packet bytes, checksums, and relationships",
                                                   "exercise": "Create a blank JSON worksheet without revealing answers",
                                                   "check": "Check objective worksheet fields; explanation/mastery require human review"}[name])
        subparser.add_argument("--case", default="fixtures/guided", help="Lab-relative case directory; default fixtures/guided")
        if name == "exercise":
            subparser.add_argument("--out", help="New lab-relative worksheet; default run/worksheet-SEED.json")
        if name == "check":
            subparser.add_argument("--answers", required=True, help="Lab-relative completed JSON worksheet")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            files = build_case(args.seed)
            directory = lab_path(args.out or "run/case-" + str(args.seed), output=True)
            write_case(directory, files)
            verify_case(directory)
            print("PASS: generated and verified SYNTHETIC case seed %s (11 packets, 5 episodes): %s" %
                  (args.seed, directory.relative_to(ROOT).as_posix()))
            return 0
        directory = lab_path(args.case)
        manifest, episodes = verify_case(directory)
        if args.command == "verify":
            print("PASS: SYNTHETIC case seed %s; hashes, deterministic bytes, 11 packet records, IPv4/UDP checksums, DNS fields, and 5 episode relationships." % manifest["seed"])
            print("This validates the fixture. Independent learner mastery: NOT assessed.")
        elif args.command == "exercise":
            output = lab_path(args.out or "run/worksheet-%s.json" % manifest["seed"], output=True)
            need(not output.exists(), "Worksheet already exists; choose a fresh --out path")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(json_bytes(worksheet(manifest, episodes)))
            print("Created blank worksheet: " + output.relative_to(ROOT).as_posix())
        else:
            answers = json.loads(lab_path(args.answers).read_text(encoding="utf-8"))
            problems = check_answers(answers, manifest, episodes)
            if problems:
                print("NOT YET: %d objective fields need another look." % len(problems))
                print("\n".join(problems))
                print("Written reasoning and independent mastery: NOT assessed.")
                return 1
            print("PASS: 20 objective fields match the packet evidence. Written reasoning and independent mastery: NOT assessed.")
        return 0
    except (LabError, OSError, ValueError, TypeError, KeyError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
