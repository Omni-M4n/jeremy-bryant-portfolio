import copy
import json
from pathlib import Path
import unittest
import lab

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_hand_decisions(self):
        self.assertEqual(lab.analyse(fixture())["decisions"],{"i1":"context-only-use","i2":"seek-origin"})

    def test_expiry_equality(self):
        self.assertEqual(lab.analyse(fixture("changed"))["decisions"]["i1"],"review-expiry")

    def test_shared_and_unspecified(self):
        self.assertEqual(lab.analyse(fixture("challenge"))["decisions"],{"i1":"narrow-scope","i2":"seek-origin"})

    def test_confidence_boundary(self):
        c=fixture(); c["data"]["records"][0]["confidence"]=70
        self.assertEqual(lab.analyse(c)["decisions"]["i1"],"context-only-use")
        c["data"]["records"][0]["confidence"]=69
        self.assertEqual(lab.analyse(c)["decisions"]["i1"],"seek-origin")

    def test_future_report_and_bad_address(self):
        for fields in [dict(reported_at="2026-01-16T00:00:00Z"),dict(type="ipv4",value="127.0.0.1"),dict(confidence=True)]:
            c=fixture(); c["data"]["records"][0].update(fields)
            with self.assertRaises(ValueError): lab.analyse(c)

    def test_conflict_priority(self):
        c=fixture(); c["data"]["records"][1]["contradicted"]=True
        self.assertEqual(lab.analyse(c)["decisions"]["i2"],"resolve-conflict")

    def test_review_date_near_last_supported_year(self):
        for now,expiry,expected in [('9999-12-29','9999-12-30','9999-12-30'),
                                    ('9999-12-01','9999-12-30','9999-12-08'),
                                    ('9999-12-23','9999-12-30','9999-12-30')]:
            c=fixture();c['data']['as_of']=now+'T00:00:00Z'
            row=c['data']['records'][0];row['valid_until']=expiry+'T00:00:00Z'
            c['data']['records']=[row]
            result=lab.analyse(c)
            self.assertEqual(result['decisions'],{'i1':'context-only-use'})
            self.assertIn('review='+expected+'T00:00:00Z',result['observations'][0])

if __name__ == "__main__":
    unittest.main()
