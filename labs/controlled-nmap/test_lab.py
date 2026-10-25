import json
import unittest
from lab import analyse, ROOT

class Checks(unittest.TestCase):
    def case(self,name="guided"):
        return json.loads((ROOT/"fixtures"/(name+".json")).read_text())
    def test_guided(self):
        d=analyse(self.case())["decisions"]
        self.assertEqual(d["s01"],"open-listener-corroborated;label-probe-consistent")
        self.assertEqual(d["s02"],"closed-consistent-with-snapshot")
    def test_filtered_is_not_closed(self):
        self.assertEqual(analyse(self.case("changed"))["decisions"]["s01"],"inconclusive-filtered")
    def test_table_label_unconfirmed(self):
        self.assertEqual(analyse(self.case("challenge"))["decisions"]["s01"],"open-listener-corroborated;label-unconfirmed")
    def test_valid_alternatives_and_conflicting_evidence(self):
        c=self.case();c["data"]["scans"][0]["label"]="ssh"
        self.assertEqual(analyse(c)["decisions"]["s01"],"open-listener-corroborated;label-disagreement")
        c["data"]["scans"][0].update(state="closed",label="",method="none")
        self.assertEqual(analyse(c)["decisions"]["s01"],"snapshot-disagreement")
    def test_scope_boundary_ports(self):
        c=self.case();c["data"]["ports"]=[1,8001,8002];c["data"]["listeners"][0]["port"]=1;c["data"]["scans"][0]["port"]=1
        self.assertTrue(analyse(c)["decisions"]["s01"].startswith("open-listener"))
    def test_reject_bad_scope_and_contradictions(self):
        for change in (lambda c:c["data"]["scans"][0].update(target="192.0.2.11"),lambda c:c["data"]["scans"][0].update(port=True),lambda c:c["data"]["scans"][1].update(label="http",method="probe"),lambda c:c["data"]["scans"].append(c["data"]["scans"][0]),lambda c:c["data"]["scans"][0].update(state="open|filtered")):
            c=self.case();change(c)
            with self.assertRaises(ValueError):analyse(c)

if __name__=="__main__":unittest.main()
