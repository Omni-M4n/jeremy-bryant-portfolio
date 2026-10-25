import json
import unittest
from lab import analyse, ROOT

class Checks(unittest.TestCase):
    def case(self,name="guided"):
        return json.loads((ROOT/"fixtures"/(name+".json")).read_text())
    def test_distinct_families(self):
        self.assertEqual(analyse(self.case())["decisions"]["s01-parity"],"unequal-observed-reachability")
    def test_same_failure_does_not_prove_same_cause(self):
        d=analyse(self.case("changed"))["decisions"]
        self.assertEqual(d["s01-parity"],"both-observed-not-reachable")
        self.assertEqual(d["s01-ipv6"],"not-reachable-cause-unproven")
    def test_missing_family_is_unknown(self):
        self.assertEqual(analyse(self.case("challenge"))["decisions"]["s01-parity"],"comparison-incomplete")
    def test_valid_both_allowed_and_rule_disagreement(self):
        c=self.case("challenge");c["data"]["services"][0]["ipv6"].update(outcome="connect",configured_rule="allow")
        self.assertEqual(analyse(c)["decisions"]["s01-parity"],"both-observed-reachable")
        c["data"]["services"][0]["ipv6"]["configured_rule"]="deny"
        self.assertEqual(analyse(c)["decisions"]["s01-ipv6"],"reachable-as-intended;rule-observation-disagreement")
    def test_reject_wrong_family_and_contradiction(self):
        for change in (lambda s:s["ipv6"].update(address="192.0.2.20"),lambda s:s["ipv6"].update(listener=False),lambda s:s.update(port=0),lambda s:s["ipv4"].update(outcome="blocked"),lambda s:s.update(extra=True)):
            c=self.case();change(c["data"]["services"][0])
            with self.assertRaises(ValueError):analyse(c)

if __name__=="__main__":unittest.main()
