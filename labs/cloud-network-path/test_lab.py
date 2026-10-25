"""Independent boundary and invalid-input tests for cloud-network-path."""
import copy
import json
from pathlib import Path
import unittest
import lab


class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((Path(__file__).parent / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_analysis_preserves_input(self):
        c = self.case()
        before = copy.deepcopy(c)
        lab.analyse(c)
        self.assertEqual(c, before)

    def test_direct_path_checks(self):
        self.assertEqual(lab.analyse(self.case())["decisions"], {"q1": "reachable-in-model", "q2": "inbound-not-allowed", "q3": "no-public-address"})

    def test_specific_route_overrides_default(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["q1"], "return-route-missing")

    def test_private_endpoint_via_declared_relay(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["q2"], "reachable-via-relay")

    def test_equivalent_route_destinations_rejected_in_both_orders(self):
        for alternate in ("0.0.0.0/0.0.0.0", "10.44.0.0/255.255.0.0"):
            for reverse in (False, True):
                with self.subTest(alternate=alternate, reverse=reverse):
                    c = self.case()
                    routes = c["data"]["endpoints"][0]["routes"]
                    routes.append({"cidr": alternate, "target": "blackhole"})
                    if reverse:
                        routes.reverse()
                    with self.assertRaisesRegex(ValueError, "duplicate route"):
                        lab.analyse(c)

    def test_unique_netmask_routes_keep_longest_prefix_in_both_orders(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                c = self.case()
                routes = c["data"]["endpoints"][0]["routes"]
                routes[1]["cidr"] = "0.0.0.0/0.0.0.0"
                routes.append({"cidr": "192.0.2.0/255.255.255.0", "target": "blackhole"})
                if reverse:
                    routes.reverse()
                self.assertEqual(lab.analyse(c)["decisions"]["q1"], "return-route-missing")

    def test_ambiguous_relay_request_rejected_in_both_orders(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                c = self.case("challenge")
                c["data"]["relays"].append({"via": "e1", "listen": 8443, "target": "e2", "port": 8080})
                if reverse:
                    c["data"]["relays"].reverse()
                with self.assertRaisesRegex(ValueError, "ambiguous relay request mapping"):
                    lab.analyse(c)

    def test_distinct_relay_requests_use_their_own_listener(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                c = self.case("challenge")
                c["data"]["relays"].append({"via": "e1", "listen": 8443, "target": "e2", "port": 8081})
                c["data"]["requests"].append({"id": "q4", "source": "192.0.2.8", "target": "e2", "port": 8081, "via": "e1"})
                if reverse:
                    c["data"]["relays"].reverse()
                decisions = lab.analyse(c)["decisions"]
                self.assertEqual(decisions["q2"], "reachable-via-relay")
                self.assertEqual(decisions["q4"], "relay-leg-1:inbound-not-allowed")

    def test_duplicate_listener_still_rejected(self):
        c = self.case("challenge")
        c["data"]["relays"].append({"via": "e1", "listen": 443, "target": "e2", "port": 8081})
        with self.assertRaisesRegex(ValueError, "ambiguous relay listener"):
            lab.analyse(c)

    def test_relay_needs_both_legs(self):
        c = self.case("challenge")
        c["data"]["endpoints"][1]["inbound"] = []
        self.assertEqual(lab.analyse(c)["decisions"]["q2"], "relay-leg-2:inbound-not-allowed")
        c["data"]["endpoints"][0]["inbound"] = []
        self.assertEqual(lab.analyse(c)["decisions"]["q2"], "relay-leg-1:inbound-not-allowed")

    def test_port_boundary_and_no_route(self):
        c = self.case()
        c["data"]["requests"][0]["port"] = 65535
        self.assertEqual(lab.analyse(c)["decisions"]["q1"], "inbound-not-allowed")
        c["data"]["endpoints"][0]["routes"] = []
        self.assertEqual(lab.analyse(c)["decisions"]["q1"], "return-route-missing")

    def test_bad_port_subnet_and_route(self):
        for value in [0, 65536, True]:
            c = self.case()
            c["data"]["requests"][0]["port"] = value
            with self.assertRaises(ValueError):
                lab.analyse(c)
        c = self.case()
        c["data"]["endpoints"][0]["subnet"] = "10.44.2.0/24"
        with self.assertRaises(ValueError):
            lab.analyse(c)
        c = self.case()
        c["data"]["endpoints"][0]["routes"].append(c["data"]["endpoints"][0]["routes"][0].copy())
        with self.assertRaises(ValueError):
            lab.analyse(c)


if __name__ == "__main__":
    unittest.main()
