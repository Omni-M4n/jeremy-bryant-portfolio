"""Synthetic, offline checks. Passing them does not demonstrate learner mastery."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from html.parser import HTMLParser
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import report


ROOT = Path(__file__).resolve().parent


def case():
    return {
        "schema_version": 1,
        "report_title": "Fictional test report",
        "findings": [{
            "id": "OBS-001",
            "resource": "https://example.test/",
            "title": "Fictional observation",
            "severity": "high",
            "confidence": "low",
            "evidence": ["Fictional scanner message."],
        }],
    }


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attributes = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attributes.extend(attrs)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.source = self.folder / "private-input.json"
        self.output = self.folder / "report.html"

    def save(self, data=None):
        self.source.write_text(json.dumps(case() if data is None else data), encoding="utf-8")

    def run_cli(self, source=None, output=None):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = report.main([str(source or self.source), str(output or self.output)])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_sample_cli_creates_complete_report_and_cleans_temporary(self):
        status, stdout, stderr = self.run_cli(ROOT / "sample.json")
        self.assertEqual((status, stdout, stderr), (0, "Wrote 3 observations.\n", ""))
        html = self.output.read_text(encoding="utf-8")
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertTrue(html.endswith("</html>\n"))
        self.assertIn("Fictional training scan", html)
        self.assertIn("does not confirm exploitation", html)
        self.assertEqual(list(self.folder.glob(".scan-report-*")), [])

    def test_delivered_example_exactly_matches_the_current_sample(self):
        expected = report.render_report(report.load_report(ROOT / "sample.json")).encode("utf-8")
        self.assertEqual((ROOT / "example.html").read_bytes(), expected)

    def test_output_is_deterministic_and_severity_then_id_sorted(self):
        data = case()
        data["findings"] = []
        for identifier, severity in (("Z", "high"), ("A", "low"), ("B", "critical"), ("C", "high")):
            finding = deepcopy(case()["findings"][0])
            finding.update(id=identifier, severity=severity)
            data["findings"].append(finding)
        first = report.render_report(data)
        data["findings"].reverse()
        self.assertEqual(first, report.render_report(data))
        positions = [first.index(f'>{identifier} · Severity:') for identifier in ("B", "C", "Z", "A")]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('<th scope="row">High</th><td>2</td>', first)

    def test_every_text_field_is_escaped_and_urls_are_never_links(self):
        data = case()
        attack = '<script>alert("x")</script><img src=x onerror=alert(1)> & \'quoted\''
        data["report_title"] = attack
        data["findings"][0].update(title=attack, resource="javascript:alert(1)",
                                   evidence=[attack, "https://example.test/?q=<svg/onload=alert(1)>"])
        html = report.render_report(data)
        parsed = Tags()
        parsed.feed(html)
        self.assertNotIn("script", parsed.tags)
        self.assertNotIn("img", parsed.tags)
        self.assertNotIn("a", parsed.tags)
        self.assertFalse(any(name in ("href", "src", "onerror", "onload") for name, _ in parsed.attributes))
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&amp;", html)
        self.assertIn("&#x27;quoted&#x27;", html)
        self.assertIn("javascript:alert(1)", html)

    def test_empty_findings_is_valid_but_not_a_security_verdict(self):
        data = case()
        data["findings"] = []
        self.save(data)
        self.assertEqual(self.run_cli()[0], 0)
        html = self.output.read_text(encoding="utf-8")
        self.assertIn("0 supplied scanner observations", html)
        self.assertIn("does not establish that a system is secure", html)

    def test_invalid_last_finding_prevents_any_output(self):
        data = case()
        data["findings"].append(dict(data["findings"][0], id="OBS-002", confidence=True))
        self.save(data)
        self.assertEqual(self.run_cli()[0], 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.folder.glob(".scan-report-*")), [])

    def test_schema_version_rejects_bool_float_text_and_unsupported_integer(self):
        for value in (True, False, 1.0, "1", 2, None):
            with self.subTest(value=value):
                data = case()
                data["schema_version"] = value
                with self.assertRaises(report.ReportError):
                    report.validate(data)

    def test_wrong_types_and_choices_are_rejected_without_coercion(self):
        invalid = {"id": [True, 1, "bad id", "-bad", "a" * 65],
                   "resource": [True, 1, None, "", " "],
                   "title": [False, 12, [], ""],
                   "severity": [True, 1, [], "HIGH", "unknown"],
                   "confidence": [True, 1, {}, "confirmed"],
                   "evidence": [True, 1, {}, "text", [], [True], [1], [""]]}
        for field, values in invalid.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    data = case()
                    data["findings"][0][field] = value
                    with self.assertRaises(report.ReportError):
                        report.validate(data)

    def test_missing_unknown_and_non_object_records_are_rejected(self):
        candidates = [None, [], {}, dict(case(), extra="ignored?")]
        for field in case():
            data = case()
            del data[field]
            candidates.append(data)
        for value in (None, True, {}, "row"):
            candidates.append(dict(case(), findings=[value]))
        extra = case()
        extra["findings"][0]["unexpected"] = "value"
        candidates.append(extra)
        for data in candidates:
            with self.subTest(data=data), self.assertRaises(report.ReportError):
                report.validate(data)

    def test_report_title_and_findings_have_strict_types(self):
        for field, value in (("report_title", True), ("report_title", 1),
                             ("report_title", " "), ("findings", {}),
                             ("findings", True), ("findings", "[]")):
            with self.subTest(field=field, value=value):
                data = case()
                data[field] = value
                with self.assertRaises(report.ReportError):
                    report.validate(data)

    def test_duplicate_ids_are_rejected(self):
        data = case()
        data["findings"].append(deepcopy(data["findings"][0]))
        with self.assertRaisesRegex(report.ReportError, "ids must be unique"):
            report.validate(data)

    def test_string_and_evidence_count_limits(self):
        for field, maximum in (("resource", 500), ("title", 200)):
            data = case()
            data["findings"][0][field] = "x" * maximum
            report.validate(data)
            data["findings"][0][field] += "x"
            with self.assertRaises(report.ReportError):
                report.validate(data)
        data = case()
        data["report_title"] = "x" * 201
        with self.assertRaises(report.ReportError):
            report.validate(data)
        for evidence in (["x"] * 11, ["x" * 2001]):
            data = case()
            data["findings"][0]["evidence"] = evidence
            with self.assertRaises(report.ReportError):
                report.validate(data)

    def test_finding_count_boundary(self):
        data = case()
        data["findings"] = [dict(data["findings"][0], id=f"OBS-{index}")
                            for index in range(report.MAX_FINDINGS)]
        report.validate(data)
        data["findings"].append(dict(data["findings"][0], id="too-many"))
        with self.assertRaises(report.ReportError):
            report.validate(data)

    def test_invalid_unicode_and_control_characters_are_rejected(self):
        for value in ("bad\x00", "bad\x1b", "bad\x7f", "bad\ud800"):
            data = case()
            data["findings"][0]["evidence"] = [value]
            with self.subTest(value=repr(value)), self.assertRaises(report.ReportError):
                report.render_report(data)

    def test_bad_json_empty_file_invalid_utf8_duplicate_keys_and_nan(self):
        for raw in (b"", b"{", b"\xff", b'{"schema_version":1,"schema_version":1}', b'{"a":NaN}'):
            with self.subTest(raw=raw):
                self.source.write_bytes(raw)
                self.assertEqual(self.run_cli()[0], 1)
                self.assertFalse(self.output.exists())

    def test_bom_is_supported(self):
        self.source.write_bytes(b"\xef\xbb\xbf" + json.dumps(case()).encode("utf-8"))
        self.assertEqual(report.load_report(self.source), case())

    def test_oversized_file_is_rejected(self):
        self.source.write_bytes(b" " * (report.MAX_BYTES + 1))
        status, _, stderr = self.run_cli()
        self.assertEqual(status, 1)
        self.assertIn("exceeds", stderr)
        self.assertFalse(self.output.exists())

    def test_deep_json_is_rejected_before_decoding(self):
        self.source.write_text("[" * 2000 + "]" * 2000, encoding="utf-8")
        with patch.object(report.json, "loads", side_effect=AssertionError("decoder called")):
            status, _, stderr = self.run_cli()
        self.assertEqual(status, 1)
        self.assertIn("nesting limit", stderr)
        self.assertFalse(self.output.exists())

    def test_depth_check_ignores_brackets_and_escaped_quotes_in_strings(self):
        data = case()
        data["findings"][0]["evidence"] = ['[{' * 30 + '\\"' + '}]' * 30]
        self.save(data)
        self.assertEqual(report.load_report(self.source), data)

    def test_existing_output_is_preserved(self):
        self.save()
        self.output.write_bytes(b"KEEP ORIGINAL OUTPUT")
        self.assertEqual(self.run_cli()[0], 1)
        self.assertEqual(self.output.read_bytes(), b"KEEP ORIGINAL OUTPUT")
        self.assertEqual(list(self.folder.glob(".scan-report-*")), [])

    def test_input_output_collision_preserves_source(self):
        self.save()
        before = self.source.read_bytes()
        self.assertEqual(self.run_cli(output=self.source)[0], 1)
        self.assertEqual(self.source.read_bytes(), before)

    def test_new_output_racing_publication_is_preserved(self):
        self.save()

        def create_before_link(*args):
            self.output.write_bytes(b"NEW OTHER FILE")
            raise FileExistsError("private path omitted")

        with patch.object(report.os, "link", side_effect=create_before_link):
            self.assertEqual(self.run_cli()[0], 1)
        self.assertEqual(self.output.read_bytes(), b"NEW OTHER FILE")
        self.assertEqual(list(self.folder.glob(".scan-report-*")), [])

    def test_output_write_failure_does_not_publish_partial_file(self):
        self.save()
        with patch.object(report.os, "fsync", side_effect=OSError("private path")):
            status, _, stderr = self.run_cli()
        self.assertEqual(status, 1)
        self.assertNotIn("private path", stderr)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.folder.glob(".scan-report-*")), [])

    def test_missing_input_and_output_folder_errors_hide_paths(self):
        status, stdout, stderr = self.run_cli()
        self.assertEqual((status, stdout), (1, ""))
        self.assertNotIn(str(self.folder), stderr)
        self.assertNotIn(self.source.name, stderr)
        self.save()
        status, _, stderr = self.run_cli(output=self.folder / "missing" / "report.html")
        self.assertEqual(status, 1)
        self.assertNotIn(str(self.folder), stderr)
        self.assertFalse((self.folder / "missing").exists())


if __name__ == "__main__":
    unittest.main()
