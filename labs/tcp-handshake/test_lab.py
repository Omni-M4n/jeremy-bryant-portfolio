
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


    def test_both_sequences_wrap(self):
        case = self.case("challenge")
        p = case["data"]["flows"][0]["packets"]
        p[1]["seq"] = 4294967295
        p[2]["ack"] = 0
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["wrapped"], "handshake-observed")

    def test_synack_ack_mismatch(self):
        case = self.case()
        case["data"]["flows"][0]["packets"][1]["ack"] = 1000
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["gallery"], "acknowledgement-mismatch")

    def test_reset_ack_mismatch(self):
        case = self.case()
        case["data"]["flows"][1]["packets"][1]["ack"] = 99
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["archive"], "acknowledgement-mismatch")

    def test_synack_retransmission_does_not_complete_handshake(self):
        case = self.case("changed")
        p = case["data"]["flows"][0]["packets"]
        duplicate = deepcopy(p[-1])
        duplicate["frame"] = 5
        p.append(duplicate)
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["gallery"], "final-ack-not-observed")

    def test_wrong_direction_rejected(self):
        case = self.case()
        case["data"]["flows"][0]["packets"][1]["direction"] = "c2s"
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_boolean_and_overflow_sequences_rejected(self):
        for value in (True, 4294967296, -1):
            case = self.case()
            case["data"]["flows"][0]["packets"][0]["seq"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                lab.analyse(self.sync(case))

    def test_multiple_attempts_rejected(self):
        case = self.case()
        case["data"]["flows"][2]["packets"][1]["seq"] += 1
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_decreasing_frame_number_rejected(self):
        case = self.case()
        case["data"]["flows"][0]["packets"][1]["frame"] = 1
        with self.assertRaises(ValueError):
            lab.analyse(self.sync(case))

    def test_artifact_disagreement_rejected(self):
        case = self.case()
        case["artifacts"]["packets.csv"] = "incorrect\n"
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_late_capture_inconsistent_synack_retransmissions_rejected(self):
        for field, value in (("seq", 1200), ("ack", 500)):
            case = self.case("changed")
            packets = case["data"]["flows"][1]["packets"]
            repeat = deepcopy(packets[0])
            repeat["frame"] = 3
            repeat[field] = value
            packets.insert(1, repeat)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "inconsistent SYN-ACK"):
                lab.analyse(self.sync(case))

    def test_late_capture_reset_cannot_be_followed_by_ack(self):
        case = self.case("changed")
        case["data"]["flows"][1]["packets"][0]["flags"] = "RST-ACK"
        with self.assertRaisesRegex(ValueError, "reset must end"):
            lab.analyse(self.sync(case))

    def test_late_capture_identical_synack_repeats_remain_incomplete(self):
        for include_final in (False, True):
            case = self.case("changed")
            flow = case["data"]["flows"][1]
            first, final = flow["packets"]
            repeat = deepcopy(first)
            repeat["frame"] = 3
            flow["packets"] = [first, repeat] + ([final] if include_final else [])
            with self.subTest(include_final=include_final):
                self.assertEqual(lab.analyse(self.sync(case))["decisions"]["archive"], "initial-syn-not-observed")

    def test_late_capture_lone_terminal_packets_remain_incomplete(self):
        for flags in ("ACK", "RST-ACK"):
            case = self.case("changed")
            flow = case["data"]["flows"][1]
            packet = deepcopy(flow["packets"][-1])
            packet["flags"] = flags
            packet["direction"] = "c2s" if flags == "ACK" else "s2c"
            flow["packets"] = [packet]
            with self.subTest(flags=flags):
                self.assertEqual(lab.analyse(self.sync(case))["decisions"]["archive"], "initial-syn-not-observed")

    def test_other_late_capture_suffix_orders_rejected(self):
        for flags in (("ACK", "SYN-ACK"), ("SYN-ACK", "RST-ACK"),
                      ("SYN-ACK", "ACK", "ACK"), ("ACK", "ACK"), ("RST-ACK", "RST-ACK")):
            case = self.case("changed")
            flow = case["data"]["flows"][1]
            flow["packets"] = [dict(frame=n+1, direction="c2s" if flag == "ACK" else "s2c",
                                    flags=flag, seq=900, ack=401) for n, flag in enumerate(flags)]
            with self.subTest(flags=flags), self.assertRaises(ValueError):
                lab.analyse(self.sync(case))


if __name__ == "__main__":
    unittest.main(verbosity=2)
