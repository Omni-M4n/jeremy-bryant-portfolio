"""Fixed expected decisions plus independently chosen boundary examples."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab


class RouteTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((lab.ROOT / "fixtures" / f"{name}.json").read_text(encoding="utf-8"))

    def sync(self, case):
        case["artifacts"] = {"snapshot.txt": lab.evidence_text(case["data"])}
        return case

    def test_all_fixed_references(self):
        for name in ("guided", "changed", "challenge"):
            with self.subTest(name=name):
                expected = json.loads((lab.ROOT / "reference" / f"{name}.json").read_text(encoding="utf-8"))
                self.assertEqual(lab.analyse(self.case(name)), expected)

    def test_input_unchanged(self):
        case = self.case()
        before = deepcopy(case)
        lab.analyse(case)
        self.assertEqual(case, before)

    def test_longest_prefix_precedes_metric(self):
        result = lab.analyse(self.case())
        self.assertIn("choose host 198.51.100.77/32, metric 999", result["observations"][1])
        self.assertIn("next-hop/ARP target 192.0.2.253", result["observations"][1])

    def test_same_destination_changes_with_subnet(self):
        self.assertEqual(lab.analyse(self.case())["decisions"]["desk"], "on-link")
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["request-a"], "via-gateway")

    def test_prefix_membership_boundary(self):
        case = self.case("changed")
        case["data"]["requests"] = [{"id": "before", "target": "198.51.100.63"}, {"id": "start", "target": "198.51.100.64"}, {"id": "end", "target": "198.51.100.127"}, {"id": "after", "target": "198.51.100.128"}]
        # These are routed prefixes, not asserted local subnet host ranges.
        notes = lab.analyse(self.sync(case))["observations"]
        for note, route in zip(notes, ("route-d", "route-e", "route-e", "route-d")):
            self.assertIn(f"choose {route} ", note)

    def test_equal_prefix_uses_lower_metric(self):
        case = self.case("challenge")
        case["data"]["routes"][-1]["metric"] = 199
        result = lab.analyse(self.sync(case))
        self.assertEqual(result["decisions"]["request-a"], "via-gateway")
        self.assertIn("choose route-d ", result["observations"][0])

    def test_equal_best_routes_never_use_input_order(self):
        case = self.case("challenge")
        before = lab.analyse(case)
        case["data"]["routes"].reverse()
        self.assertEqual(lab.analyse(self.sync(case)), before)

    def test_no_default_means_no_matching_route(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["request-c"], "no-route")

    def test_dns_unknown_does_not_become_default_route(self):
        self.assertEqual(lab.analyse(self.case())["decisions"]["unknown"], "name-unresolved")

    def test_own_ip_is_local_host(self):
        self.assertEqual(lab.analyse(self.case())["decisions"]["self"], "local-host")

    def test_bad_gateway_rejected(self):
        for gateway in ("198.51.100.1", "192.0.2.10", "192.0.2.0", "192.0.2.255"):
            case = self.case()
            case["data"]["routes"][1]["via"] = gateway
            with self.subTest(gateway=gateway), self.assertRaises(ValueError):
                lab.analyse(self.sync(case))

    def test_wrong_or_missing_connected_route_rejected(self):
        for omit in (True, False):
            case = self.case()
            if omit:
                case["data"]["routes"].pop(0)
            else:
                case["data"]["routes"][0]["destination"] = "192.0.2.0/25"
            with self.subTest(omit=omit), self.assertRaises(ValueError):
                lab.analyse(self.sync(case))

    def test_noncanonical_and_non_documentation_prefix_rejected(self):
        for prefix in ("198.51.100.7/24", "10.0.0.0/8", "192.0.0.0/16"):
            case = self.case()
            case["data"]["routes"][2]["destination"] = prefix
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                lab.analyse(self.sync(case))

    def test_invalid_metric_rejected(self):
        for metric in (True, -1, 10000, "5"):
            case = self.case()
            case["data"]["routes"][1]["metric"] = metric
            with self.subTest(metric=metric), self.assertRaises(ValueError):
                lab.analyse(self.sync(case))

    def test_duplicate_ids_rejected(self):
        for group in ("interfaces", "routes", "requests"):
            case = self.case()
            case["data"][group].append(deepcopy(case["data"][group][0]))
            with self.subTest(group=group), self.assertRaises(ValueError):
                lab.analyse(self.sync(case))

    def test_bad_input_and_artifact_rejected(self):
        case = self.case()
        case["data"]["extra"] = True
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case()
        case["artifacts"]["snapshot.txt"] += "stale row\n"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_local_network_and_broadcast_targets_rejected(self):
        for target in ("192.0.2.0", "192.0.2.127"):
            case = self.case("changed")
            case["data"]["requests"][0]["target"] = target
            with self.subTest(target=target), self.assertRaises(ValueError): lab.analyse(self.sync(case))

    def test_unlisted_name_and_public_address_rejected(self):
        for target in ("missing.test", "8.8.8.8"):
            case = self.case()
            case["data"]["requests"][0]["target"] = target
            with self.subTest(target=target), self.assertRaises(ValueError): lab.analyse(self.sync(case))

    def test_independent_metadata_uses_neutral_titles_and_ids(self):
        for key, suffix in (("changed", "B"), ("challenge", "C")):
            case = self.case(key)
            self.assertEqual(case["title"], "Route snapshot " + suffix)
            for route in case["data"]["routes"]:
                self.assertRegex(route["id"], r"^route-[a-z]$")
            for request in case["data"]["requests"]:
                self.assertRegex(request["id"], r"^request-[a-z]$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
