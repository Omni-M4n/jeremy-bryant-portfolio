"""Synthetic-only checks; never open a real export or contact a console."""
import base64
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import chiaki_pairing_converter as converter


ACCOUNT = base64.b64encode(b"fakeacct").decode("ascii")
REGISTRATION = b"1234abcd" + bytes(8)
RP_KEY = b'"\\)\x00\xffA0\x1c,;=\n\r\t\x00\x00'
MAC = b"\x00\x12\xab\xcd\xef\xff"


def bytearray_text(data):
    # A simple independent valid Qt serialization: every byte has its own escape.
    return "@ByteArray(" + "".join(f"\\x{b:02x}" for b in data) + ")"


def fixture(records=1, targets=None):
    targets = targets or [1000100] * records
    lines = ["[General]", "version=2", "[registered_hosts]", f"size={records}"]
    for i, target in enumerate(targets, 1):
        lines.extend([
            f"{i}\\target={target}", f"{i}\\rp_key_type=7",
            f"{i}\\rp_regist_key={bytearray_text(REGISTRATION)}",
            f"{i}\\rp_key={bytearray_text(RP_KEY)}",
            f"{i}\\server_mac={bytearray_text(MAC)}",
            f"{i}\\server_nickname=Synthetic console",
        ])
    lines.extend(["[settings]", "psn_refresh_token=FAKE-TOKEN-MUST-NOT-COPY"])
    return "\n".join(lines) + "\n"


class ConverterTests(unittest.TestCase):
    def test_escaped_native_value_and_embedded_parenthesis(self):
        raw = r'"@ByteArray(\"\\)\0\xff\x41\x30\x1c,;=\n\r\t\0\0)"'
        self.assertEqual(converter.qt_bytearray(raw, 16), RP_KEY)

    def test_greedy_hex_and_printable_hex_adjacency(self):
        self.assertEqual(converter.qt_bytearray(r"@ByteArray(\x1\x41\x32Z)", 4),
                         b"\x01A2Z")
        self.assertEqual(converter.qt_bytearray(r"@ByteArray(\x1aZ)", 2), b"\x1aZ")
        with self.assertRaises(converter.ConversionError):
            converter.qt_bytearray(r"@ByteArray(\x1aAZ)", 3)

    def test_nul_adjacency_octal_and_controls(self):
        self.assertEqual(converter.qt_bytearray(r"@ByteArray(\0\x37\a\b\f\v\377)", 7),
                         b"\0" + b"7\a\b\f\v\xff")
        self.assertEqual(converter.qt_bytearray(r"@ByteArray(\012)", 1), b"\n")

    def test_all_byte_values_and_repeated_trailing_nuls(self):
        for start in range(0, 256, 16):
            value = bytes(range(start, start + 16))
            self.assertEqual(converter.qt_bytearray(bytearray_text(value), 16), value)
        self.assertEqual(converter.qt_bytearray(bytearray_text(bytes(16)), 16), bytes(16))

    def test_mapping_defaults_and_nul_preservation(self):
        config, count = converter.build_config(fixture(), ACCOUNT, "192.168.1.10")
        self.assertEqual(count, 1)
        self.assertEqual(base64.b64decode(config["registered_key"]), REGISTRATION)
        self.assertEqual(base64.b64decode(config["rp_key"]), RP_KEY)
        self.assertEqual(config["psn_account_id"], ACCOUNT)
        self.assertEqual(config["rp_key_type"], 7)
        self.assertEqual(config["ps5_mac"], "00:12:ab:cd:ef:ff")
        self.assertEqual((config["video_width"], config["video_height"],
                          config["video_fps"], config["video_bitrate"],
                          config["video_codec"]), (1920, 1080, 60, 15000, "h265"))
        self.assertFalse(config["wakeup"])
        self.assertFalse(config["sleep_on_exit"])
        self.assertEqual(config["log_level"], "warning")
        self.assertEqual(config["ss4s_module"], "auto")
        self.assertEqual(config["psn_refresh_token"], "")

    def test_single_ps5_selected_among_ps4(self):
        self.assertEqual(converter.build_config(fixture(2, [1000, 1000100]),
                                               ACCOUNT, "10.1.2.3")[1], 2)

    def test_ambiguous_missing_or_inconsistent_hosts(self):
        for text in (fixture(2), fixture(1, [1000]), fixture(0),
                     fixture().replace("size=1", "size=2"),
                     fixture().replace("1\\target=1000100\n", ""),
                     fixture() + "[registered_hosts]\nsize=0\n",
                     fixture().replace("size=1", "size=1\nsize=1"),
                     fixture().replace("1\\rp_key_type=7\n", "")):
            with self.subTest(case=text[:30]), self.assertRaises(converter.ConversionError):
                converter.build_config(text, ACCOUNT, "192.168.1.10")

    def test_bad_lengths_and_malformed_bytearray(self):
        for data, expected in ((bytes(15), 16), (bytes(17), 16), (bytes(5), 6)):
            with self.assertRaises(converter.ConversionError):
                converter.qt_bytearray(bytearray_text(data), expected)
        for raw in (r"@ByteArray(\x)", r"@ByteArray(\q)", r"@ByteArray(\Xff)",
                    "@ByteArray(abc", '"@ByteArray(abc)', "@ByteArray(a,b)",
                    "@ByteArray(abc)garbage", "QGJ5dGVz", r"@ByteArray(\400)"):
            with self.subTest(raw=raw), self.assertRaises(converter.ConversionError):
                converter.qt_bytearray(raw, 3)

    def test_account_validation(self):
        for account in ("bad", "AAAAAAAAAA==", "AAAAAAAAAAAA", ACCOUNT + "\n",
                        "é" * 12, "ZmFrZWFjY3R="):
            with self.subTest(account=account), self.assertRaises(converter.ConversionError):
                converter.build_config(fixture(), account, "192.168.1.10")

    def test_rfc1918_only_and_key_type_limits(self):
        for host in ("127.0.0.1", "169.254.1.1", "100.64.0.1", "8.8.8.8", "::1",
                     "172.32.0.1", "192.168.001.1", "console.example"):
            with self.subTest(host=host), self.assertRaises(converter.ConversionError):
                converter.build_config(fixture(), ACCOUNT, host)
        for key_type in ("-1", "1.2", "2147483648", "4294967295"):
            with self.assertRaises(converter.ConversionError):
                converter.build_config(fixture().replace("rp_key_type=7", "rp_key_type=" + key_type),
                                       ACCOUNT, "172.16.0.1")

    def test_cli_bom_crlf_no_overwrite_and_no_secrets_in_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "fake.ini", Path(directory) / "new.json"
            original = b"\xef\xbb\xbf" + fixture().replace("\n", "\r\n").encode("utf-8")
            source.write_bytes(original)
            args = ["--input", str(source), "--account-id", ACCOUNT,
                    "--host", "192.168.1.10", "--output", str(output)]
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(converter.main(args), 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("registered_key_bytes=16", stdout.getvalue())
            for secret in (ACCOUNT, "192.168.1.10", "FAKE-TOKEN", str(source), str(output)):
                self.assertNotIn(secret, stdout.getvalue())
            saved = output.read_bytes()
            self.assertEqual(base64.b64decode(json.loads(saved)["registered_key"]), REGISTRATION)
            self.assertEqual(source.read_bytes(), original)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(converter.main(args), 1)
            self.assertEqual(output.read_bytes(), saved)
            args[-1] = str(source)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(converter.main(args), 1)
            self.assertEqual(source.read_bytes(), original)

    def test_argument_error_does_not_echo_unknown_secret(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as result:
            converter.main(["--bogus=FAKE-SECRET"])
        self.assertEqual(result.exception.code, 2)
        self.assertNotIn("FAKE-SECRET", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
