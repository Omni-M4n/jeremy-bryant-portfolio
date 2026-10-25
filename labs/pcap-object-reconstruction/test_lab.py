"""Domain boundaries plus real local operations; no external systems."""
import copy
import json
import os
from pathlib import Path
import unittest
import uuid
import lab
import practice
import loopback
import socket
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
            first_view=read_json(lab.ROOT/output/'output'/'packet-log.json')
            self.assertEqual(set(first_view),{'parsed_body_segments','exported_bytes','exported_sha256'})
            self.assertEqual(read_json(lab.ROOT/output/'output'/'feedback.json'),receipt['result'])
            with self.assertRaises(ValueError): practice.run(name,output)

    def test_bad_scenario_is_refused_before_writes(self):
        with self.assertRaises(ValueError): practice.run('../other','run/never-created')

def check_practical(test,name,receipt):
    expected={'guided':('complete-matches-known-object',6),'changed':('stream-incomplete',3),'challenge':('conflicting-overlap',2)}
    test.assertEqual(receipt['result']['decisions']['stream'],expected[name][0])
    test.assertEqual(receipt['exported_bytes'],expected[name][1])
    test.assertFalse(receipt['network_used']); test.assertFalse(receipt['live_capture_performed'])
    if name=='guided': test.assertEqual(receipt['exported_sha256'],practice.sha_bytes(b'alpha\n'))

class DomainTests(unittest.TestCase):
    def test_exact_duplicate_and_out_of_order_segments(self):
        value=case(); value['data']['segments'].reverse()
        row=copy.deepcopy(value['data']['segments'][0]); row['id']='item-03'; value['data']['segments'].append(row)
        self.assertEqual(lab.analyse(value)['decisions']['stream'],'complete-matches-known-object')
    def test_complete_wrong_content(self):
        value=case(); value['data']['known_sha256']='0'*64
        self.assertEqual(lab.analyse(value)['decisions']['stream'],'complete-object-differs')
    def test_encrypted_input_is_not_plaintext(self):
        value=case(); value['data']['encrypted']=True; value['data']['segments']=[]
        self.assertEqual(lab.analyse(value)['decisions']['stream'],'encrypted-no-plaintext')
        value['data']['segments']=case()['data']['segments']
        with self.assertRaises(ValueError): lab.analyse(value)
    def test_out_of_bounds_segment(self):
        value=case(); value['data']['segments'][0]['offset']=6
        with self.assertRaises(ValueError): lab.analyse(value)
    def test_checksum_manual_sum_vector(self):
        self.assertEqual(practice.checksum(bytes.fromhex('0001f203f4f5f6f7')),0x220d)
    def test_truncated_record_and_bad_checksum(self):
        raw=practice.make_pcap(case()['data'])
        with self.assertRaises(ValueError): practice.extract(raw[:-1])
        raw=bytearray(raw); raw[-1]^=1
        with self.assertRaises(ValueError): practice.extract(bytes(raw))
    def test_malformed_pcap_header(self):
        with self.assertRaises(ValueError): practice.extract(b'not pcap')

class LoopbackTests(unittest.TestCase):
    def test_actual_transfer_and_closed_listener(self):
        output='run/local-test-'+uuid.uuid4().hex[:10]
        loopback.prepare(output)
        loopback.transfer(output)
        target=lab.ROOT/output
        receipt=read_json(target/'transfer-receipt.json')
        self.assertEqual(receipt['requests'],[{'peer':'127.0.0.1','method':'GET','path':'/dummy.txt'}])
        self.assertEqual((target/'source'/'dummy.txt').read_bytes(),(target/'output'/'client-dummy.txt').read_bytes())
        self.assertTrue(receipt['source_bytes_unchanged'])
        self.assertFalse(receipt['capture_performed_by_helper'])
        with socket.socket() as probe:
            self.assertNotEqual(probe.connect_ex((loopback.HOST,loopback.PORT)),0)
        with self.assertRaises(ValueError): loopback.transfer(output)

    def test_changed_dummy_is_rejected_before_network(self):
        output='run/local-altered-'+uuid.uuid4().hex[:10]
        loopback.prepare(output)
        source=lab.ROOT/output/'source'/'dummy.txt'
        source.chmod(0o600); source.write_bytes(b'changed')
        with self.assertRaises(ValueError): loopback.transfer(output)
        self.assertFalse((lab.ROOT/output/'output'/'client-dummy.txt').exists())

    def test_occupied_port_is_not_reused(self):
        output='run/local-busy-'+uuid.uuid4().hex[:10]
        loopback.prepare(output)
        with socket.socket() as other:
            other.bind((loopback.HOST,loopback.PORT)); other.listen(1)
            with self.assertRaises(OSError): loopback.transfer(output)
        self.assertFalse((lab.ROOT/output/'output'/'client-dummy.txt').exists())

    def test_unprepared_and_external_paths_rejected(self):
        for output in ('../outside','run/a/b','C:/elsewhere','run/not-prepared-'+uuid.uuid4().hex[:8]):
            with self.subTest(output=output):
                with self.assertRaises(ValueError): loopback.transfer(output)

if __name__ == '__main__':
    unittest.main(verbosity=2)
