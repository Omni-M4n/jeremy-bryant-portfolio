import copy
import json
import unittest
import lab

def sample(): return json.loads((lab.ROOT / "fixtures/guided.json").read_text())

class BaselineTests(unittest.TestCase):
    def test_freshness_boundary(self):
        c=sample();c["data"]["controls"][0]["observed_on"]="2026-10-18"
        self.assertEqual(lab.analyse(c)["decisions"]["c1"],"matches-requirement")
        c["data"]["controls"][0]["observed_on"]="2026-10-17"
        self.assertEqual(lab.analyse(c)["decisions"]["c1"],"recheck-stale")

    def test_zero_lock_is_off(self):
        c=sample();c["data"]["controls"][3]["observed"]=0
        self.assertEqual(lab.analyse(c)["decisions"]["c4"],"change-needed")
        c["data"]["controls"][3]["observed"]=300
        self.assertEqual(lab.analyse(c)["decisions"]["c4"],"matches-requirement")
        c["data"]["controls"][3]["observed"]=301
        self.assertEqual(lab.analyse(c)["decisions"]["c4"],"change-needed")

    def test_exception_date_and_stale_precedence(self):
        c=sample();c["data"]["controls"][2]["observed"]=False
        c["data"]["exceptions"]=[{"control_id":"c3","reason":"Supervised setup","approved_by":"reviewer","expires_on":"2026-10-25"}]
        self.assertEqual(lab.analyse(c)["decisions"]["c3"],"exception-active")
        c["data"]["exceptions"][0]["expires_on"]="2026-10-24"
        self.assertEqual(lab.analyse(c)["decisions"]["c3"],"exception-expired")
        c["data"]["controls"][2]["observed_on"]="2026-10-01"
        self.assertEqual(lab.analyse(c)["decisions"]["c3"],"recheck-stale")

    def test_invalid_and_missing(self):
        for index,change in [(0,{"observed":1}),(1,{"observed":True}),(0,{"observed_on":"2026-10-26"}),(3,{"required":0}),(0,{"observed":None})]:
            c=sample();c["data"]["controls"][index].update(change)
            with self.assertRaises(ValueError): lab.analyse(c)
        c=sample();c["data"]["controls"][0].update(observed=None,observed_on="",evidence="")
        self.assertEqual(lab.analyse(c)["decisions"]["c1"],"not-observed")

    def test_no_input_change(self):
        c=sample();before=copy.deepcopy(c);lab.analyse(c);self.assertEqual(c,before)

if __name__ == "__main__": unittest.main()
