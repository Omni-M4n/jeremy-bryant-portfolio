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

    def test_verified_signature_does_not_clear_context_trigger(self):
        result = lab.analyse(self.case())["decisions"]
        self.assertEqual(result["p3"], "prioritise-context-review")
        self.assertEqual(result["p1"], "no-modelled-triage-trigger")

    def test_approval_changes_context_not_malware_verdict(self):
        case = self.case()
        case["data"]["processes"][2]["approved_change"] = True
        self.assertEqual(lab.analyse(case)["decisions"]["p3"], "documented-change-context")

    def test_unsigned_without_other_signal_needs_evidence(self):
        case = self.case()
        case["data"]["processes"][3]["location"] = "program"
        self.assertEqual(lab.analyse(case)["decisions"]["p4"], "signature-context-incomplete")

    def test_rejects_missing_parent(self):
        case = self.case()
        case["data"]["processes"][2]["parent"] = "not-collected"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_rejects_cycle_and_duplicate_ids(self):
        for mutation in ("cycle", "duplicate"):
            case = self.case()
            if mutation == "cycle": case["data"]["processes"][0]["parent"] = "p3"
            else: case["data"]["processes"][3]["id"] = "p2"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): lab.analyse(case)

    def test_rejects_unknown_role_and_nonboolean_approval(self):
        for key, value in (("role", "trusted"), ("approved_change", "yes")):
            case = self.case(); case["data"]["processes"][0][key] = value
            with self.subTest(field=key), self.assertRaises(ValueError): lab.analyse(case)

if __name__ == "__main__":
    unittest.main()
