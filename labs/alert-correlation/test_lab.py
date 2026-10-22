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

    def test_inclusive_anchor_boundary(self):
        case = self.case("challenge"); case["data"]["alerts"][3]["time"] = "2026-02-01T00:05:00Z"
        result = lab.analyse(case)["decisions"]
        self.assertEqual(result["workstation.test/student/1"], "review-auth-sequence")
        self.assertEqual(result["workstation.test/student/2"], "retain-context")

    def test_window_does_not_chain(self):
        case = self.case(); rows = case["data"]["alerts"][:3]
        rows[1]["time"] = "2026-02-01T00:04:00Z"; rows[2]["time"] = "2026-02-01T00:08:00Z"
        case["data"]["alerts"] = rows
        self.assertEqual(len(lab.analyse(case)["decisions"]), 2)

    def test_duplicate_ids_collapse_but_conflicts_reject(self):
        self.assertIn("unique alerts=3", lab.analyse(self.case("changed"))["observations"][0])
        case = self.case(); case["data"]["alerts"][-1]["kind"] = "auth-success"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_distinct_ids_remain_distinct_at_same_time(self):
        case = self.case(); rows = case["data"]["alerts"][:4]
        for row in rows[:3]: row["time"] = "2026-02-01T00:00:00Z"
        case["data"]["alerts"] = rows
        self.assertEqual(lab.analyse(case)["decisions"]["workstation.test/student/1"], "review-auth-sequence")
        rows[3]["time"] = "2026-02-01T00:00:00Z"
        self.assertEqual(lab.analyse(case)["decisions"]["workstation.test/student/1"], "retain-context")

    def test_account_partition_prevents_false_sequence(self):
        case = self.case(); case["data"]["alerts"] = case["data"]["alerts"][:4]
        case["data"]["alerts"][3]["account"] = "other-user"
        self.assertEqual(set(lab.analyse(case)["decisions"].values()), {"retain-context"})

    def test_rejects_nonfictional_host_and_invalid_window(self):
        case = self.case(); case["data"]["alerts"][0]["host"] = "live.example.com"
        with self.assertRaises(ValueError): lab.analyse(case)
        for value in (0, 3601, True):
            case = self.case(); case["data"]["window_seconds"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): lab.analyse(case)

if __name__ == "__main__":
    unittest.main()
