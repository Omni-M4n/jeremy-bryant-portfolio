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
    first=receipt['timeline'][0]
    test.assertEqual(first['observed_utc'],'2025-01-12T10:02:00Z')
    test.assertEqual(first['corrected_utc'],'' if name=='challenge' else '2025-01-12T10:00:00Z')
    test.assertEqual(receipt['timeline'][1]['collection_note'],'partial-export')

class DomainTests(unittest.TestCase):
    def test_clock_correction_rejects_both_date_overflows(self):
        for observed,error in (('0001-01-01T00:00:00Z',1),('9999-12-31T23:59:59Z',-1)):
            value=case(); value['data']['records'][0]['time']=observed
            value['data']['sources'][0]['clock_error_seconds']=error
            with self.subTest(observed=observed):
                with self.assertRaisesRegex(ValueError,'corrected UTC timestamp'):
                    lab.analyse(value)
                target=practice.fresh_target('run/date-bound-'+uuid.uuid4().hex[:10])
                with self.assertRaisesRegex(ValueError,'corrected UTC timestamp'):
                    practice.perform(target,value)
                self.assertEqual(list((target/'source').iterdir()),[])

    def test_valid_corrected_date_boundaries_keep_four_digit_years(self):
        for observed,error,expected in (('0001-01-01T00:00:01Z',1,'0001-01-01T00:00:00Z'),
                                         ('9999-12-31T23:59:58Z',-1,'9999-12-31T23:59:59Z')):
            value=case(); value['data']['records'][0]['time']=observed
            value['data']['sources'][0]['clock_error_seconds']=error
            target=practice.fresh_target('run/date-valid-'+uuid.uuid4().hex[:10])
            receipt=practice.perform(target,value)
            self.assertEqual(receipt['timeline'][0]['corrected_utc'],expected)

    def test_unpaired_corrected_date_is_also_validated(self):
        value=case(); row=copy.deepcopy(value['data']['records'][0])
        row['id']='item-03'; row['time']='0001-01-01T00:00:00Z'
        value['data']['records'].append(row)
        with self.assertRaisesRegex(ValueError,'corrected UTC timestamp'):
            lab.analyse(value)

    def test_intervals_touch_at_boundary(self):
        value=case(); value['data']['records'][1]['time']='2025-01-12T10:00:02Z'
        self.assertEqual(lab.analyse(value)['decisions']['pair-01'],'link-supported-within-clock-bounds')
        value['data']['records'][1]['time']='2025-01-12T10:00:03Z'
        self.assertEqual(lab.analyse(value)['decisions']['pair-01'],'time-conflict')
    def test_missing_identifier_does_not_link_on_time(self):
        value=case(); value['data']['records'][1]['request_id']=None
        self.assertEqual(lab.analyse(value)['decisions']['pair-01'],'insufficient-link')
    def test_content_conflict(self):
        value=case(); value['data']['records'][1]['object_sha256']='0'*64
        self.assertEqual(lab.analyse(value)['decisions']['pair-01'],'content-conflict')
    def test_negative_clock_error(self):
        value=case(); value['data']['sources'][0]['clock_error_seconds']=-1; value['data']['records'][0]['time']='2025-01-12T10:00:00Z'
        self.assertEqual(lab.analyse(value)['decisions']['pair-01'],'link-supported-within-clock-bounds')
    def test_unknown_source_and_same_source_pair(self):
        value=case(); value['data']['records'][0]['source']='source-99'
        with self.assertRaises(ValueError): lab.analyse(value)
        value=case(); value['data']['records'][0]['source']='source-02'
        with self.assertRaises(ValueError): lab.analyse(value)
    def test_boolean_uncertainty_rejected(self):
        value=case(); value['data']['sources'][0]['uncertainty_seconds']=True
        with self.assertRaises(ValueError): lab.analyse(value)

if __name__ == '__main__':
    unittest.main(verbosity=2)
