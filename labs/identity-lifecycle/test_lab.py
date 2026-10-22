"""Boundary checks for the fictional domain model; no network required."""
import copy
import json
import unittest
from pathlib import Path
from lab import analyse, ROOT


def load(name="guided"):
    return json.loads((ROOT / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))


class DomainTests(unittest.TestCase):
    def test_all_reference_outputs_are_explicit_and_match(self):
        for name in ("guided", "changed", "challenge"):
            with self.subTest(case=name):
                expected = json.loads((ROOT / "reference" / (name + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(analyse(load(name)), expected)

    def test_analysis_preserves_supplied_evidence(self):
        case = load()
        before = copy.deepcopy(case)
        analyse(case)
        self.assertEqual(case, before)

    def test_rejects_unknown_data_fields(self):
        case = load()
        case["data"]["unexpected"] = "do not ignore"
        with self.assertRaises(ValueError):
            analyse(case)

    def test_rejects_wrong_envelope(self):
        case = load()
        case["synthetic"] = False
        with self.assertRaises(ValueError):
            analyse(case)

    def test_mover_preserves_new_duties_and_removes_stale_queue(self):
        self.assertEqual(analyse(load())["decisions"]["team-move"], "add:new-queue;remove:old-queue;retain:mail,old-reports")

    def test_exception_valid_on_expiry_day_then_removed(self):
        case = load()
        self.assertIn("retain:mail,old-reports", analyse(case)["decisions"]["team-move"])
        case["data"]["as_of"] = "2026-10-24"
        self.assertEqual(analyse(case)["decisions"]["team-move"], "add:new-queue;remove:old-queue,old-reports;retain:mail")

    def test_leaver_effective_today_is_removed(self):
        self.assertEqual(analyse(load())["decisions"]["departed"], "add:none;remove:casework,mail;retain:none")

    def test_future_leaver_retains_current_access_for_now(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["future-leaver"], "add:none;remove:none;retain:casework,mail")

    def test_future_joiner_early_access_is_removed(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["early-starter"], "add:none;remove:mail;retain:none")

    def test_future_mover_is_not_granted_new_queue_early(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["future-mover"], "add:none;remove:none;retain:mail,old-queue")

    def test_invalid_calendar_date_is_rejected(self):
        case = load()
        case["data"]["as_of"] = "2026-02-30"
        with self.assertRaises(ValueError):
            analyse(case)

    def test_leaver_cannot_smuggle_required_access(self):
        case = load()
        case["data"]["people"][2]["required"] = ["mail"]
        with self.assertRaises(ValueError):
            analyse(case)

    def test_exception_cannot_grant_new_access(self):
        case = load()
        case["data"]["people"][1]["exceptions"][0]["access"] = "payroll"
        with self.assertRaises(ValueError):
            analyse(case)

    def test_empty_set_word_is_reserved(self):
        case = load()
        case["data"]["people"][0]["required"] = ["none"]
        with self.assertRaises(ValueError):
            analyse(case)

    def test_duplicate_access_and_undated_exception_rejected(self):
        for change in ("duplicate", "date"):
            with self.subTest(change=change):
                case = load()
                if change == "duplicate":
                    case["data"]["people"][0]["required"] = ["mail", "mail"]
                else:
                    case["data"]["people"][1]["exceptions"][0]["expires_on"] = None
                with self.assertRaises(ValueError):
                    analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
