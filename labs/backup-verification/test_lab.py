"""Boundary and invalid-evidence tests for the offline teaching model."""
import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((Path(__file__).parent / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_preserves_input(self):
        case = self.case()
        before = copy.deepcopy(case)
        lab.analyse(case)
        self.assertEqual(case, before)

    def test_rejects_unknown_data_field(self):
        case = self.case()
        case["data"]["unsupported"] = 1
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_rpo_boundary_is_inclusive_to_the_second(self):
        case = self.case(); case["data"]["backups"][0]["captured_at"] = "2026-02-01T08:00:00Z"
        self.assertEqual(lab.analyse(case)["decisions"]["b1"], "qualified-synthetic-copy")
        case["data"]["backups"][0]["captured_at"] = "2026-02-01T07:59:59Z"
        self.assertEqual(lab.analyse(case)["decisions"]["b1"], "rpo-exceeded")

    def test_retention_end_is_exclusive(self):
        case = self.case(); case["data"]["backups"][0]["retained_until"] = "2026-02-01T12:00:00Z"
        self.assertEqual(lab.analyse(case)["decisions"]["b1"], "retention-expired")

    def test_missing_scope_and_hash_mismatch_are_different(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["b1"], "required-scope-missing")
        result = lab.analyse(self.case("changed"))["decisions"]
        self.assertEqual(result["b1"], "restore-bytes-mismatch")
        self.assertEqual(result["b0"], "rpo-exceeded")
        self.assertEqual(result["recovery"], "no-qualified-copy")

    def test_rejects_invalid_base64_and_future_capture(self):
        case = self.case(); case["data"]["backups"][0]["payload_base64"]["notes.txt"] = "not base64!"
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case(); case["data"]["backups"][0]["captured_at"] = "2026-02-01T12:00:01Z"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_rejects_unknown_scope_and_invalid_manifest(self):
        case = self.case(); case["data"]["backups"][0]["payload_base64"]["unknown.txt"] = ""
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case(); case["data"]["required_sha256"]["notes.txt"] = "not-a-hash"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_latest_qualified_copy_wins_and_ties_are_explicit(self):
        case = self.case(); second = copy.deepcopy(case["data"]["backups"][0]); second["id"] = "b2"
        case["data"]["backups"].append(second)
        self.assertEqual(lab.analyse(case)["decisions"]["recovery"], "select:b2")
        second["captured_at"] = "2026-02-01T09:59:59Z"
        self.assertEqual(lab.analyse(case)["decisions"]["recovery"], "select:b1")

    def test_zero_rpo_requires_exact_recovery_point(self):
        case = self.case(); case["data"]["rpo_hours"] = 0
        case["data"]["backups"][0]["captured_at"] = case["data"]["recovery_time"]
        self.assertEqual(lab.analyse(case)["decisions"]["b1"], "qualified-synthetic-copy")

if __name__ == "__main__":
    unittest.main()
