import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).parent/'fixtures'/'guided.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'configured-only;listed-service-checks-present', 'item-2': 'path-reachable;listed-service-checks-present', 'item-3': 'configured-only;listed-service-checks-present'})
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_ids(self):
        c=self.fixture(); c['data']['paths'].append(copy.deepcopy(c['data']['paths'][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_permission_independent_of_location(self):
        c=self.fixture(); c['data']['paths'][0]['resource_check']=False
        self.assertEqual(lab.analyse(c)['decisions']['item-1'],'configured-only;review-resource-permission')
    def test_conflicting_observation_is_evidence(self):
        c=self.fixture(); c['data']['paths'][0]['observed']='reachable'
        self.assertIn('configuration-observation-conflict',lab.analyse(c)['decisions']['item-1'])
    def test_bad_inputs(self):
        for key,value in [('observed','safe'),('resource_check',1),('destination','real.example')]:
            c=self.fixture(); c['data']['paths'][0][key]=value
            with self.assertRaises(ValueError): lab.analyse(c)

if __name__=='__main__':
    unittest.main()
