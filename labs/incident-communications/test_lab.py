import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).parent/'fixtures'/'guided.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'use-confirmed-fact-for-staff', 'item-2': 'label-hypothesis-do-not-present-as-fact', 'item-3': 'assign-action-and-owner'})
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_ids(self):
        c=self.fixture(); c['data']['statements'].append(copy.deepcopy(c['data']['statements'][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_hypothesis_stays_labelled(self):
        c=self.fixture(); c['data']['statements'][0]['status']='hypothesis'
        self.assertEqual(lab.analyse(c)['decisions']['item-1'],'label-hypothesis-do-not-present-as-fact')
    def test_bad_update_and_route(self):
        for key,value in [('next_update_minute',600),('reporting_route','outside.test')]:
            c=self.fixture(); c['data'][key]=value
            with self.assertRaises(ValueError): lab.analyse(c)
    def test_bad_status_and_empty_owner(self):
        for key,value in [('status','probably-true'),('owner','')]:
            c=self.fixture(); c['data']['statements'][0][key]=value
            with self.assertRaises(ValueError): lab.analyse(c)

if __name__=='__main__':
    unittest.main()
