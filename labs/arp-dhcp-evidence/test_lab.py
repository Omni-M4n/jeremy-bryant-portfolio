"""Independent correlation boundaries and fixed fixture expectations."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab


class ExchangeTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((lab.ROOT / "fixtures" / f"{name}.json").read_text(encoding="utf-8"))

    def sync(self, case):
        case["artifacts"] = {"packets.txt": lab.evidence_text(case["data"])}
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

    def test_renewal_does_not_need_discover_or_offer(self):
        result = lab.analyse(self.case("changed"))
        self.assertEqual(result["decisions"]["client-a"], "renewal-ack-observed")
        self.assertIn("ignored frames [12]", result["observations"][0])

    def test_same_xid_wrong_client_does_not_complete_lease(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["client-b"], "ack-not-observed")

    def test_wrong_xid_does_not_complete_lease(self):
        case = self.case()
        case["data"]["dhcp_sessions"][0]["packets"][-1]["xid"] = 1002
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["lease-a"], "ack-not-observed")

    def test_matching_xid_alone_does_not_accept_wrong_server(self):
        case = self.case()
        case["data"]["dhcp_sessions"][0]["packets"][-1]["server_id"] = "192.0.2.2"
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["lease-a"], "reply-mismatch")

    def test_nak_is_not_acknowledgement(self):
        case = self.case()
        packet = case["data"]["dhcp_sessions"][0]["packets"][-1]
        packet.update(message="NAK", yiaddr="0.0.0.0", lease_seconds=None)
        result = lab.analyse(self.sync(case))["decisions"]
        self.assertEqual(result["lease-a"], "nak-observed")
        self.assertEqual(result["gateway-lease-link"], "lease-link-not-established")

    def test_offer_without_request_is_not_a_lease(self):
        case = self.case()
        case["data"]["dhcp_sessions"][0]["packets"] = case["data"]["dhcp_sessions"][0]["packets"][:2]
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["lease-a"], "request-not-observed")

    def test_allocation_ack_with_missing_discover_has_gap(self):
        case = self.case()
        case["data"]["dhcp_sessions"][0]["packets"].pop(0)
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["lease-a"], "allocation-ack-with-gaps")

    def test_arp_reply_to_other_client_does_not_match(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["exchange-b"], "request-no-reply-observed")

    def test_missing_arp_request_is_not_filled_in(self):
        case = self.case()
        case["data"]["arp_exchanges"][0]["packets"].pop(0)
        result = lab.analyse(self.sync(case))["decisions"]
        self.assertEqual(result["gateway"], "reply-without-prior-request")
        self.assertEqual(result["gateway-lease-link"], "lease-link-not-established")

    def test_two_mac_claims_are_disagreement_without_cause(self):
        case = self.case()
        packets = case["data"]["arp_exchanges"][0]["packets"]
        other = deepcopy(packets[-1]); other.update(frame=7, sender_mac="02:00:00:00:00:02")
        packets.append(other)
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["gateway"], "mapping-disagreement")

    def test_arp_before_ack_cannot_be_explained_by_later_ack(self):
        case = self.case()
        case["data"]["dhcp_sessions"][0]["packets"][-1]["frame"] = 7
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["gateway-lease-link"], "arp-precedes-ack")

    def test_address_disagreement_survives_same_mac(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["exchange-c-lease-link"], "lease-address-disagreement")

    def test_duplicate_or_reverse_frames_rejected(self):
        for frame in (1, 5):
            case = self.case()
            case["data"]["arp_exchanges"][0]["packets"][-1]["frame"] = frame
            with self.subTest(frame=frame), self.assertRaises(ValueError): lab.analyse(self.sync(case))

    def test_invalid_xid_and_lease_rejected(self):
        for field, value in (("xid", True), ("xid", -1), ("xid", 2**32), ("lease_seconds", 0)):
            case = self.case()
            case["data"]["dhcp_sessions"][0]["packets"][-1][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError): lab.analyse(self.sync(case))

    def test_bad_renewal_and_init_reboot_rejected(self):
        case = self.case("changed")
        case["data"]["dhcp_sessions"][0]["packets"][0]["server_id"] = "192.0.2.1"
        with self.assertRaises(ValueError): lab.analyse(self.sync(case))
        case = self.case()
        case["data"]["dhcp_sessions"][0]["packets"][2]["server_id"] = None
        with self.assertRaises(ValueError): lab.analyse(self.sync(case))

    def test_repeated_step_and_bad_order_rejected(self):
        for repeat in (True, False):
            case = self.case()
            packets = case["data"]["dhcp_sessions"][0]["packets"]
            if repeat: packets[0] = dict(packets[1], frame=1)
            else: packets[0], packets[1] = dict(packets[1], frame=1), dict(packets[0], frame=2)
            with self.subTest(repeat=repeat), self.assertRaises(ValueError): lab.analyse(self.sync(case))

    def test_artifact_and_extra_field_rejected(self):
        case = self.case(); case["artifacts"]["packets.txt"] += "stale\n"
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case(); case["data"]["extra"] = True
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_unknown_related_session_and_client_mismatch_rejected(self):
        for field, value in (("related_dhcp", "missing"), ("requester_mac", "02:00:00:00:00:99")):
            case = self.case(); case["data"]["arp_exchanges"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): lab.analyse(self.sync(case))

    # R1-R3 reproduce the review's recorded failing shapes, with valid controls.
    def test_offer_nonzero_ciaddr_rejected(self):
        case = self.case()
        case["data"]["dhcp_sessions"][0]["packets"][1]["ciaddr"] = "192.0.2.44"
        with self.assertRaisesRegex(ValueError, "Offer ciaddr"):
            lab.analyse(self.sync(case))

    def test_offer_delivery_alternatives_and_unrelated_destination(self):
        for destination in ("255.255.255.255", "192.0.2.20", "203.0.113.90"):
            case = self.case()
            case["data"]["dhcp_sessions"][0]["packets"][1]["ip_destination"] = destination
            with self.subTest(destination=destination):
                if destination == "203.0.113.90":
                    with self.assertRaisesRegex(ValueError, "Offer destination"):
                        lab.analyse(self.sync(case))
                else:
                    self.assertEqual(lab.analyse(self.sync(case))["decisions"]["lease-a"], "allocation-ack-observed")

    def test_nak_invalid_fields_rejected_individually(self):
        for field, value in (("ciaddr", "192.0.2.44"), ("ip_destination", "192.0.2.20")):
            case = self.case()
            packet = case["data"]["dhcp_sessions"][0]["packets"][-1]
            packet.update(message="NAK", yiaddr="0.0.0.0", lease_seconds=None)
            packet[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "NAK"):
                lab.analyse(self.sync(case))

    def test_allocation_ack_contradictions_rejected_individually(self):
        for field, value in (("ciaddr", "192.0.2.44"), ("ip_destination", "203.0.113.90")):
            case = self.case()
            case["data"]["dhcp_sessions"][0]["packets"][-1][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "ACK"):
                lab.analyse(self.sync(case))

    def test_allocation_ack_broadcast_and_yiaddr_delivery_are_valid(self):
        for destination in ("255.255.255.255", "192.0.2.20"):
            case = self.case()
            case["data"]["dhcp_sessions"][0]["packets"][-1]["ip_destination"] = destination
            with self.subTest(destination=destination):
                result = lab.analyse(self.sync(case))["decisions"]
                self.assertEqual(result["lease-a"], "allocation-ack-observed")
                self.assertEqual(result["gateway-lease-link"], "same-client-address-observed")

    def test_renewal_ack_broadcast_and_wrong_host_rejected(self):
        for destination in ("255.255.255.255", "203.0.113.90"):
            case = self.case("changed")
            case["data"]["dhcp_sessions"][0]["packets"][-1]["ip_destination"] = destination
            with self.subTest(destination=destination), self.assertRaisesRegex(ValueError, "renewal ACK"):
                lab.analyse(self.sync(case))

    def test_renewal_ack_zero_or_copied_ciaddr_are_valid(self):
        for ciaddr in ("0.0.0.0", "192.0.2.20"):
            case = self.case("changed")
            packet = case["data"]["dhcp_sessions"][0]["packets"][-1]
            packet.update(ciaddr=ciaddr, ip_destination="192.0.2.20")
            with self.subTest(ciaddr=ciaddr):
                result = lab.analyse(self.sync(case))["decisions"]
                self.assertEqual(result["client-a"], "renewal-ack-observed")
                self.assertEqual(result["exchange-a-lease-link"], "same-client-address-observed")

    def test_renewal_ack_different_ciaddr_rejected(self):
        case = self.case("changed")
        case["data"]["dhcp_sessions"][0]["packets"][-1]["ciaddr"] = "192.0.2.44"
        with self.assertRaisesRegex(ValueError, "ACK ciaddr"):
            lab.analyse(self.sync(case))

    def test_renewal_nak_broadcast_is_valid(self):
        case = self.case("changed")
        packet = case["data"]["dhcp_sessions"][0]["packets"][-1]
        packet.update(message="NAK", ciaddr="0.0.0.0", yiaddr="0.0.0.0", lease_seconds=None, ip_destination="255.255.255.255")
        result = lab.analyse(self.sync(case))["decisions"]
        self.assertEqual(result["client-a"], "nak-observed")
        self.assertEqual(result["exchange-a-lease-link"], "lease-link-not-established")

    def test_earlier_reply_does_not_hide_later_observed_pair(self):
        case = self.case()
        exchange = case["data"]["arp_exchanges"][0]
        request, reply = exchange["packets"]
        exchange["packets"] = [dict(reply, frame=5), dict(request, frame=6), dict(reply, frame=7)]
        result = lab.analyse(self.sync(case))
        self.assertEqual(result["decisions"]["gateway"], "exchange-observed")
        self.assertIn("Reply frames [5] have no earlier observed matching request.", result["observations"][1])

    def test_earlier_reply_without_later_reply_remains_unpaired(self):
        case = self.case()
        exchange = case["data"]["arp_exchanges"][0]
        request, reply = exchange["packets"]
        exchange["packets"] = [dict(reply, frame=5), dict(request, frame=6)]
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["gateway"], "reply-without-prior-request")

    def test_mapping_disagreement_precedes_observed_pair(self):
        case = self.case()
        exchange = case["data"]["arp_exchanges"][0]
        request, reply = exchange["packets"]
        exchange["packets"] = [dict(reply, frame=5), dict(request, frame=6), dict(reply, frame=7, sender_mac="02:00:00:00:00:02")]
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["gateway"], "mapping-disagreement")

    def test_same_mapping_repeated_reply_still_has_observed_pair(self):
        case = self.case()
        packets = case["data"]["arp_exchanges"][0]["packets"]
        packets.append(dict(packets[-1], frame=7))
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["gateway"], "exchange-observed")

    def test_independent_metadata_uses_neutral_titles_and_ids(self):
        for key, suffix in (("changed", "B"), ("challenge", "C")):
            case = self.case(key)
            self.assertEqual(case["title"], "Packet excerpt set " + suffix)
            for session in case["data"]["dhcp_sessions"]:
                self.assertRegex(session["id"], r"^client-[a-z]$")
            for exchange in case["data"]["arp_exchanges"]:
                self.assertRegex(exchange["id"], r"^exchange-[a-z]$")
                self.assertRegex(exchange["related_dhcp"], r"^client-[a-z]$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
