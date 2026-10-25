import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).parent/'fixtures'/'guided.json').read_text(encoding='utf-8'))
    def test_guided_independent_literal_decisions(self):
        self.assertEqual(lab.analyse(self.fixture())['decisions'],{'item-1': 'seeded-values-removed', 'item-2': 'listed-claims-preserved'})
    def test_input_is_unchanged(self):
        c=self.fixture(); before=copy.deepcopy(c); lab.analyse(c); self.assertEqual(c,before)
    def test_unsupported_field(self):
        c=self.fixture(); c['data']['extra']=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_repeated_values_and_claims(self):
        c=self.fixture(); out=lab.redact(c)
        self.assertEqual(out.count('[REMOVED-1]'),2)
        self.assertIn('status=403',out)
        self.assertNotIn('DEMO-TOKEN-418',out)
    def test_overlap_absent_and_reserved(self):
        for change in ('overlap','absent','marker'):
            c=self.fixture()
            if change=='overlap': c['data']['keep']=['DEMO-TOKEN-418']
            elif change=='absent': c['data']['remove']=['absent-value']
            else: c['artifacts']['record.txt']+='[REMOVED-1]'
            with self.assertRaises(ValueError): lab.redact(c)
    def test_copy_preserves_original_and_refuses_overwrite(self):
        import tempfile
        from unittest.mock import patch
        import practice
        from foundation_runtime import encoded
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); folder=root/'run'/'trial'; folder.mkdir(parents=True)
            c=self.fixture(); (folder/'case.json').write_bytes(encoded(c))
            original=c['artifacts']['record.txt'].encode(); (folder/'record.txt').write_bytes(original)
            with patch.object(practice,'ROOT',root):
                receipt=practice.make_copy('run/trial')
                self.assertEqual(receipt['original_before_sha256'],receipt['original_after_sha256'])
                self.assertEqual((folder/'record.txt').read_bytes(),original)
                with self.assertRaises(ValueError): practice.make_copy('run/trial')
    def test_tampered_original_and_escape_refused(self):
        import tempfile
        from unittest.mock import patch
        import practice
        from foundation_runtime import encoded
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); folder=root/'run'/'trial'; folder.mkdir(parents=True)
            c=self.fixture(); (folder/'case.json').write_bytes(encoded(c))
            (folder/'record.txt').write_text('changed',encoding='utf-8')
            with patch.object(practice,'ROOT',root):
                with self.assertRaises(ValueError): practice.make_copy('run/trial')
                with self.assertRaises(ValueError): practice.make_copy('../outside')
            self.assertFalse((folder/'excerpt.txt').exists())

if __name__=='__main__':
    unittest.main()
