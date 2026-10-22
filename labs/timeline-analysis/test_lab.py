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

    def test_offset_correction_can_reverse_display_order(self):
        result = lab.analyse(self.case("challenge"))["decisions"]
        self.assertEqual(result["e1-vs-e2"], "definitely-after")
        self.assertEqual(result["e2-vs-e3"], "order-uncertain")

    def test_touching_intervals_are_not_strict_order(self):
        case = self.case(); case["data"]["events"][0]["uncertainty_seconds"] = 12
        self.assertEqual(lab.analyse(case)["decisions"]["e1-vs-e2"], "order-uncertain")
        case["data"]["events"][0]["uncertainty_seconds"] = 11
        self.assertEqual(lab.analyse(case)["decisions"]["e1-vs-e2"], "definitely-before")

    def test_negative_offset_is_added_to_recorded_time(self):
        case = self.case(); case["data"]["events"][0]["clock_offset_seconds"] = -30
        self.assertEqual(lab.analyse(case)["decisions"]["e1-vs-e2"], "definitely-after")

    def test_rejects_naive_or_impossible_timestamp(self):
        for stamp in ("2026-01-15T10:00:00", "2026-02-30T10:00:00Z", "2026-01-15T10:00:00+10:99"):
            case = self.case(); case["data"]["events"][0]["time"] = stamp
            with self.subTest(stamp=stamp), self.assertRaises(ValueError): lab.analyse(case)

    def test_rejects_invalid_uncertainty_and_boolean_offset(self):
        for key, value in (("uncertainty_seconds", -1), ("uncertainty_seconds", 3601), ("clock_offset_seconds", True)):
            case = self.case(); case["data"]["events"][0][key] = value
            with self.subTest(key=key,value=value), self.assertRaises(ValueError): lab.analyse(case)

    def test_rejects_unknown_or_same_event_comparison(self):
        for value in ("unknown", "e1"):
            case = self.case(); case["data"]["pairs"][0]["right"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): lab.analyse(case)

if __name__ == "__main__":
    unittest.main()
