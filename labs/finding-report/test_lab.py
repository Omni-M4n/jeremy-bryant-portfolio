import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).parent/'fixtures'/'guided.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'bounded-correction-supported'})
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_ids(self):
        c=self.fixture(); c['data']['attempts'].append(copy.deepcopy(c['data']['attempts'][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_fix_claim_not_evidence(self):
        c=self.fixture(); c['data']['attempts'][0]['fix_claimed']=False
        self.assertEqual(lab.analyse(c)['decisions']['item-1'],'bounded-correction-supported')
    def test_owner_missing(self):
        c=self.fixture(); c['data']['attempts'][0]['owner_code']=None
        self.assertEqual(lab.analyse(c)['decisions']['item-1'],'legitimate-use-retest-missing')
    def test_contradictions_and_status(self):
        for key,value in [('original_code',403),('retest_other_record',True),('owner_code',600)]:
            c=self.fixture(); c['data']['attempts'][0][key]=value
            with self.assertRaises(ValueError): lab.analyse(c)

if __name__=='__main__':
    unittest.main()
