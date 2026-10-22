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

    def test_numeric_version_comparison_not_lexical(self):
        from lab import version
        self.assertLess(version("1.9.9"), version("1.10.0"))
        self.assertLess(version("2.0.9"), version("2.0.10"))

    def test_introduced_boundary_is_included(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["report-parser"], "affected-validate-path")

    def test_fixed_boundary_is_excluded(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["upload-parser"], "outside-supplied-ranges")

    def test_separate_later_range_is_evaluated(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["new-parser"], "affected-investigate-path")

    def test_development_dependency_is_not_discarded(self):
        self.assertEqual(analyse(load())["decisions"]["asset-builder"], "affected-review-build-exposure")

    def test_no_advisory_is_distinct_from_no_range_match(self):
        self.assertEqual(analyse(load())["decisions"]["theme-helper"], "no-advisory-supplied")
        self.assertEqual(analyse(load("challenge"))["decisions"]["old-parser"], "outside-supplied-ranges")

    def test_unsupported_version_forms_are_rejected(self):
        for version in ("1.2", "01.2.3", "1.2.3-rc.1", "1.2.3+build", "v1.2.3", "1.2.10000", 1.2):
            with self.subTest(version=version):
                case = load()
                case["data"]["components"][0]["version"] = version
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_equal_or_reversed_range_rejected(self):
        for fixed in ("1.9.0", "1.8.9"):
            with self.subTest(fixed=fixed):
                case = load()
                case["data"]["advisories"][0]["fixed"] = fixed
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_empty_reachability_evidence_rejected(self):
        case = load()
        case["data"]["components"][0]["evidence"] = " "
        with self.assertRaises(ValueError):
            analyse(case)

    def test_real_advisory_identifier_is_rejected(self):
        case = load()
        case["data"]["advisories"][0]["id"] = "CVE-2026-0000"
        with self.assertRaises(ValueError):
            analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
