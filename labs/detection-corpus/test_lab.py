import copy
import json
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch
import lab
import operations

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_hand_matrix(self):
        result=lab.analyse(fixture())
        self.assertEqual(result["decisions"]["r3/tune"],"tp=2,fp=1,fn=0,tn=1")
        self.assertEqual(result["decisions"]["r5/holdout"],"tp=1,fp=1,fn=1,tn=1")

    def test_threshold_inclusive(self):
        c=fixture(); c["data"]["events"]=[dict(id="a1",failures=3,label="exercise",partition="tune"),dict(id="b1",failures=5,label="routine",partition="holdout")]
        r=lab.analyse(c)["decisions"]
        self.assertEqual(r["r3/tune"],"tp=1,fp=0,fn=0,tn=0")
        self.assertEqual(r["r5/holdout"],"tp=0,fp=1,fn=0,tn=0")

    def test_zero_denominator_not_zero_rate(self):
        r=lab.analyse(fixture("challenge"))
        self.assertIn("misses=undefined(0/0)",r["observations"][0])

    def test_duplicate_across_partitions_rejected(self):
        c=fixture(); c["data"]["events"][-1]["id"]="a1"
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_invalid_count_and_unknown_label(self):
        for field,value in [("failures",True),("label","unknown")]:
            c=fixture(); c["data"]["events"][0][field]=value
            with self.assertRaises(ValueError): lab.analyse(c)

    def test_missing_partition(self):
        c=fixture(); c["data"]["events"]=[r for r in c["data"]["events"] if r["partition"]=="tune"]
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_tune_choice_holdout_order_and_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);run=root/'run';run.mkdir();path=run/'case.json'
            path.write_text(json.dumps(fixture()));before=path.read_bytes()
            with patch.object(lab,'ROOT',root):
                tune=operations.view(path,'tune')
                self.assertTrue(all(r['partition']=='tune' for r in tune['events']))
                self.assertNotIn('holdout',json.dumps(tune))
                with self.assertRaises(ValueError): operations.view(path,'holdout')
                operations.choose(path,5,'Misses and false alarms have different costs.')
                first=(run/'choice.json').read_bytes()
                with self.assertRaises(FileExistsError): operations.choose(path,3,'A revised choice')
                self.assertEqual((run/'choice.json').read_bytes(),first)
                holdout=operations.view(path,'holdout')
                self.assertEqual(holdout['chosen_threshold'],5)
                self.assertTrue(all(r['partition']=='holdout' for r in holdout['events']))
                self.assertEqual(path.read_bytes(),before)
                changed=fixture();changed['data']['events'][0]['failures']+=1
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError,'changed'): operations.view(path,'holdout')

    def test_choice_validation_leaves_no_record(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);run=root/'run';run.mkdir();path=run/'case.json'
            path.write_text(json.dumps(fixture()))
            with patch.object(lab,'ROOT',root):
                for threshold,reason in [(4,'A reason'),(True,'A reason'),(3,' '),(3,'a'*501)]:
                    with self.assertRaises(ValueError): operations.choose(path,threshold,reason)
                    self.assertFalse((run/'choice.json').exists())

if __name__ == "__main__":
    unittest.main()
