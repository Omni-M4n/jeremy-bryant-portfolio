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

    def test_deleted_line_still_exposes_value_in_diff(self):
        output = analyse(load())
        self.assertIn("change-diff.txt:L1(diff,shared)", output["observations"][0])
        self.assertEqual(output["decisions"]["export-token"], "contain;revoke-and-replace;clean-copies;review-use")

    def test_local_only_value_is_relocated_before_sharing(self):
        self.assertEqual(analyse(load())["decisions"]["local-token"], "relocate-before-sharing")

    def test_revocation_does_not_erase_retained_copy(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["export-token"], "confirm-revocation;clean-copies;review-use")

    def test_exact_marker_boundary_does_not_match_longer_marker(self):
        output = analyse(load("challenge"))
        self.assertEqual(output["decisions"]["short-token"], "relocate-before-sharing")
        self.assertNotIn("package-log", output["observations"][0])

    def test_unlisted_dummy_marker_is_not_detected(self):
        output = analyse(load("challenge"))
        self.assertEqual(set(output["decisions"]), {"short-token", "long-token"})
        self.assertTrue(any("Only exact listed" in value for value in output["limitations"]))

    def test_lowercase_suffix_is_not_an_exact_token(self):
        case = load("challenge")
        case["data"]["files"][1]["lines"] = ["TOKEN=DEMO_ONLY_TOKEN_APPended"]
        case["artifacts"]["draft-config.txt"] = "TOKEN=DEMO_ONLY_TOKEN_APPended\n"
        self.assertEqual(analyse(case)["decisions"]["short-token"], "not-seen-in-supplied-artifacts")

    def test_absence_is_only_absence_from_supplied_artifacts(self):
        self.assertEqual(analyse(load())["decisions"]["unused-token"], "not-seen-in-supplied-artifacts")

    def test_readable_artifact_mismatch_is_rejected(self):
        case = load()
        case["artifacts"]["app-config.txt"] = "different evidence\n"
        with self.assertRaises(ValueError):
            analyse(case)

    def test_real_looking_marker_and_duplicate_marker_rejected(self):
        for marker in ("actual-token", "DEMO_ONLY_TOKEN_EXPORT"):
            with self.subTest(marker=marker):
                case = load()
                case["data"]["secrets"][1]["marker"] = marker
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_embedded_newline_is_rejected(self):
        case = load()
        case["data"]["files"][0]["lines"] = ["first\nsecond"]
        with self.assertRaises(ValueError):
            analyse(case)

    def test_unknown_audience_is_rejected(self):
        case = load()
        case["data"]["files"][0]["audience"] = "probably-private"
        with self.assertRaises(ValueError):
            analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
