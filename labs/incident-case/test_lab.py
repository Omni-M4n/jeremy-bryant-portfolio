import copy
import json
from pathlib import Path
import unittest
import lab

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_guided_hypothesis(self):
        self.assertEqual(lab.analyse(fixture())["decisions"]["working-hypothesis"],"consistent-with-change")

    def test_destination_changes_hypothesis(self):
        self.assertEqual(lab.analyse(fixture("changed"))["decisions"]["working-hypothesis"],"review-outside-change")

    def test_missing_kind_and_sort(self):
        r=lab.analyse(fixture("challenge"))["decisions"]
        self.assertEqual(r["working-hypothesis"],"request-missing-source")
        self.assertEqual(r["timeline"],"e1,e3,e4")

    def test_end_excluded_and_start_included(self):
        c=fixture(); c["data"]["events"][0]["time"]=c["data"]["change"]["start"]
        self.assertEqual(lab.analyse(c)["decisions"]["working-hypothesis"],"consistent-with-change")
        c["data"]["events"][0]["time"]=c["data"]["change"]["end"]
        self.assertEqual(lab.analyse(c)["decisions"]["working-hypothesis"],"review-outside-change")

    def test_no_approval_requires_owner(self):
        c=fixture(); c["data"]["change"]["approved"]=False
        self.assertEqual(lab.analyse(c)["decisions"]["working-hypothesis"],"request-owner-check")

    def test_duplicate_id_and_unknown_kind_rejected(self):
        for field,value in [("id","e1"),("kind","unknown")]:
            c=fixture(); c["data"]["events"][1][field]=value
            with self.assertRaises(ValueError): lab.analyse(c)

if __name__ == "__main__":
    unittest.main()
