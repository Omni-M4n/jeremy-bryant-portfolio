import copy
import json
from pathlib import Path
import unittest
import lab

def fixture(cid="guided"):
    return json.loads((Path(__file__).parent / "fixtures" / (cid + ".json")).read_text(encoding="utf-8"))

class LabTests(unittest.TestCase):
    def test_gap_is_separate_from_delay(self):
        r=lab.analyse(fixture())["decisions"]
        self.assertEqual(r["b/coverage"],"gap-at-cutoff")
        self.assertEqual(r["b/delivery"],"within-budget")

    def test_late_complete_case(self):
        r=lab.analyse(fixture("changed"))["decisions"]
        self.assertEqual(r["a/coverage"],"complete-at-cutoff")
        self.assertEqual(r["a/delivery"],"late-delivery")

    def test_unknown_and_boundary(self):
        r=lab.analyse(fixture("challenge"))["decisions"]
        self.assertEqual(r["a/coverage"],"source-unverified")
        self.assertEqual(r["b/delivery"],"within-budget")

    def test_future_arrival_rejected(self):
        c=fixture(); c["data"]["intervals"][1]["received"][0]["ingested_at"]="2026-01-15T00:05:01Z"
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_inconsistent_source_rejected(self):
        c=fixture(); c["data"]["intervals"][1]["source_ids"]=[]
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_overlap_rejected(self):
        c=fixture(); c["data"]["intervals"][1]["start"]="2026-01-15T00:00:30Z"
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_exact_end_excluded(self):
        c=fixture(); c["data"]["intervals"][1]["received"][0]["event_at"]=c["data"]["intervals"][1]["end"]
        with self.assertRaises(ValueError): lab.analyse(c)

if __name__ == "__main__":
    unittest.main()
