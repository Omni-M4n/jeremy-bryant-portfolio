#!/usr/bin/env python3
"""Convert one PS5 registration from a chiaki-ng v1.10.0 INI export.

Contract: --input FILE --account-id BASE64 --host RFC1918_IP --output NEW_JSON.
Python 3.9+; stdlib only; no network, discovery, registry or credential lookup.
Reads only the named input; creates (never overwrites) the named output. Output
contains sensitive pairing material. CLI diagnostics never echo input values.

Supported: native Qt UTF-8 (optional BOM), LF/CRLF, [registered_hosts], 1-based
array keys, optional whole-value quoting, Qt ByteArray/numeric scalar escapes.
Rejects duplicate/partial arrays, multiple PS5s, hand-edited multiline/list/
non-byte escape values, unknown escapes, and non-native key/section spelling.
Other sections and non-required host fields are ignored; OAuth is not copied.

Primary-source contracts (verified 2026-10-21):
https://github.com/chiaki-ng/chiaki-ng/blob/v1.10.0/gui/src/host.cpp
https://github.com/chiaki-ng/chiaki-ng/blob/v1.10.0/gui/src/settings.cpp
https://github.com/chiaki-ng/chiaki-ng/blob/v1.10.0/lib/include/chiaki/common.h
https://github.com/qt/qtbase/blob/v6.8.3/src/corelib/io/qsettings.cpp
  variantToString/stringToVariant; iniEscapedString/iniUnescapedStringList.
https://github.com/TacticalBill/chiaki-lg/blob/v0.1.2/src/config.c
https://github.com/TacticalBill/chiaki-lg/blob/v0.1.2/src/main.c
https://github.com/TacticalBill/chiaki-lg/blob/v0.1.2/src/config_import.c
"""

import argparse
import base64
import binascii
import ipaddress
import json
import os
from pathlib import Path
import re
import sys


MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_HOSTS = 1024
REQUIRED_FIELDS = {"target", "rp_regist_key", "rp_key", "rp_key_type", "server_mac"}
ESCAPES = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r",
           "t": "\t", "v": "\v", '"': '"', "'": "'", "?": "?", "\\": "\\"}
RFC1918 = tuple(ipaddress.ip_network(n) for n in
                ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))


class ConversionError(ValueError):
    """A fixed, non-sensitive diagnostic suitable for CLI display."""


def qt_scalar(raw):
    """Decode the native-export subset of QSettings INI scalar escaping.

    Hex AND octal runs are greedy, as in Qt. A byte export cannot produce an
    escape above 255: reject it instead of truncating or guessing boundaries.
    Qt writes following hex characters as separate escapes to avoid ambiguity.
    """
    value = raw.strip(" \t")
    if value.startswith('"'):
        if len(value) < 2 or not value.endswith('"'):
            raise ConversionError("Unterminated quoted setting.")
        value = value[1:-1]
        quoted = True
    else:
        quoted = False
    result = []
    i = 0
    while i < len(value):
        ch = value[i]
        i += 1
        if ch == "\\":
            if i == len(value):
                raise ConversionError("Incomplete setting escape.")
            ch = value[i]
            i += 1
            if ch in ESCAPES:
                result.append(ESCAPES[ch])
                continue
            if ch == "x":
                digits, radix, start = "0123456789abcdefABCDEF", 16, i
            elif ch in "01234567":
                digits, radix, start = "01234567", 8, i - 1
            else:
                raise ConversionError("Unsupported setting escape.")
            while i < len(value) and value[i] in digits:
                i += 1
            if i == start:
                raise ConversionError("Empty numeric setting escape.")
            # Bound conversion before int(): long runs are not native byte exports.
            run = value[start:i]
            if len(run) > 6:
                raise ConversionError("Numeric setting escape exceeds a byte.")
            number = int(run, radix)
            if number > 255:
                raise ConversionError("Numeric setting escape exceeds a byte.")
            result.append(chr(number))
        elif ch == '"' or (not quoted and ch in ",;="):
            raise ConversionError("Unsupported quoted/list setting format.")
        elif ord(ch) < 32 or ord(ch) > 126:
            raise ConversionError("Setting is not in native export scalar format.")
        else:
            result.append(ch)
    return "".join(result)


def qt_bytearray(raw, expected_length):
    value = qt_scalar(raw)
    if not value.startswith("@ByteArray(") or not value.endswith(")"):
        raise ConversionError("Required field is not a Qt ByteArray.")
    # Only remove the outer wrapper: embedded ')' and trailing NUL are data.
    data = value[11:-1].encode("latin-1")
    if len(data) != expected_length:
        raise ConversionError("Required byte field has an invalid decoded length.")
    return data


def uint_setting(raw, maximum):
    value = qt_scalar(raw)
    if not re.fullmatch(r"[0-9]{1,10}", value):
        raise ConversionError("Required numeric setting is not an unsigned integer.")
    number = int(value)
    if number > maximum:
        raise ConversionError("Required numeric setting is out of range.")
    return number


def read_registered_hosts(text):
    hosts = {}
    size = None
    in_hosts = False
    seen_section = False
    seen_keys = set()
    for line in text.split("\n"):
        line = line.removesuffix("\r").strip(" \t")
        if not line or line.startswith(";"):
            continue
        if line.startswith("["):
            if not line.endswith("]"):
                raise ConversionError("Malformed INI section.")
            in_hosts = line == "[registered_hosts]"
            if in_hosts:
                if seen_section:
                    raise ConversionError("Duplicate registered-host section.")
                seen_section = True
            continue
        if not in_hosts:
            continue
        if "=" not in line:
            raise ConversionError("Malformed registered-host setting.")
        key, raw = line.split("=", 1)
        key = key.strip(" \t")
        if key in seen_keys:
            raise ConversionError("Duplicate registered-host setting.")
        seen_keys.add(key)
        if key == "size":
            size = uint_setting(raw, MAX_HOSTS)
            continue
        match = re.fullmatch(r"([1-9][0-9]{0,3})\\([a-z_]+)", key)
        if match is None:
            raise ConversionError("Unsupported registered-host key format.")
        index, field = int(match[1]), match[2]
        record = hosts.setdefault(index, {})
        if field in REQUIRED_FIELDS:
            record[field] = raw
    if not seen_section or size is None:
        raise ConversionError("Registered-host array or size is missing.")
    if set(hosts) != set(range(1, size + 1)):
        raise ConversionError("Registered-host array is incomplete or inconsistent.")
    candidates = []
    for record in hosts.values():
        if "target" not in record:
            raise ConversionError("A registered host has no target setting.")
        if uint_setting(record["target"], 2147483647) >= 1000000:
            candidates.append(record)
    if len(candidates) != 1:
        raise ConversionError("Export must contain exactly one registered PS5.")
    selected = candidates[0]
    if not REQUIRED_FIELDS.issubset(selected):
        raise ConversionError("The PS5 registration is missing required fields.")
    return selected, size


def build_config(text, account_id, host):
    try:
        account = base64.b64decode(account_id, validate=True)
    except (binascii.Error, ValueError):
        raise ConversionError("Account ID must be canonical base64 of 8 bytes.") from None
    if len(account) != 8 or base64.b64encode(account).decode("ascii") != account_id:
        raise ConversionError("Account ID must be canonical base64 of 8 bytes.")
    try:
        address = ipaddress.IPv4Address(host)
    except ipaddress.AddressValueError:
        raise ConversionError("Host must be an RFC1918 IPv4 address.") from None
    if not any(address in network for network in RFC1918):
        raise ConversionError("Host must be an RFC1918 IPv4 address.")
    record, count = read_registered_hosts(text)
    registration = qt_bytearray(record["rp_regist_key"], 16)
    rp_key = qt_bytearray(record["rp_key"], 16)
    mac = qt_bytearray(record["server_mac"], 6)
    # chiaki-lg config_load uses json_object_get_int, so reject signed overflow.
    key_type = uint_setting(record["rp_key_type"], 2147483647)
    config = {
        "host": str(address), "ps5": True, "psn_account_id": account_id,
        "registered_key": base64.b64encode(registration).decode("ascii"),
        "rp_key": base64.b64encode(rp_key).decode("ascii"), "rp_key_type": key_type,
        "video_width": 1920, "video_height": 1080, "video_fps": 60,
        "video_bitrate": 15000, "video_codec": "h265", "audio_volume": 100,
        "wakeup": False, "ps5_mac": ":".join(f"{b:02x}" for b in mac),
        "wakeup_delay_ms": 60000, "sleep_on_exit": False,
        "log_level": "warning", "psn_refresh_token": "", "ss4s_module": "auto",
    }
    return config, count


def convert(input_path, account_id, host, output_path):
    try:
        with Path(input_path).open("rb") as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
    except OSError:
        raise ConversionError("Could not read the input file.") from None
    if len(raw) > MAX_INPUT_BYTES:
        raise ConversionError("Input file exceeds the supported size limit.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ConversionError("Input must be a UTF-8 Qt INI export.") from None
    config, count = build_config(text, account_id, host)
    payload = (json.dumps(config, indent=2) + "\n").encode("utf-8")
    try:
        # O_EXCL prevents overwrite, including symlinks, even with concurrent runs.
        fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ConversionError("Output already exists; choose a new output file.") from None
    except OSError:
        raise ConversionError("Could not create the new output file.") from None
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        # Preserve a partial output for inspection; never delete an input/source.
        raise ConversionError("Output write failed; a partial new file may exist.") from None
    return count


class QuietArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes unknown arguments, which may include secrets.
        self.exit(2, "Invalid command arguments; use --help for the CLI contract.\n")


def main(argv=None):
    parser = QuietArgumentParser(description=__doc__.split("\n\n", 1)[0],
                                 allow_abbrev=False)
    parser.add_argument("--input", required=True, metavar="FILE")
    parser.add_argument("--account-id", required=True, metavar="BASE64")
    parser.add_argument("--host", required=True, metavar="RFC1918_IP")
    parser.add_argument("--output", required=True, metavar="NEW_JSON")
    args = parser.parse_args(argv)
    try:
        count = convert(args.input, args.account_id, args.host, args.output)
    except ConversionError as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        return 1
    print(f"registered_hosts={count}; selected_ps5=1; registered_key_bytes=16; "
          "rp_key_bytes=16; account_id_bytes=8; mac_bytes=6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
