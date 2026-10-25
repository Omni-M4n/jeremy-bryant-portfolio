import json
import unittest
from lab import analyse, ROOT

class Checks(unittest.TestCase):
    def case(self,name="guided"):
        return json.loads((ROOT/"fixtures"/(name+".json")).read_text())
    def test_split_and_ipv6(self):
        d=analyse(self.case())["decisions"]
        self.assertEqual(d["f01"],"before:local;after:tunnel;intent:met");self.assertEqual(d["f03"],"before:local;after:local;intent:unmet")
    def test_dns_specific_route_exception(self):
        d=analyse(self.case("changed"))["decisions"]
        self.assertEqual(d["f01"],"before:local;after:tunnel;intent:met");self.assertEqual(d["q01"],"before:local;after:local;intent:unmet")
    def test_prefix_before_metric_and_multiple_resolvers(self):
        d=analyse(self.case("challenge"))["decisions"]
        self.assertEqual(d["f01"],"before:local;after:local;intent:unmet");self.assertEqual(d["q01"],"before:local;after:local+tunnel;intent:unmet")
    def test_domain_boundary(self):
        self.assertEqual(analyse(self.case())["decisions"]["q02"],"before:local;after:local;intent:met")
    def test_no_route_and_no_resolver_are_valid_missing_evidence(self):
        c=self.case();c["data"]["after_routes"]=[];c["data"]["after_dns"]=[]
        self.assertEqual(analyse(c)["decisions"]["f01"],"before:local;after:none;intent:unmet");self.assertEqual(analyse(c)["decisions"]["q01"],"before:local;after:none;intent:unmet")
    def test_reject_ties_bad_prefix_and_external_targets(self):
        for change in (lambda c:c["data"]["after_routes"].append(c["data"]["after_routes"][0]),lambda c:c["data"]["after_routes"][0].update(prefix="192.0.2.1/24"),lambda c:c["data"]["flows"][0].update(destination="8.8.8.8"),lambda c:c["data"]["after_routes"][0].update(metric=True),lambda c:c["data"]["queries"][0].update(name="office.example")):
            c=self.case();change(c)
            with self.assertRaises(ValueError):analyse(c)

if __name__=="__main__":unittest.main()
