"""Focused offline edge checks; every input is synthetic."""

import json
import struct
import tempfile
import unittest

import lab


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.files = lab.build_case(37)
        self.capture = self.files[lab.PCAP_NAME]
        self.frames = lab.read_pcap(self.capture)

    def test_checksum_known_vector_and_odd_byte(self):
        # Independent Internet-checksum example, plus a one-byte padding case.
        self.assertEqual(lab.checksum(bytes.fromhex("0001f203f4f5f6f7")), 0x220d)
        self.assertEqual(lab.checksum(b"\x01"), 0xfeff)

    def test_truncated_record_rejected(self):
        with self.assertRaisesRegex(lab.LabError, "Truncated PCAP record data"):
            lab.read_pcap(self.capture[:-1])

    def test_packet_payload_corruption_rejected(self):
        changed = bytearray(self.capture)
        changed[-1] ^= 1
        with self.assertRaisesRegex(lab.LabError, "UDP checksum"):
            lab.read_pcap(bytes(changed))

    def test_header_corruption_rejected(self):
        changed = bytearray(self.capture)
        # First record begins at 40; alter the IPv4 checksum field itself.
        changed[40 + 14 + 10] ^= 1
        with self.assertRaisesRegex(lab.LabError, "IPv4 length or checksum"):
            lab.read_pcap(bytes(changed))

    def test_compression_loop_and_out_of_range_pointer_rejected(self):
        for value, message in ((b"\xc0\x00", "pointer loop"), (b"\xc0\xff", "outside message")):
            with self.subTest(value=value), self.assertRaisesRegex(lab.LabError, message):
                lab.decode_name(value, 0)

    def test_nxdomain_with_answer_rejected(self):
        message = bytearray(lab.dns_message(10, "synthetic-example.test", "answer", "203.0.113.20"))
        message[2:4] = struct.pack("!H", 0x8183)
        with self.assertRaisesRegex(lab.LabError, "NXDOMAIN"):
            lab.read_dns(bytes(message))

    def test_same_id_different_clients_are_separate_episodes(self):
        episodes = lab.relationships(self.frames)
        collided = [episode for episode in episodes if episode["dns_id"] == 32783]
        self.assertEqual(len(collided), 2)
        self.assertEqual({episode["client"] for episode in collided}, {"192.0.2.10", "192.0.2.11"})
        self.assertEqual({tuple(episode["response_frames"]) for episode in collided}, {(2,), (7,)})

    def test_retry_with_late_reply_is_one_answered_episode(self):
        episodes = lab.relationships(self.frames)
        late = next(episode for episode in episodes if episode["qname"] == "synthetic-lantern.test")
        self.assertEqual(late["request_frames"], [8, 10])
        self.assertEqual(late["response_frames"], [11])
        self.assertEqual(late["outcome"], "answer")
        self.assertEqual(late["first_response_ms"], 1511.0)
        self.assertEqual(sum(episode["outcome"] == "unanswered" for episode in episodes), 1)

    def test_orphan_reply_rejected(self):
        with self.assertRaisesRegex(lab.LabError, "without an earlier matching request"):
            lab.relationships(self.frames[1:])

    def test_non_documentation_addresses_and_real_names_rejected(self):
        with self.assertRaises(lab.LabError):
            lab.documentation_ip("127.0.0.1")
        with self.assertRaises(lab.LabError):
            lab.encode_name("synthetic-example.com")

    def test_variants_change_data_but_preserve_learning_relationships(self):
        different = lab.build_case(91)
        self.assertNotEqual(self.capture, different[lab.PCAP_NAME])
        self.assertEqual(self.files, lab.build_case(37))
        for seed in (0, 91, 2147483647):
            with self.subTest(seed=seed):
                episodes = lab.relationships(lab.read_pcap(lab.build_case(seed)[lab.PCAP_NAME]))
                self.assertEqual(sorted(item["outcome"] for item in episodes),
                                 ["answer", "answer", "answer", "nxdomain", "unanswered"])
        for seed in (-1, True, 2147483648):
            with self.subTest(seed=seed), self.assertRaises(lab.LabError):
                lab.build_case(seed)


class FileAndExerciseTests(unittest.TestCase):
    def setUp(self):
        (lab.ROOT / "run").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="test-", dir=lab.ROOT / "run")
        self.addCleanup(self.temp.cleanup)
        self.directory = lab.Path(self.temp.name)
        self.files = lab.build_case(37)
        lab.write_case(self.directory, self.files)
        self.manifest, self.episodes = lab.verify_case(self.directory)

    def solved_worksheet(self):
        result = lab.worksheet(self.manifest, self.episodes)
        for target, source in zip(result["episodes"], self.episodes):
            for field in lab.ANSWER_FIELDS:
                target[field] = source[field]
        return result

    def test_modified_manifest_and_capture_are_rejected(self):
        manifest = json.loads(self.files["manifest.json"])
        manifest["expected"]["episodes"][0]["outcome"] = "unanswered"
        (self.directory / "manifest.json").write_bytes(lab.json_bytes(manifest))
        with self.assertRaisesRegex(lab.LabError, "Manifest differs"):
            lab.verify_case(self.directory)
        (self.directory / "manifest.json").write_bytes(self.files["manifest.json"])
        (self.directory / lab.PCAP_NAME).write_bytes(self.files[lab.PCAP_NAME][:-1])
        with self.assertRaisesRegex(lab.LabError, "integrity mismatch"):
            lab.verify_case(self.directory)

    def test_existing_changed_output_is_preserved(self):
        original = (self.directory / lab.PCAP_NAME).read_bytes()
        with self.assertRaisesRegex(lab.LabError, "choose a fresh output directory"):
            lab.write_case(self.directory, lab.build_case(91))
        self.assertEqual((self.directory / lab.PCAP_NAME).read_bytes(), original)

    def test_output_escape_rejected(self):
        for name in ("../escape", ".", "lab.py", "fixtures"):
            with self.subTest(name=name), self.assertRaises(lab.LabError):
                lab.lab_path(name, output=True)

    def test_blank_and_correct_worksheets_are_distinguished(self):
        blank = lab.worksheet(self.manifest, self.episodes)
        self.assertTrue(lab.check_answers(blank, self.manifest, self.episodes))
        self.assertEqual(lab.check_answers(self.solved_worksheet(), self.manifest, self.episodes), [])
        self.assertEqual(blank["independent_mastery"], "NOT assessed")

    def test_mismatched_case_and_duplicate_answers_rejected(self):
        answers = self.solved_worksheet()
        answers["capture_sha256"] = "0" * 64
        with self.assertRaisesRegex(lab.LabError, "different case"):
            lab.check_answers(answers, self.manifest, self.episodes)
        answers = self.solved_worksheet()
        answers["episodes"].append(answers["episodes"][0])
        with self.assertRaisesRegex(lab.LabError, "Duplicate worksheet episode"):
            lab.check_answers(answers, self.manifest, self.episodes)

    def test_boolean_is_not_accepted_as_frame_number(self):
        answers = self.solved_worksheet()
        violet = next(item for item in answers["episodes"] if item["qname"] == "synthetic-violet.test")
        violet["request_frames"] = [True]
        self.assertTrue(lab.check_answers(answers, self.manifest, self.episodes))


if __name__ == "__main__":
    unittest.main()
