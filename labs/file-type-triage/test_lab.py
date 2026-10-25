"""Domain boundaries plus real local operations; no external systems."""
import copy
import json
import os
from pathlib import Path
import unittest
import uuid
import lab
import practice
from foundation_runtime import analyse_checked, read_json, validate_case, prepare

def case(name='guided'):
    return read_json(lab.ROOT/'fixtures'/f'{name}.json')

class ContractTests(unittest.TestCase):
    def test_reference_cases_are_explicit(self):
        for name in ('guided','changed','challenge'):
            with self.subTest(name=name):
                actual=analyse_checked(case(name),lab.LAB_ID,lab.analyse)
                expected=read_json(lab.ROOT/'reference'/f'{name}.json')
                self.assertEqual(actual,expected)

    def test_unrecognized_fields_are_rejected(self):
        value=case(); value['data']['unsupported']=True
        with self.assertRaises(ValueError): lab.analyse(value)

    def test_common_malformed_field_types(self):
        locations={
            'evidence-custody':('files','source'),
            'file-type-triage':('files','reported_mime'),
            'file-time-analysis':('snapshots','operation'),
            'deleted-file-recovery':('entries','directory_present'),
            'browser-artifacts':('events','kind'),
            'restore-drill':('expected','size'),
            'pcap-object-reconstruction':('segments','offset'),
            'cross-source-corroboration':('sources','kind')}
        group,key=locations[lab.LAB_ID]
        for malformed in ([],{},None):
            value=case(); value['data'][group][0][key]=malformed
            with self.subTest(value=malformed):
                with self.assertRaises(ValueError): lab.analyse(value)

    def test_missing_fields_are_rejected(self):
        value=case(); value['data'].pop(next(iter(value['data'])))
        with self.assertRaises(ValueError): lab.analyse(value)

    def test_wrong_lab_and_non_synthetic_envelope(self):
        value=case(); value['synthetic']=False
        with self.assertRaises(ValueError): validate_case(value,lab.LAB_ID)
        value=case(); value['lab_id']='another-lab'
        with self.assertRaises(ValueError): validate_case(value,lab.LAB_ID)

    def test_output_paths_are_contained(self):
        for name in ('../outside','run/../outside','run','/tmp/elsewhere','C:/elsewhere','run/a/b','run/con','run/a:stream'):
            # Windows reserved names are refused before creating a folder.
            with self.subTest(name=name):
                with self.assertRaises((ValueError,OSError)): practice.fresh_target(name)

    def test_prepare_refuses_traversal(self):
        with self.assertRaises(ValueError):
            prepare(lab.ROOT,lab.LAB_ID,lab.analyse,'guided','../outside')

    def test_symbolic_output_link_is_refused(self):
        token=uuid.uuid4().hex[:10]
        target=lab.ROOT/'run'/('link-target-'+token)
        target.parent.mkdir(exist_ok=True); target.mkdir()
        link=lab.ROOT/'run'/('link-'+token)
        try: link.symlink_to(target,target_is_directory=True)
        except OSError as error: self.skipTest('local symlink creation unavailable: '+str(error.errno))
        with self.assertRaises(ValueError): practice.fresh_target('run/'+link.name)

    def test_hardlinked_input_is_refused(self):
        target=practice.fresh_target('run/hardlink-'+uuid.uuid4().hex[:10])
        source=target/'source'/'item-01.txt'; source.write_bytes(b'local test')
        linked=target/'output'/'item-01.txt'
        try: os.link(source,linked)
        except OSError as error: self.skipTest('local hardlink creation unavailable: '+str(error.errno))
        with self.assertRaises(ValueError): practice.read_bytes(source)

    def test_practical_operations_preserve_source_and_first_attempt(self):
        for name in ('guided','changed','challenge'):
            output='run/test-'+name+'-'+uuid.uuid4().hex[:10]
            practice.run(name,output)
            receipt=read_json(lab.ROOT/output/'receipt.json')
            self.assertTrue(receipt['source_integrity'])
            self.assertTrue(all(row['unchanged'] for row in receipt['source_integrity']))
            check_practical(self,name,receipt)
            with self.assertRaises(ValueError): practice.run(name,output)

    def test_bad_scenario_is_refused_before_writes(self):
        with self.assertRaises(ValueError): practice.run('../other','run/never-created')

def check_practical(test,name,receipt):
    rows=receipt['observations']
    if name=='guided':
        test.assertEqual(rows[0]['prefix_hex'][:16],'89504e470d0a1a0a')
        test.assertEqual(rows[0]['size'],69)
    elif name=='changed':
        test.assertEqual(bytes.fromhex(rows[0]['prefix_hex']),b'plain training\n')
        test.assertEqual(bytes.fromhex(rows[1]['prefix_hex']),b'SQLite format 3\x00')
    else: test.assertEqual([row['size'] for row in rows],[4,0])

class DomainTests(unittest.TestCase):
    def test_png_extension_agreement_does_not_require_mime_agreement(self):
        value=case(); row=value['data']['files'][0]; row['name']='item-01.png'
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'png-signature-extension-agrees')
    def test_signature_only_is_a_clue_not_full_validation(self):
        value=case(); row=value['data']['files'][0]; row['prefix_hex']='89504e470d0a1a0a'; row['size']=8
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'png-signature-extension-differs')
    def test_sqlite_extension_agrees(self):
        value=case('changed'); value['data']['files'][1]['name']='item-02.sqlite'
        self.assertEqual(lab.analyse(value)['decisions']['item-02'],'sqlite-signature-extension-agrees')
    def test_incomplete_prefix_and_boolean_size_rejected(self):
        value=case(); value['data']['files'][0]['prefix_hex']='89'
        with self.assertRaises(ValueError): lab.analyse(value)
        value=case(); value['data']['files'][0]['size']=True
        with self.assertRaises(ValueError): lab.analyse(value)
    def test_bad_hex_and_path_in_name(self):
        value=case(); value['data']['files'][0]['prefix_hex']='gg'*16
        with self.assertRaises(ValueError): lab.analyse(value)
        value=case(); value['data']['files'][0]['name']='../sample.png'
        with self.assertRaises(ValueError): lab.analyse(value)

if __name__ == '__main__':
    unittest.main(verbosity=2)
