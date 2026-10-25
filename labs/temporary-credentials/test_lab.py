"""Independent boundary and invalid-input tests for temporary-credentials."""
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

    def test_issue_and_expiry_boundaries(self):
        result = lab.analyse(self.case())["decisions"]
        self.assertEqual(result, {"q1": "not-yet-issued", "q2": "allowed-in-model", "q3": "action-not-granted", "q4": "expired"})

    def test_disabled_human_does_not_erase_existing_session(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["q2"], "allowed-in-model")

    def test_cutoff_is_strict_and_not_retroactive(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"], {"q1": "allowed-in-model", "q2": "revoked", "q3": "allowed-in-model", "q4": "expired"})

    def test_disabled_issuer_cannot_mint(self):
        c = self.case()
        c["data"]["humans"][0]["disabled_at"] = 10
        with self.assertRaises(ValueError):
            lab.analyse(c)

    def test_invalid_times(self):
        for value in [True, -1, 1.5]:
            c = self.case()
            c["data"]["requests"][0]["at"] = value
            with self.assertRaises(ValueError):
                lab.analyse(c)
        c = self.case()
        c["data"]["sessions"][0]["expires"] = 10
        with self.assertRaises(ValueError):
            lab.analyse(c)

    def test_unknown_session_and_untrusted_issuer(self):
        c = self.case()
        c["data"]["requests"][0]["session"] = "absent"
        with self.assertRaises(ValueError):
            lab.analyse(c)
        c = self.case()
        c["data"]["roles"][0]["trusted_humans"] = []
        with self.assertRaises(ValueError):
            lab.analyse(c)


if __name__ == "__main__":
    unittest.main()
