
"""Meaningful boundaries and malformed-input checks; fixtures have fixed answers."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab


class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((lab.ROOT / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def sync(self, case):
        if lab.LAB_ID == "asset-discovery":
            case["artifacts"] = {"scan.xml": case["data"]["nmap_xml"]}
        elif lab.LAB_ID == "tcp-handshake":
            case["artifacts"] = {"packets.csv": lab.packet_csv(case["data"]["flows"])}
        elif lab.LAB_ID == "http-header-review":
            case["artifacts"] = {"headers.txt": lab.rendered(case["data"]["responses"])}
        elif lab.LAB_ID == "email-triage":
            case["artifacts"] = {"headers.txt": lab.rendered(case["data"]["messages"])}
        return case

    def test_fixed_reference_cases(self):
        for name in ("guided", "changed", "challenge"):
            with self.subTest(case=name):
                expected = json.loads((lab.ROOT / "reference" / (name + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(lab.analyse(self.case(name)), expected)

    def test_analysis_preserves_input(self):
        case = self.case()
        before = deepcopy(case)
        lab.analyse(case)
        self.assertEqual(case, before)

    def test_unknown_data_field_rejected(self):
        case = self.case()
        case["data"]["unexpected"] = True
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_missing_envelope_rejected(self):
        case = self.case()
        del case["synthetic"]
        with self.assertRaises(ValueError):
            lab.analyse(case)


    def test_filtered_does_not_become_closed_or_removed(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["192.0.2.10"], "expected-service-not-observed")

    def test_open_unexpected_service_wins_but_missing_is_reported(self):
        output = lab.analyse(self.case("challenge"))
        self.assertEqual(output["decisions"]["192.0.2.10"], "unapproved-service-observed")
        self.assertIn("expected-not-observed-open=[443]", output["observations"][0])

    def test_unregistered_down_is_not_an_observed_up_host(self):
        case = self.case("changed")
        case["data"]["approved"] = case["data"]["approved"][:1]
        self.assertEqual(lab.analyse(case)["decisions"]["192.0.2.20"], "not-observed-up")

    def test_duplicate_inventory_rejected(self):
        case = self.case()
        case["data"]["approved"].append(deepcopy(case["data"]["approved"][0]))
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_out_of_scope_scan_rejected(self):
        case = self.case()
        case["data"]["nmap_xml"] = case["data"]["nmap_xml"].replace("192.0.2.30", "192.0.2.99")
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_dtd_and_malformed_xml_rejected(self):
        for xml in ('<!DOCTYPE nmaprun><nmaprun scanner="nmap"/>', '<nmaprun>'):
            with self.subTest(xml=xml), self.assertRaises(ValueError):
                lab.parse_scan(xml)

    def test_duplicate_port_rejected(self):
        case = self.case()
        entry = '<port protocol="tcp" portid="443"><state state="open"/></port>'
        case["data"]["nmap_xml"] = case["data"]["nmap_xml"].replace(entry, entry + entry, 1)
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_wrong_artifact_mirror_rejected(self):
        case = self.case()
        case["artifacts"]["scan.xml"] += " "
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_boolean_port_rejected(self):
        case = self.case()
        case["data"]["approved"][0]["expected_tcp_ports"] = [True]
        with self.assertRaises(ValueError):
            lab.analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
