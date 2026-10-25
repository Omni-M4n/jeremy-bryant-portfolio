"""Synthetic parser and filesystem checks; never query Windows event logs."""

import contextlib
import hashlib
import io
import json
import re
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid
import xml.etree.ElementTree as ET

import lab


def fixture(name="guided"):
    return (lab.ROOT / "fixtures" / f"{name}.xml").read_bytes()


class ParserTests(unittest.TestCase):
    def test_guided_chain_and_near_miss(self):
        report = lab.analyse(fixture())
        self.assertEqual(report["event_1_count"], 4)
        rows = {r["record_id"]: r for r in report["timeline"]}
        self.assertEqual(rows[102]["parent_record_id"], 101)
        self.assertEqual(rows[103]["parent_record_id"], 102)
        self.assertIsNone(rows[104]["parent_record_id"])
        self.assertEqual(rows[103]["command_line"], rows[104]["command_line"])
        self.assertNotEqual(rows[103]["parent_guid"], rows[104]["parent_guid"])

    def test_pid_reuse_does_not_choose_earlier_process(self):
        rows = lab.analyse(fixture("changed"))["timeline"]
        self.assertEqual([r["pid"] for r in rows], [2000, 2000, 3000])
        self.assertEqual(rows[2]["parent_record_id"], 202)
        self.assertEqual(rows[2]["pid_only_other_candidates"], [201])

    def test_missing_parent_is_not_replaced_by_pid_candidate(self):
        rows = lab.analyse(fixture("challenge"))["timeline"]
        self.assertEqual([r["record_id"] for r in rows], [301, 302])
        self.assertEqual(rows[1]["relationship"], "parent-not-in-export")
        self.assertIsNone(rows[1]["parent_record_id"])
        self.assertEqual(rows[1]["pid_only_other_candidates"], [301])

    def test_computer_is_part_of_correlation_key(self):
        root = ET.fromstring(fixture())
        root[1].find(lab.NS + "System/" + lab.NS + "Computer").text = "OTHER.test"
        rows = lab.analyse(ET.tostring(root))["timeline"]
        self.assertIsNone(rows[1]["parent_record_id"])
        self.assertIsNone(rows[2]["parent_record_id"])

    def test_utf16_and_single_event_exports(self):
        text = fixture().decode().replace('encoding="utf-8"', 'encoding="utf-16"')
        self.assertEqual(lab.analyse(text.encode("utf-16"))["event_1_count"], 4)
        event = ET.fromstring(fixture())[2]
        self.assertEqual(lab.analyse(ET.tostring(event))["event_1_count"], 1)

    def test_invalid_xml_and_other_formats_fail(self):
        for data in (b"<Events>", b"", b"<Objs/>", b"<QueryList/>", b"<Events/>",
                     b"<Event/>", b"<!DOCTYPE Events [<!ENTITY x 'x'>]><Events/>",
                     "<!DOCTYPE Events><Events/>".encode("utf-16")):
            with self.subTest(data=data[:60]), self.assertRaises(ValueError):
                lab.analyse(data)

    def test_required_field_and_duplicate_fields_fail(self):
        data = fixture()
        for changed in (
            data.replace(b'<Data Name="ProcessId">1000</Data>', b"", 1),
            data.replace(b'<Data Name="ProcessId">1000</Data>', b'<Data Name="ProcessId">1000</Data>' * 2, 1),
            data.replace(b"2026-10-20 09:00:00.000", b"not-a-time", 1),
            data.replace(b"11111111-1111-1111-1111-111111111101", b"bad-guid", 1),
            data.replace(b'<Data Name="ProcessId">1000</Data>', b'<Data Name="ProcessId">-1</Data>', 1),
        ):
            with self.subTest(changed=changed[:40]), self.assertRaises(ValueError):
                lab.analyse(changed)

    def test_duplicate_record_or_guid_fails(self):
        data = fixture()
        for changed in (
            data.replace(b"<EventRecordID>102", b"<EventRecordID>101", 1),
            data.replace(b'Name="ProcessGuid">{11111111-1111-1111-1111-111111111102}',
                         b'Name="ProcessGuid">{11111111-1111-1111-1111-111111111101}', 1),
        ):
            with self.assertRaises(ValueError):
                lab.analyse(changed)

    def test_non_target_event_is_counted_not_misread(self):
        data = fixture().replace(b"<EventID>1</EventID>", b"<EventID>3</EventID>", 1)
        report = lab.analyse(data)
        self.assertEqual(report["event_1_count"], 3)
        self.assertEqual(report["skipped_other_events"], 1)
        with self.assertRaises(ValueError):
            lab.analyse(data.replace(b"<EventID>1</EventID>", b"<EventID>3</EventID>"))

    def test_timestamp_precision_timezone_and_invalid_dates(self):
        first, text = lab.timestamp("2026-10-20T09:00:00.0000001Z")
        second, _ = lab.timestamp("2026-10-20T09:00:00.0000002Z")
        self.assertEqual(second - first, 1)
        self.assertEqual(text, "2026-10-20T09:00:00.0000001Z")
        self.assertEqual(lab.timestamp("2026-10-20T20:00:00.0000001+11:00")[0], first)
        for value in (
            "2026-02-30T01:00:00Z", "2026-10-20T09:00:00", "2026-10-20T09:00:00.12345678Z",
            "2026-10-20T09:00:00+01:60", "2026-10-20T09:00:00+00:99",
            "2026-10-20T09:00:00-01:60", "2026-10-20T09:00:00+24:00",
            "0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00",
        ):
            with self.assertRaises(ValueError):
                lab.timestamp(value)

    def test_inconsistent_parent_metadata_is_flagged(self):
        data = fixture().replace(b'Name="ParentProcessId">1000', b'Name="ParentProcessId">9999', 1)
        self.assertIn("GUID matches but parent PID disagrees.", lab.analyse(data)["timeline"][1]["consistency_notes"])

    def test_size_and_record_count_bounds(self):
        with self.assertRaises(ValueError):
            lab.analyse(b"x" * (lab.MAX_BYTES + 1))
        with patch.object(lab, "MAX_EVENTS", 3), self.assertRaises(ValueError):
            lab.analyse(fixture())


class FilesystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = lab.fresh_run("tests-" + uuid.uuid4().hex[:12])

    def test_prepare_is_blank_and_refuses_overwrite(self):
        with patch.object(lab, "ROOT", self.sandbox), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lab.main(["prepare", "--name", "blank"]), 0)
            before = (self.sandbox / "run/blank/worksheet.json").read_bytes()
            self.assertEqual(json.loads(before)["finding"], "")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(lab.main(["prepare", "--name", "blank"]), 2)
            self.assertEqual((self.sandbox / "run/blank/worksheet.json").read_bytes(), before)

    def test_inspection_does_not_modify_source(self):
        source = self.sandbox / "source.xml"
        source.write_bytes(fixture())
        before = source.stat().st_mtime_ns, hashlib.sha256(source.read_bytes()).hexdigest()
        with patch.object(lab, "ROOT", self.sandbox), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lab.main(["inspect", "--xml", str(source), "--name", "inspection", "--evidence-kind", "synthetic"]), 0)
        after = source.stat().st_mtime_ns, hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(before, after)
        receipt = json.loads((self.sandbox / "run/inspection/receipt.json").read_text())
        self.assertEqual(receipt["sha256"], before[1])
        self.assertFalse(receipt["real_capture_verified"])

    def test_invalid_source_does_not_create_result(self):
        bad = self.sandbox / "invalid.xml"
        bad.write_text("<Events>", encoding="utf-8")
        with patch.object(lab, "ROOT", self.sandbox), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lab.main(["inspect", "--xml", str(bad), "--name", "invalid-run", "--evidence-kind", "synthetic"]), 2)
        self.assertFalse((self.sandbox / "run/invalid-run").exists())

    def test_invalid_timestamp_does_not_create_result(self):
        for index, value in enumerate((b"2026-10-20T09:00:00+01:60", b"0001-01-01T00:00:00+01:00")):
            bad = self.sandbox / f"invalid-time-{index}.xml"
            data = re.sub(rb'SystemTime="[^"]+"', b'SystemTime="' + value + b'"', fixture(), count=1)
            bad.write_bytes(data)
            name = f"invalid-time-{index}"
            with patch.object(lab, "ROOT", self.sandbox), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(lab.main(["inspect", "--xml", str(bad), "--name", name, "--evidence-kind", "synthetic"]), 2)
            self.assertFalse((self.sandbox / "run" / name).exists())

    def test_names_cannot_escape_run_directory(self):
        for name in ("../escape", "/absolute", "a/b", "a\\b", "UPPER", "con", "com1", "nul", "a" * 49):
            with self.subTest(name=name), self.assertRaises(ValueError):
                lab.fresh_run(name, self.sandbox)

    def test_reparse_component_is_rejected(self):
        # Simulate the Windows reparse attribute without creating a host junction.
        with patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=0, st_file_attributes=0x400)):
            with self.assertRaisesRegex(ValueError, "reparse"):
                lab.safe_path(self.sandbox / "linked" / "input.xml")

    def test_non_xml_and_oversize_source_are_rejected(self):
        with self.assertRaises(ValueError):
            lab.read_source(self.sandbox / "source.evtx")
        source = self.sandbox / "oversize.xml"
        source.write_bytes(b"x" * 100)
        with patch.object(lab, "MAX_BYTES", 50), self.assertRaises(ValueError):
            lab.read_source(source)


if __name__ == "__main__":
    unittest.main()
