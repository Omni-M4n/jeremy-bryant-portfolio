import copy
import json
from pathlib import Path
import unittest
import lab

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_guided_actions(self):
        self.assertEqual(lab.analyse(fixture())["decisions"],{"action-card":"account-card","continuity":"use-manual-fallback","resumption":"hold-service-resumption"})

    def test_bytes_alone_do_not_resume(self):
        r=lab.analyse(fixture("changed"))
        self.assertEqual(r["decisions"]["resumption"],"hold-service-resumption")
        self.assertIn("uncovered demand=2/hour",r["observations"][2])

    def test_full_gate_case(self):
        self.assertEqual(lab.analyse(fixture("challenge"))["decisions"]["resumption"],"resume-with-owner-release")

    def test_capacity_boundary(self):
        c=fixture(); c["data"]["fallback"]["capacity_per_hour"]=6
        self.assertEqual(lab.analyse(c)["decisions"]["continuity"],"use-manual-fallback")
        c["data"]["fallback"]["capacity_per_hour"]=5
        self.assertEqual(lab.analyse(c)["decisions"]["continuity"],"escalate-capacity")

    def test_authority_and_emergency_priority(self):
        c=fixture(); c["data"]["incident"]["authority"]="pending"
        self.assertEqual(lab.analyse(c)["decisions"]["action-card"],"request-authority")
        c["data"]["incident"]["urgent"]=True
        self.assertEqual(lab.analyse(c)["decisions"]["action-card"],"emergency-escalation")

    def test_missing_evidence_and_wrong_boolean(self):
        c=fixture(); del c["data"]["evidence"]["d1"]
        with self.assertRaises(ValueError): lab.analyse(c)
        c=fixture(); c["data"]["service"]["available"]="false"
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_active_issue_blocks_resumption(self):
        c=fixture("challenge"); c["data"]["incident"]["active"]=True
        self.assertEqual(lab.analyse(c)["decisions"]["resumption"],"hold-service-resumption")

if __name__ == "__main__":
    unittest.main()
