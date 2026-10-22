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

    def test_exact_maintenance_tuple_and_partial_approval(self):
        self.assertEqual(lab.analyse(self.case())["decisions"]["archive"], "approved-maintenance-difference")
        case = self.case(); case["data"]["observed"][0]["account"] = "SYSTEM"
        self.assertEqual(lab.analyse(case)["decisions"]["archive"], "unapproved-change-review")

    def test_new_task_can_have_exact_documented_approval(self):
        case = self.case("changed")
        approval = copy.deepcopy(case["data"]["observed"][1]); approval["reason"] = "Fictional approved cleanup"
        case["data"]["approvals"] = [approval]
        self.assertEqual(lab.analyse(case)["decisions"]["cleanup"], "approved-maintenance-difference")

    def test_missing_snapshot_is_not_deletion_verdict(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["inventory"], "missing-from-snapshot")

    def test_daily_time_boundaries(self):
        case = self.case(); case["data"]["observed"][0]["daily_time"] = "23:59"
        self.assertEqual(lab.analyse(case)["decisions"]["archive"], "unapproved-change-review")
        for value in ("24:00", "12:60", "3:00", None):
            case["data"]["observed"][0]["daily_time"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): lab.analyse(case)

    def test_rejects_duplicate_and_unobserved_approval(self):
        case = self.case(); case["data"]["observed"].append(copy.deepcopy(case["data"]["observed"][0]))
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case(); case["data"]["approvals"][0]["id"] = "unobserved"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_literal_path_comparison_and_no_traversal(self):
        case = self.case(); case["data"]["observed"][0]["action"] = "C:/Lab/bin/ARCHIVE.exe"
        self.assertEqual(lab.analyse(case)["decisions"]["archive"], "unapproved-change-review")
        case["data"]["observed"][0]["action"] = "C:/Lab/../real.exe"
        with self.assertRaises(ValueError): lab.analyse(case)

if __name__ == "__main__":
    unittest.main()
