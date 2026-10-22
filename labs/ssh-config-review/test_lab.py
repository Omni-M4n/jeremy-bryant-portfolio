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

    def test_first_value_wins_even_when_later_value_looks_better(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["permitrootlogin"], "differs-from-lab-baseline")
        case = self.case("challenge"); case["data"]["config"] = case["data"]["config"].replace("PermitRootLogin yes\nPermitRootLogin no", "PermitRootLogin no\nPermitRootLogin yes")
        self.assertEqual(lab.analyse(case)["decisions"]["permitrootlogin"], "matches-lab-baseline")

    def test_keywords_case_insensitive_but_values_are_not(self):
        case = self.case("changed"); case["data"]["config"] = case["data"]["config"].replace("PermitRootLogin", "pERmitROOTLogin")
        self.assertEqual(lab.analyse(case)["decisions"]["permitrootlogin"], "matches-lab-baseline")
        case["data"]["config"] += "PasswordAuthentication NO\n"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_missing_directives_do_not_assume_defaults(self):
        case = self.case(); case["data"]["config"] = "PermitRootLogin no\n"
        result = lab.analyse(case)["decisions"]
        self.assertEqual(result["passwordauthentication"], "missing-explicit-setting")
        self.assertEqual(result["access-route"], "insufficient-explicit-method-settings")

    def test_rejects_match_include_and_unknown_directives(self):
        for line in ("Match all", "Include /etc/ssh/extra.conf", "X11Forwarding no"):
            case = self.case(); case["data"]["config"] += line + "\n"
            with self.subTest(line=line), self.assertRaises(ValueError): lab.analyse(case)

    def test_numeric_policy_boundary(self):
        for value, expected in ((1,"matches-lab-baseline"),(4,"matches-lab-baseline"),(5,"differs-from-lab-baseline")):
            case = self.case(); case["data"]["config"] = "MaxAuthTries " + str(value) + "\n"
            self.assertEqual(lab.analyse(case)["decisions"]["maxauthtries"], expected)
        for value in ("0", "101", "many"):
            case = self.case(); case["data"]["config"] = "MaxAuthTries " + value + "\n"
            with self.subTest(value=value), self.assertRaises(ValueError): lab.analyse(case)

    def test_no_supported_method_is_not_a_working_login(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["access-route"], "no-supported-method-enabled")
        case = self.case("challenge"); case["data"]["config"] = case["data"]["config"].replace("PasswordAuthentication no", "PasswordAuthentication yes")
        self.assertEqual(lab.analyse(case)["decisions"]["access-route"], "alternative-method-enabled")

    def test_complex_syntax_is_explicitly_rejected(self):
        for line in ('PermitRootLogin "no"', 'PermitRootLogin no # comment', 'PermitRootLogin=no'):
            case = self.case(); case["data"]["config"] = line + "\n"
            with self.subTest(line=line), self.assertRaises(ValueError): lab.analyse(case)

if __name__ == "__main__":
    unittest.main()
