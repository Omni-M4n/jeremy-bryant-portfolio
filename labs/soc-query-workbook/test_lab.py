import copy
import json
from pathlib import Path
import unittest
import sqlite3
import tempfile
from unittest.mock import patch
import lab
import operations

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_hand_count_join(self):
        self.assertEqual(lab.analyse(fixture())["decisions"],dict(failures="2",joined="4",linked="2",web="1"))

    def test_account_alone_not_enough(self):
        self.assertEqual(lab.analyse(fixture("changed"))["decisions"]["linked"],"0")

    def test_repeat_deduplicated(self):
        self.assertEqual(lab.analyse(fixture("challenge"))["decisions"]["joined"],"2")

    def test_empty_tables(self):
        c=fixture(); c["data"]={k:[] for k in c["data"]}
        self.assertEqual(set(lab.analyse(c)["decisions"].values()),{"0"})

    def test_status_boundary(self):
        c=fixture(); c["data"]["web"][0]["status"]=399; c["data"]["web"][1]["status"]=400
        self.assertEqual(lab.analyse(c)["decisions"]["web"],"1")
        c["data"]["web"][0]["status"]=True
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_conflict_rejected(self):
        c=fixture(); row=copy.deepcopy(c["data"]["login"][0]); row["outcome"]="success"; c["data"]["login"].append(row)
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_empty_queries_fail_without_changing_database(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);run=root/'run';run.mkdir();db_path=run/'events.sqlite'
            db=sqlite3.connect(db_path)
            db.execute('CREATE TABLE sample (value INTEGER)');db.execute('INSERT INTO sample VALUES (7)');db.commit();db.close()
            before=db_path.read_bytes();query=run/'query.sql'
            with patch.object(lab,'ROOT',root):
                for sql in ('',' \t\n','-- no statement\n','/* no statement */'):
                    query.write_text(sql)
                    with self.subTest(sql=sql), self.assertRaisesRegex(ValueError,'SELECT'):
                        operations.query(db_path,query)
                    self.assertEqual(db_path.read_bytes(),before)
                query.write_text('SELECT value FROM sample')
                self.assertEqual(operations.query(db_path,query),{'columns':['value'],'rows':[(7,)]})
                self.assertEqual(db_path.read_bytes(),before)

if __name__ == "__main__":
    unittest.main()
