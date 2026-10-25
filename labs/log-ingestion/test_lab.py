import copy
import json
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch
import lab
import operations

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_known_rows(self):
        result = lab.analyse(fixture())
        self.assertEqual(result["decisions"], {"row-1":"import","row-2":"repeat","row-3":"import","row-4":"reject"})

    def test_conflicting_id_stops(self):
        raw = "event_id,timestamp,user,status\ne1,2026-01-01T00:00:00Z,a,success\ne1,2026-01-01T00:00:00Z,a,failure\n"
        with self.assertRaises(ValueError): lab.parse_records(raw,"csv")

    def test_offset_and_day_boundary(self):
        row=dict(id="e1",time="2026-01-01T00:00:00+14:00",account="a",outcome="success")
        self.assertEqual(lab.normalise(row)["time"], "2025-12-31T10:00:00Z")
        row["time"]="2026-01-01T00:00:00+14:01"
        with self.assertRaises(ValueError): lab.normalise(row)

    def test_header_and_duplicate_json_key(self):
        for raw,fmt in [("wrong\na", "csv"), ('[{"id":"e1","id":"e2"}]',"json")]:
            with self.assertRaises(ValueError): lab.parse_records(raw,fmt)

    def test_offset_minutes_not_normalised_silently(self):
        with self.assertRaises(ValueError):
            lab.normalise(dict(id="e1",time="2026-01-01T00:00:00+01:60",account="a",outcome="success"))

    def test_extra_csv_cell_and_missing_account_rejected(self):
        raw="event_id,timestamp,user,status\ne1,2026-01-01T00:00:00Z,a,success,extra\ne2,2026-01-01T00:00:00Z,,success\n"
        records,states,rejected=lab.parse_records(raw,"csv")
        self.assertEqual(records,[])
        self.assertEqual(states,{"row-1":"reject","row-2":"reject"})

    def test_distinct_ids_retained(self):
        self.assertEqual(list(lab.analyse(fixture("challenge"))["decisions"].values()),["import"]*3)

    def test_input_unchanged(self):
        data=fixture(); before=copy.deepcopy(data); lab.analyse(data); self.assertEqual(data,before)

    def test_utc_range_errors_are_rejected_rows(self):
        for stamp in ('0001-01-01T00:00:00+14:00', '9999-12-31T23:59:59-14:00'):
            raw=json.dumps([dict(id='e1',time=stamp,account='a',outcome='success')])
            records,states,rejected=lab.parse_records(raw,'json')
            self.assertEqual(records,[])
            self.assertEqual(states,{'row-1':'reject'})
            self.assertIn('UTC time',rejected[0]['reason'])
        for stamp in ('0001-01-01T14:00:00+14:00','9999-12-31T09:59:59-14:00'):
            row=dict(id='e1',time=stamp,account='a',outcome='success')
            self.assertEqual(len(lab.normalise(row)['time']),20)

    def test_import_keeps_exact_source_bytes(self):
        for newline,final in [(b'\r\n',True),(b'\n',True),(b'\r\n',False)]:
            with self.subTest(newline=newline,final=final), tempfile.TemporaryDirectory() as folder:
                root=Path(folder);run=root/'run';run.mkdir()
                raw=newline.join([b'event_id,timestamp,user,status',b'e1,2026-01-01T00:00:00Z,a,success'])
                if final: raw+=newline
                source=run/'input.csv';source.write_bytes(raw)
                with patch.object(lab,'ROOT',root):
                    result=operations.import_file(source,'csv','run/imported')
                self.assertEqual(result['imported'],1)
                self.assertEqual(source.read_bytes(),raw)
                self.assertEqual((run/'imported/source.txt').read_bytes(),raw)

if __name__ == "__main__":
    unittest.main()
