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
    before,after=receipt['before'],receipt['after']
    test.assertEqual(before['sha256']==after['sha256'],name!='challenge')
    if name in {'guided','challenge'}: test.assertEqual(before['mtime_ns'],after['mtime_ns'])
    if name=='changed': test.assertNotEqual(before['mtime_ns'],after['mtime_ns'])
    test.assertIn('birthtime_ns',after)

class DomainTests(unittest.TestCase):
    def test_one_nanosecond_is_different(self):
        value=case(); value['data']['snapshots'][0]['after_mtime_ns']+=1
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'content-equal-time-differs')
    def test_both_fields_change(self):
        value=case('challenge'); value['data']['snapshots'][0]['after_mtime_ns']+=1
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'content-and-time-differ')
    def test_time_can_move_back_without_proving_intent(self):
        value=case(); value['data']['snapshots'][0]['after_mtime_ns']-=100
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'content-equal-time-differs')
    def test_bad_number_and_unknown_operation(self):
        value=case(); value['data']['snapshots'][0]['before_mtime_ns']=True
        with self.assertRaises(ValueError): lab.analyse(value)
        value=case(); value['data']['snapshots'][0]['operation']='system-clock-change'
        with self.assertRaises(ValueError): lab.analyse(value)
    def test_bad_hash_and_duplicate_ids(self):
        value=case(); value['data']['snapshots'][0]['before_sha256']='no'
        with self.assertRaises(ValueError): lab.analyse(value)
        value=case(); value['data']['snapshots']*=2
        with self.assertRaises(ValueError): lab.analyse(value)

if __name__ == '__main__':
    unittest.main(verbosity=2)
