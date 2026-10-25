import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).parent/'fixtures'/'guided.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'supported-within-case', 'item-2': 'collect-bounded-evidence'})
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_ids(self):
        c=self.fixture(); c['data']['observations'].append(copy.deepcopy(c['data']['observations'][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_two_track_boundary(self):
        c=self.fixture(); self.assertEqual(lab.analyse(c)['decisions']['item-2'],'collect-bounded-evidence')
        c['data']['observations'][1]['track']='dns'
        with self.assertRaises(ValueError): lab.analyse(c)
    def test_invalid_status_and_claim(self):
        for key,value in [('track','unknown'),('claim','')]:
            c=self.fixture(); c['data']['observations'][0][key]=value
            with self.assertRaises(ValueError): lab.analyse(c)
    def test_supported_does_not_claim_mastery(self):
        c=self.fixture(); c['data']['observations'][1]['claim']='editor-role-absent'
        self.assertEqual(lab.analyse(c)['decisions']['item-2'],'supported-within-case')
        self.assertIn('mastery is not assessed',lab.analyse(c)['limitations'][0])

if __name__=='__main__':
    unittest.main()
