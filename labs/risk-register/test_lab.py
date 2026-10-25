import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).parent/'fixtures'/'guided.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'high;reduce;review-planned;projection-only', 'item-2': 'low;accept;owner-acceptance-needed;projection-only'})
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_ids(self):
        c=self.fixture(); c['data']['risks'].append(copy.deepcopy(c['data']['risks'][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_bands_and_due_boundary(self):
        c=self.fixture(); r=c['data']['risks'][0]; r.update(likelihood=1,impact=3,likelihood_after=1,impact_after=2,review='2026-10-25')
        self.assertEqual(lab.analyse(c)['decisions']['item-1'],'medium;reduce;review-due;projection-only')
    def test_invalid_scales_and_dates(self):
        for key,value in [('likelihood',0),('impact',True),('review','2026-02-30')]:
            c=self.fixture(); c['data']['risks'][0][key]=value
            with self.assertRaises(ValueError): lab.analyse(c)
    def test_acceptance_does_not_reduce_risk(self):
        c=self.fixture(); c['data']['risks'][0]['treatment']='accept'
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_date_shape_and_calendar_for_both_fields(self):
        invalid = ['20261025', '2026-W43-7', '2026-1-25', '26-10-25',
                   '2026-10-25T00:00:00', ' 2026-10-25', '2026-10-25\n',
                   '２０２６-１０-２５', '2026-02-29', '2026-02-30',
                   '2026-13-01', '2026-00-01', '2026-01-00', '0000-01-01']
        for value in invalid:
            for key in ('as_of', 'review'):
                with self.subTest(key=key, value=value):
                    c = self.fixture()
                    if key == 'as_of': c['data'][key] = value
                    else: c['data']['risks'][0][key] = value
                    with self.assertRaises(ValueError): lab.analyse(c)

    def test_leap_day_and_due_date_boundary(self):
        c = self.fixture(); c['data']['as_of'] = '2024-02-29'
        r = c['data']['risks'][0]; r['review'] = '2024-03-01'
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'high;reduce;review-planned;projection-only')
        r['review'] = '2024-02-29'
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'high;reduce;review-due;projection-only')
        c['data']['as_of'] = '2024-03-01'
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'high;reduce;review-due;projection-only')

if __name__=='__main__':
    unittest.main()
