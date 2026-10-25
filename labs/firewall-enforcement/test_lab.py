import json
import unittest
from lab import analyse, ROOT

class Checks(unittest.TestCase):
    def case(self,name="guided"):
        return json.loads((ROOT/"fixtures"/(name+".json")).read_text())
    def test_supported_rule_and_rollback(self):
        self.assertEqual(analyse(self.case())["decisions"],{"p01":"permitted-supported","p02":"deny-supported-by-control-and-counter","rollback":"rollback-supported"})
    def test_stopped_service_is_not_rule_evidence(self):
        self.assertEqual(analyse(self.case("changed"))["decisions"]["p02"],"failure-needs-cause-check")
    def test_control_failure_blocks_causal_claim(self):
        d=analyse(self.case("challenge"))["decisions"]
        self.assertEqual(d["p02"],"failure-needs-cause-check");self.assertEqual(d["rollback"],"rollback-not-confirmed")
    def test_valid_rule_miss(self):
        c=self.case();c["data"]["probes"][1].update(during={"listener":True,"outcome":"connect"},hits=0)
        self.assertEqual(analyse(c)["decisions"]["p02"],"deny-not-enforced")
    def test_counter_boundary_and_baseline(self):
        c=self.case();c["data"]["probes"][1]["hits"]=0
        self.assertEqual(analyse(c)["decisions"]["p02"],"failure-needs-cause-check")
        c["data"]["probes"][1]["before"]["outcome"]="timeout"
        self.assertEqual(analyse(c)["decisions"]["p02"],"baseline-not-established")
    def test_hash_alone_does_not_prove_rollback(self):
        c=self.case();c["data"]["rule_removed"]=False
        self.assertEqual(analyse(c)["decisions"]["rollback"],"rollback-not-confirmed")
    def test_reject_contradictory_and_bad_inputs(self):
        for change in (lambda c:c["data"]["probes"][0].update(hits=1),lambda c:c["data"]["probes"][0]["before"].update(listener=False),lambda c:c["data"].update(rule_removed=1),lambda c:c["data"]["probes"][0].update(hits=-1),lambda c:c["data"]["probes"][0].update(expected="deny")):
            c=self.case();change(c)
            with self.assertRaises(ValueError):analyse(c)

if __name__=="__main__":unittest.main()
