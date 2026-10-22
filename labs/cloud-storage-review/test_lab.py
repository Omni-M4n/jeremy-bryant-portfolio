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

    def test_acl_still_grants_when_policy_is_removed(self):
        case = load("challenge")
        row = case["data"]["buckets"][2]
        self.assertFalse(row["policy_public_read"])
        self.assertEqual(analyse(case)["decisions"]["forgotten-acl"], "public-read-unapproved")

    def test_account_block_applies_to_approved_site(self):
        case = load()
        case["data"]["account_block_public"] = True
        self.assertEqual(analyse(case)["decisions"]["poster-site"], "blocked-public-grant")

    def test_explicit_deny_overrides_both_grants(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["deny-overrides"], "blocked-public-grant")

    def test_restricted_data_is_not_approved_public_material(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["mislabelled-site"], "public-read-unapproved")

    def test_no_grant_is_distinct_from_blocked_grant(self):
        self.assertEqual(analyse(load("changed"))["decisions"]["no-grant"], "no-public-grant")

    def test_block_removal_reveals_dormant_grant(self):
        case = load()
        case["data"]["buckets"][2]["bucket_block_public"] = False
        self.assertEqual(analyse(case)["decisions"]["archive"], "public-read-unapproved")

    def test_integer_cannot_stand_in_for_boolean(self):
        case = load()
        case["data"]["account_block_public"] = 1
        with self.assertRaises(ValueError):
            analyse(case)

    def test_unknown_class_and_duplicate_ids_are_rejected(self):
        for change in ("unknown-class", "duplicate"):
            with self.subTest(change=change):
                case = load()
                if change == "unknown-class":
                    case["data"]["buckets"][0]["data_class"] = "safe"
                else:
                    case["data"]["buckets"][1]["id"] = "poster-site"
                with self.assertRaises(ValueError):
                    analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
