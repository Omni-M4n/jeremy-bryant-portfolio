import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).parent/'fixtures'/'guided.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'within-written-plan-only', 'item-2': 'outside-target-scope'})
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_ids(self):
        c=self.fixture(); c['data']['requests'].append(copy.deepcopy(c['data']['requests'][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_start_and_end(self):
        c = self.fixture(); c['data']['requests'][0]['minute'] = 630
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'outside-time-window')
        c['data']['requests'][0]['minute'] = 600
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'within-written-plan-only')
    def test_approval_is_required(self):
        c = self.fixture(); c['data']['approved'] = False
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'do-not-start-plan-incomplete')
    def test_bad_window_and_boolean(self):
        for key, value in [('end_minute', 600), ('approved', 1), ('allowed', ['scan'])]:
            c = self.fixture(); c['data'][key] = value
            with self.assertRaises(ValueError): lab.analyse(c)

    def test_target_grammar_rejects_urls_and_malformed_names(self):
        invalid = ['https://public.invalid/?scope=.test', 'lab.test/path.test',
                   'lab.test?scope=.test', 'lab.test#scope=.test', 'lab.test:443',
                   'user@lab.test', ' lab.test', 'lab.test\n', 'lab..test', '.test',
                   '-lab.test', 'lab-.test', 'lab_name.test', 'LAB.test',
                   'láb.test', 'lab.test.', 'test', 'lab.example', 'a'*64+'.test',
                   '.'.join(['a'*63]*3 + ['b'*57, 'test'])]
        for target in invalid:
            for location in ('plan', 'request'):
                with self.subTest(target=target, location=location):
                    c = self.fixture()
                    if location == 'plan': c['data']['targets'] = [target]
                    else: c['data']['requests'][0]['target'] = target
                    with self.assertRaises(ValueError): lab.analyse(c)

    def test_valid_subdomain_label_and_total_length_boundaries(self):
        valid = ['audit-2.training.test', '7.test', 'a'*63+'.test',
                 '.'.join(['a'*63]*3 + ['b'*56, 'test'])]
        for target in valid:
            with self.subTest(target=target):
                c = self.fixture(); c['data']['targets'] = [target]
                c['data']['requests'][0]['target'] = target
                self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'within-written-plan-only')

    def test_exact_target_and_decision_precedence(self):
        c = self.fixture(); r = c['data']['requests'][0]
        c['data']['targets'] = ['audit.training.test']
        r.update(target='other.audit.training.test', activity='change-config', minute=630)
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'outside-target-scope')
        r['target'] = 'audit.training.test'
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'outside-activity-scope')
        r['activity'] = 'read-config'
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'outside-time-window')
        c['data']['approved'] = False
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'do-not-start-plan-incomplete')
        c['data']['stop_active'] = True
        self.assertEqual(lab.analyse(c)['decisions']['item-1'], 'stop-and-contact-owner')

if __name__=='__main__':
    unittest.main()
