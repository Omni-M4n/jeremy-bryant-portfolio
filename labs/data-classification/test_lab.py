import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self, scenario='guided'):
        return json.loads((Path(__file__).parent/'fixtures'/f'{scenario}.json').read_text(encoding='utf-8'))
    def reference(self, scenario):
        return json.loads((Path(__file__).parent/'reference'/f'{scenario}.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'confidential;retain-until-review;share-as-approved;no-receipt', 'item-2': 'public;retain-until-review;share-as-approved;no-receipt'})
    def test_all_three_references_remain_exact(self):
        for scenario in ('guided', 'changed', 'challenge'):
            with self.subTest(scenario=scenario):
                self.assertEqual(lab.analyse(self.fixture(scenario)), self.reference(scenario))
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_ids(self):
        c=self.fixture(); c['data']['records'].append(copy.deepcopy(c['data']['records'][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_exact_retention_boundary(self):
        c=self.fixture(); c['data']['records'][0]['age_days']=30
        self.assertIn('disposal-due',lab.analyse(c)['decisions']['item-1'])
        c['data']['records'][0]['hold']=True
        self.assertIn('retain-on-hold',lab.analyse(c)['decisions']['item-1'])
    def test_conflicts(self):
        for key,value in [('public',True),('age_days',-1),('needed',['unknown'])]:
            c=self.fixture(); c['data']['records'][0][key]=value
            with self.assertRaises(ValueError): lab.analyse(c)
    def test_early_disposal(self):
        c=self.fixture(); c['data']['records'][0]['disposal']='all-listed-copies'
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_missing_context_is_rejected(self):
        c=self.fixture(); del c['context']
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_extra_context_field_is_rejected(self):
        c=self.fixture(); c['context']['extra']='unsupported'
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_missing_question_is_rejected(self):
        c=self.fixture(); del c['context']['question']
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_empty_question_is_rejected(self):
        c=self.fixture(); c['context']['question']='  '
        with self.assertRaises(ValueError): lab.analyse(c)

if __name__=='__main__':
    unittest.main()
