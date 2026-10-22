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

    def test_denial_is_not_a_successful_policy_change(self):
        self.assertEqual(analyse(load())["decisions"]["e02"], "denied-no-success-evidence")

    def test_approved_change_requires_correlated_authentication(self):
        case = load()
        case["data"]["events"][2]["session"] = "different-session"
        self.assertEqual(analyse(case)["decisions"]["e03"], "successful-action-unattributed")

    def test_approval_end_boundary_is_inclusive(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["c02"], "approved-change-correlated")

    def test_correlation_15_minutes_is_inclusive(self):
        decisions = analyse(load("challenge"))["decisions"]
        self.assertEqual(decisions["x02"], "successful-read-correlated")
        self.assertEqual(decisions["x03"], "successful-action-unattributed")

    def test_identity_mismatch_breaks_session_correlation(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["x04"], "successful-action-unattributed")

    def test_later_signin_cannot_explain_earlier_action(self):
        case = load("changed")
        case["data"]["events"][0]["at"] = "2026-10-23T10:12:00Z"
        self.assertEqual(analyse(case)["decisions"]["c02"], "successful-action-unattributed")

    def test_denied_disable_does_not_mark_interruption(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["logging"], "coverage-configured")

    def test_fragment_does_not_repair_category_gap(self):
        self.assertEqual(analyse(load())["decisions"]["logging"], "coverage-gap:data;interruption-observed")

    def test_rejects_event_outside_window_and_invalid_timestamp(self):
        for timestamp in ("2026-10-23T09:59:59Z", "2026-10-23T10:60:00Z", "2026-10-23T10:00:00+00:00"):
            with self.subTest(timestamp=timestamp):
                case = load()
                case["data"]["events"][0]["at"] = timestamp
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_unknown_action_and_non_boolean_logging_rejected(self):
        for change in ("action", "logging"):
            with self.subTest(change=change):
                case = load()
                if change == "action":
                    case["data"]["events"][0]["action"] = "invented-action"
                else:
                    case["data"]["logging"]["data"] = "true"
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_duplicate_event_id_rejected(self):
        case = load()
        case["data"]["events"][1]["id"] = "e01"
        with self.assertRaises(ValueError):
            analyse(case)

    def test_non_string_action_rejected_as_value_error(self):
        case = load()
        case["data"]["events"][0]["action"] = []
        with self.assertRaises(ValueError):
            analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
