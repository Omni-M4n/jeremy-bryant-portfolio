
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


    def test_spf_pass_for_unrelated_domain_does_not_authenticate_from(self):
        self.assertEqual(lab.analyse(self.case())["decisions"]["invoice"], "domain-authentication-failed")

    def test_relay_name_alone_is_not_trusted(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["message-a"], "authentication-unverified")

    def test_aligned_dkim_can_support_dmarc_when_spf_fails(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["forwarded"], "authenticated-domain-review-content")

    def test_trusted_pass_without_alignment_rejected(self):
        case = self.case()
        a = case["data"]["messages"][1]["authentication_results"][0]
        a["dmarc"] = "pass"
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_trusted_fail_with_aligned_pass_rejected(self):
        case = self.case()
        case["data"]["messages"][0]["authentication_results"][0]["dmarc"] = "fail"
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_trust_register_absent_record_rejected(self):
        case = self.case()
        case["context"]["trusted_receiving_relay"]["trusted_record_ids"].append("missing")
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_trusted_record_wrong_relay_rejected(self):
        case = self.case()
        case["data"]["messages"][0]["authentication_results"][0]["authserv_id"] = "external.test"
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_authenticated_message_with_external_link_needs_review(self):
        case = self.case()
        case["data"]["messages"][0]["link_domains"] = ["external.test"]
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["notice"], "authenticated-domain-with-mismatch")

    def test_subdomain_is_not_strictly_aligned(self):
        case = self.case()
        a = case["data"]["messages"][0]["authentication_results"][0]
        a["mailfrom_domain"] = "mail.museum.test"
        a["dkim_domain"] = "sign.museum.test"
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_untrusted_contradictory_claim_is_not_accepted(self):
        case = self.case("changed")
        a = case["data"]["messages"][0]["authentication_results"][0]
        a["mailfrom_domain"] = "sender.test"
        a["dkim"] = "fail"
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["message-a"], "authentication-unverified")

    def test_absent_dkim_signature_has_no_signing_domain(self):
        case = self.case("challenge")
        a = case["data"]["messages"][1]["authentication_results"][0]
        self.assertIsNone(a["dkim_domain"])
        a["dkim_domain"] = "museum.test"
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))


if __name__ == "__main__":
    unittest.main(verbosity=2)
