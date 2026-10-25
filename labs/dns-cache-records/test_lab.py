"""Domain checks with hand-reasoned boundaries, not generated references."""
import copy
import json
import unittest
from lab import analyse, ROOT

class Checks(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((ROOT / "fixtures" / (name + ".json")).read_text())
    def test_alias_and_record_purposes(self):
        self.assertEqual(analyse(self.case())["decisions"], {"q01":"cached-answer:192.0.2.20", "q02":"cached-answer:2001:db8::20", "q03":"cached-answer:10 mail.school.test"})
    def test_exact_expiry_and_direct_lookup(self):
        result=analyse(self.case("changed"))["decisions"]
        self.assertEqual(result["q01"], "refresh-required")
        self.assertEqual(result["q02"], "cached-answer:192.0.2.20")
    def test_ttl_zero_and_one_second_left(self):
        c=self.case(); c["data"]["records"][0]["ttl"]=31
        self.assertEqual(analyse(c)["decisions"]["q01"], "cached-answer:192.0.2.20")
        c["data"]["records"][0]["ttl"]=0
        self.assertEqual(analyse(c)["decisions"]["q01"], "refresh-required")
    def test_negative_scope_and_boundary(self):
        self.assertEqual(analyse(self.case("challenge"))["decisions"], {"q01":"cached-negative:NXDOMAIN", "q02":"refresh-required", "q03":"refresh-required", "q04":"cached-negative:NODATA"})
    def test_valid_nodata_other_type_answer(self):
        c=self.case("challenge"); c["data"]["records"]=[dict(owner="mail.school.test",type="A",value="192.0.2.9",received=0,ttl=90)]
        self.assertEqual(analyse(c)["decisions"]["q03"], "cached-answer:192.0.2.9")
    def test_malformed_and_contradictory(self):
        for alter in (lambda c:c["data"]["records"][0].update(value="www.school.test"), lambda c:c["data"]["records"][1].update(ttl=True), lambda c:c["data"]["records"][1].update(value="8.8.8.8"), lambda c:c["data"]["queries"][0].update(at=-1), lambda c:c["data"].update(extra=1)):
            c=self.case(); alter(c)
            with self.assertRaises(ValueError): analyse(c)
    def test_no_input_change(self):
        c=self.case(); original=copy.deepcopy(c); analyse(c); self.assertEqual(c,original)

if __name__ == "__main__": unittest.main()
