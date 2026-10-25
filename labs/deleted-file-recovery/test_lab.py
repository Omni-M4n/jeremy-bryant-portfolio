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
    row=receipt['entry']
    expected={'guided':'matches-known-training-file','changed':'candidate-content-differs','challenge':'no-directory-candidate'}
    test.assertEqual(receipt['comparison']['decisions']['item-01'],expected[name])
    if name=='guided': test.assertEqual(bytes.fromhex(row['candidate_hex']),b'Library practice: blue notebook, shelf 4.\n')
    test.assertFalse(receipt['mounted_or_device_accessed'])

class DomainTests(unittest.TestCase):
    def test_cluster_limit(self):
        value=case(); row=value['data']['entries'][0]; row['declared_size']=512; row['candidate_hex']='00'*512
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'candidate-content-differs')
        row['declared_size']=513
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'outside-recovery-model')
    def test_allocated_cluster_is_not_recovered(self):
        value=case(); value['data']['entries'][0]['cluster_allocated']=True
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'outside-recovery-model')
    def test_short_candidate(self):
        value=case(); value['data']['entries'][0]['candidate_hex']='01'
        self.assertEqual(lab.analyse(value)['decisions']['item-01'],'candidate-size-differs')
    def test_absence_contradiction(self):
        value=case('challenge'); value['data']['entries'][0]['candidate_hex']='01'
        with self.assertRaises(ValueError): lab.analyse(value)
    def test_bad_image_and_wrong_geometry(self):
        with self.assertRaises(ValueError): practice.read_deleted(b'not an image')
        image=bytearray(practice.build_image('guided')); image[13]=2
        with self.assertRaises(ValueError): practice.read_deleted(bytes(image))
    def test_fat_disagreement_and_outside_cluster(self):
        image=bytearray(practice.build_image('guided')); image[512+3]=1
        with self.assertRaises(ValueError): practice.read_deleted(bytes(image))
        image=bytearray(practice.build_image('guided')); image[3*512+26]=250
        with self.assertRaises(ValueError): practice.read_deleted(bytes(image))

if __name__ == '__main__':
    unittest.main(verbosity=2)
