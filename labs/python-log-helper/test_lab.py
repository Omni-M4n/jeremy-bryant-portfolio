import copy
import json
from pathlib import Path
import unittest
import lab

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_exact_window(self):
        self.assertEqual(lab.analyse(fixture())["decisions"],{"line-1":"count","line-2":"reject","line-3":"other-outcome","line-4":"outside"})

    def test_repeat_and_distinct(self):
        self.assertEqual(lab.analyse(fixture("changed"))["decisions"]["line-3"],"repeat")
        self.assertEqual(lab.analyse(fixture("challenge"))["decisions"]["line-2"],"count")

    def test_bad_window(self):
        c=fixture(); c["data"]["end"]=c["data"]["start"]
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_conflicting_id(self):
        c=fixture(); raw=c["artifacts"]["events.jsonl"].splitlines()[0]
        c["artifacts"]["events.jsonl"]=raw+"\n"+raw.replace('failure','success')
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_duplicate_key_and_blank_line(self):
        states,counts,rejected=lab.count_lines('{"id":"e1","id":"e2"}\n\n',"2026-01-15T00:01:00Z","2026-01-15T00:03:00Z")
        self.assertEqual(states,{"line-1":"reject","line-2":"reject"})
        self.assertEqual(counts,{})

    def test_no_implicit_timezone(self):
        with self.assertRaises(ValueError): lab.moment("2026-01-15T00:01:00")

if __name__ == "__main__":
    unittest.main()
