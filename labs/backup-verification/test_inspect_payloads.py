"""Independent known-byte and disclosure checks for the evidence inspector."""
import base64
import contextlib
import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import inspect_payloads
import lab


class InspectorTests(unittest.TestCase):
    def case(self):
        return json.loads((Path(__file__).parent / "fixtures" / "guided.json").read_text(encoding="utf-8"))

    def test_known_bytes_and_sha256_without_manifest_comparison(self):
        case = self.case()
        case["data"]["backups"][0]["payload_base64"]["notes.txt"] = "YWJj"
        measured = lab.measure_payloads(case)[0]
        self.assertEqual(measured, {"backup_id": "b1", "file": "notes.txt",
                                   "byte_length": 3, "decoded_bytes_hex": "616263",
                                   "decoded_utf8": "abc",
                                   "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"})

    def test_preserves_input(self):
        case = self.case()
        before = copy.deepcopy(case)
        lab.measure_payloads(case)
        self.assertEqual(case, before)

    def test_binary_bytes_are_retained_without_lossy_text(self):
        case = self.case()
        case["data"]["backups"][0]["payload_base64"]["notes.txt"] = base64.b64encode(b"\xff\x00").decode("ascii")
        measured = lab.measure_payloads(case)[0]
        self.assertEqual(measured["decoded_bytes_hex"], "ff00")
        self.assertEqual(measured["byte_length"], 2)
        self.assertIsNone(measured["decoded_utf8"])

    def test_invalid_payload_and_duplicate_backup_are_rejected(self):
        case = self.case()
        case["data"]["backups"][0]["payload_base64"]["notes.txt"] = "!invalid!"
        with self.assertRaises(ValueError): lab.measure_payloads(case)
        case = self.case()
        case["data"]["backups"][1]["id"] = "b1"
        with self.assertRaises(ValueError): lab.measure_payloads(case)

    def test_unknown_scope_is_rejected(self):
        case = self.case()
        case["data"]["backups"][0]["payload_base64"]["extra.txt"] = "YWJj"
        with self.assertRaises(ValueError): lab.measure_payloads(case)

    def test_cli_does_not_call_analyser_or_emit_decisions(self):
        output = io.StringIO()
        with patch.object(inspect_payloads, "read_json", return_value=self.case()), patch.object(lab, "analyse", side_effect=AssertionError("answer must remain closed")), contextlib.redirect_stdout(output):
            code = inspect_payloads.main(["--case", "unused.json"])
        result = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(set(result), {"case_id", "measurements", "scope"})
        self.assertEqual(len(result["measurements"]), 4)
        self.assertTrue(all(set(row) == {"backup_id", "file", "byte_length", "decoded_bytes_hex", "decoded_utf8", "sha256"} for row in result["measurements"]))

    def test_invalid_input_exits_two_without_partial_measurements(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(inspect_payloads, "read_json", side_effect=ValueError("bad case")), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = inspect_payloads.main(["--case", "unused.json"])
        self.assertEqual(code, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("Input error: bad case", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
