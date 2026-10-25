"""Independent boundary and invalid-input tests for iam-explicit-deny."""
import copy
import json
from pathlib import Path
import unittest
import lab


class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((Path(__file__).parent / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_analysis_preserves_input(self):
        c = self.case()
        before = copy.deepcopy(c)
        lab.analyse(c)
        self.assertEqual(c, before)

    def test_precedence_is_order_independent(self):
        c = self.case()
        c["data"]["statements"].reverse()
        self.assertEqual(lab.analyse(c)["decisions"], {"q1": "allow", "q2": "explicit-deny", "q3": "implicit-deny"})

    def test_no_grants(self):
        c = self.case()
        c["data"]["statements"] = []
        self.assertEqual(set(lab.analyse(c)["decisions"].values()), {"implicit-deny"})

    def test_exact_name_does_not_match_suffix(self):
        c = self.case("challenge")
        self.assertEqual(lab.analyse(c)["decisions"]["q3"], "allow")

    def test_reject_condition(self):
        c = self.case()
        c["data"]["statements"][0]["Condition"] = {}
        with self.assertRaises(ValueError):
            lab.analyse(c)

    def test_reject_nonterminal_wildcard(self):
        c = self.case()
        c["data"]["statements"][0]["resource"] = "arn:aws:s3:::practice-library/*/x"
        with self.assertRaises(ValueError):
            lab.analyse(c)

    def test_reject_duplicate_id_and_unsupported_action(self):
        for field, value in [("id", "q1"), ("action", "s3:ListBucket")]:
            c = self.case()
            c["data"]["requests"][1][field] = value
            with self.assertRaises(ValueError):
                lab.analyse(c)


if __name__ == "__main__":
    unittest.main()
