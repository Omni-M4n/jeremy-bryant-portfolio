"""Packet and boundary tests. Mocked wrapper tests never count as real Snort runs."""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import lab


class SnortLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ("fixtures/cases.json", "reference/expected.json", "local.rules", "PROVENANCE.json"):
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(lab.ROOT / name, destination)
        self.root_patch = patch.object(lab, "ROOT", self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def test_packet_headers_handshake_ack_and_independent_inputs(self):
        for case in lab.load_cases():
            rows = lab.parse_pcap(lab.build_pcap(case))
            self.assertEqual(len(rows), 9)
            self.assertEqual([row["flags"] for row in rows[:4]], [2, 18, 16, 24])
            self.assertEqual(rows[1]["ack"], rows[0]["seq"] + 1)
            self.assertEqual(rows[2]["ack"], rows[1]["seq"] + 1)
            self.assertEqual(rows[4]["ack"], rows[3]["seq"] + len(rows[3]["payload"]))
            self.assertEqual(rows[8]["ack"], rows[7]["seq"] + 1)
            self.assertEqual(rows[3]["source"], "192.0.2.10")
            self.assertEqual(rows[3]["destination"], "198.51.100.20")
            self.assertEqual(sum(bool(row["payload"]) for row in rows), 1)
            expected_marker = {"positive": b"ORCHARD-CANARY-42", "near-miss": b"orchard-canary-42",
                               "negative": b"ORDINARY-BOOKING-42", "wrong-port": b"ORCHARD-CANARY-42"}[case["id"]]
            self.assertIn(b"X-Lab-Marker: " + expected_marker + b"\r\n", rows[3]["payload"])
            self.assertEqual(rows[3]["destination_port"], 18081 if case["id"] == "wrong-port" else 18080)

    def test_known_checksum_vector_and_corruption(self):
        self.assertEqual(lab.checksum(bytes.fromhex("0001f203f4f5f6f7")), 0x220D)
        self.assertEqual(lab.checksum(b"\x01"), 0xFEFF)
        data = lab.build_pcap(lab.load_cases()[0])
        for invalid in (data[:23], data[:-1], data + b"x", bytes(24)):
            with self.subTest(length=len(invalid)), self.assertRaises(ValueError):
                lab.parse_pcap(invalid)
        changed = bytearray(data)
        changed[24 + 16 + 14 + 8] ^= 1  # change IP TTL without repairing checksum
        with self.assertRaisesRegex(ValueError, "checksum"):
            lab.parse_pcap(bytes(changed))
        changed = bytearray(data)
        changed[24 + 16 + 34 + 4] ^= 1  # change TCP sequence number
        with self.assertRaisesRegex(ValueError, "TCP checksum"):
            lab.parse_pcap(bytes(changed))

    def test_fixture_integrity_is_not_engine_execution(self):
        result = lab.verify_sources()
        self.assertEqual(result["snort_execution"], "not performed by verify")
        lab.prepare("run/first")
        lab.prepare("run/second")
        for name in lab.CASE_IDS:
            self.assertEqual((self.root / f"run/first/{name}.pcap").read_bytes(),
                             (self.root / f"run/second/{name}.pcap").read_bytes())
        self.assertFalse(json.loads((self.root / "run/first/provenance.json").read_text())["captured_from_network"])

    def test_expected_results_are_explicit_and_not_generated_from_rule(self):
        expected = json.loads((self.root / "reference/expected.json").read_text())
        self.assertEqual(expected["case-sensitive"], {"positive": 1, "near-miss": 0, "negative": 0, "wrong-port": 0})
        self.assertEqual(expected["case-insensitive"], {"positive": 1, "near-miss": 1, "negative": 0, "wrong-port": 0})

    def test_source_tampering_and_unsupported_fixture_rejected(self):
        fixture = self.root / "fixtures/cases.json"
        value = json.loads(fixture.read_text())
        value["cases"][0]["source_ip"] = "127.0.0.1"
        fixture.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "source hash"):
            lab.verify_sources()
        with self.assertRaisesRegex(ValueError, "documentation addresses"):
            lab.load_cases()

    def test_no_snort_is_explicitly_unverified(self):
        lab.prepare("run/input")
        with patch.object(lab.shutil, "which", return_value=None), patch.object(lab.subprocess, "run") as process:
            result, code = lab.run_snort("run/input", "run/no-engine", "case-sensitive")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "unverified")
        process.assert_not_called()

    def test_external_engine_errors_cannot_pass_as_zero_alerts(self):
        lab.prepare("run/input")
        version = subprocess.CompletedProcess([], 0, "Snort++ Version 3.1.0\n", "")
        error = subprocess.CompletedProcess([], 1, "", "rule parse failed")
        with patch.object(lab.shutil, "which", return_value="snort"), \
                patch.object(lab.subprocess, "run", side_effect=[version, error, error, error, error]), \
                contextlib.redirect_stdout(io.StringIO()):
            result, code = lab.run_snort("run/input", "run/engine-error", "case-sensitive")
        self.assertEqual(code, 1)
        self.assertTrue(all(row["status"] == "engine_error" and row["count"] is None for row in result["cases"].values()))

    def test_rule_edit_is_local_and_bounded(self):
        lab.prepare("run/input")
        rule_file = self.root / "run/input/local.rules"
        original = rule_file.read_text()
        rule_file.write_text(original.replace('content:"ORCHARD-CANARY-42";', 'content:"ORCHARD-CANARY-42",nocase;'))
        lab.validate_attempt("run/input")
        rule_file.write_text(original + "include /elsewhere.rules\n")
        with self.assertRaises(ValueError):
            lab.validate_attempt("run/input")

    def test_paths_freshness_and_link_boundary(self):
        for bad in ("run/../../escape", "run/a/b", "run", "elsewhere/name", "run/nul", "run/x:y"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                lab.fresh_run(bad)
        path = lab.fresh_run("run/kept")
        lab.write_new(path / "note.txt", "keep me")
        with self.assertRaises(ValueError):
            lab.fresh_run("run/kept")
        with self.assertRaises(FileExistsError):
            lab.write_new(path / "note.txt", "replace")
        linked = self.root / "run/link"
        try:
            linked.symlink_to(path, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaises(ValueError):
            lab.run_path("run/link")

    def test_json_alert_parser_does_not_treat_noise_as_clean(self):
        self.assertEqual(lab.count_alerts(""), [])
        self.assertEqual(len(lab.count_alerts('{"rule":"1:1000001:1","pkt_num":4}')), 1)
        for text in ("warning: logger failed", "{}", "[]"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                lab.count_alerts(text)

    def test_windows_reparse_attribute_refused(self):
        run = self.root / "run"
        run.mkdir()
        original = Path.lstat
        def metadata(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400) if path == run else info
        with patch.object(Path, "lstat", metadata), self.assertRaises(ValueError):
            lab.fresh_run("run/escaped")


if __name__ == "__main__":
    unittest.main(verbosity=2)
