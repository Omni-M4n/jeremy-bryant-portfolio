
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


    def test_expiry_is_inclusive_then_one_second_late(self):
        case = self.case("challenge")
        self.assertEqual(lab.analyse(case)["decisions"]["boundary"], "renewal-due")
        case["data"]["evaluation_time"] = "2030-01-11T00:00:01Z"
        self.assertEqual(lab.analyse(case)["decisions"]["boundary"], "expired")

    def test_exact_renewal_threshold(self):
        case = self.case()
        case["data"]["certificates"][0]["not_after"] = "2030-01-25T00:00:00Z"
        self.assertEqual(lab.analyse(case)["decisions"]["gallery"], "renewal-due")
        case["data"]["certificates"][0]["not_after"] = "2030-01-25T00:00:01Z"
        self.assertEqual(lab.analyse(case)["decisions"]["gallery"], "fields-and-reported-chain-pass")

    def test_wildcard_does_not_match_apex_or_two_labels(self):
        self.assertTrue(lab.matches("east.museum.test", "*.museum.test"))
        self.assertFalse(lab.matches("museum.test", "*.museum.test"))
        self.assertFalse(lab.matches("a.east.museum.test", "*.museum.test"))

    def test_case_insensitive_san(self):
        case = self.case()
        case["data"]["certificates"][0]["dns_names"] = ["GALLERY.MUSEUM.TEST"]
        self.assertEqual(lab.analyse(case)["decisions"]["gallery"], "fields-and-reported-chain-pass")

    def test_simultaneous_issues_are_preserved(self):
        case = self.case()
        case["data"]["certificates"][2]["dns_names"] = ["other.test"]
        self.assertEqual(lab.analyse(case)["decisions"]["kiosk"], "expired|hostname-mismatch|chain-unverified")

    def test_reversed_interval_rejected(self):
        case = self.case()
        case["data"]["certificates"][0]["not_before"] = "2031-01-01T00:00:00Z"
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_invalid_calendar_and_offset_rejected(self):
        for value in ("2030-02-30T00:00:00Z", "2030-01-11T00:00:00+00:00"):
            case = self.case()
            case["data"]["evaluation_time"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                lab.analyse(case)

    def test_partial_wildcard_rejected(self):
        case = self.case()
        case["data"]["certificates"][0]["dns_names"] = ["gal*.museum.test"]
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_boolean_window_rejected(self):
        case = self.case()
        case["data"]["renew_within_days"] = True
        with self.assertRaises(ValueError):
            lab.analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
