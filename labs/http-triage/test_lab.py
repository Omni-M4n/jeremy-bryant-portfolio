"""Checks of evidence handling and fixture integrity, not learner grading."""

import copy
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

import lab


def case_data(scenario="mixed", seed=53):
    files = lab.make_case(seed, scenario)
    rows = list(csv.DictReader(io.StringIO(files["access.csv"].decode("utf-8"))))
    return rows, json.loads(files["context.json"])


def rules_for(report, prefix):
    return [item["rule"] for item in report["review_items"] if item["source_ip"].startswith(prefix)]


class EvidenceTests(unittest.TestCase):
    def test_busy_crawler_and_path_variety_are_separate_questions(self):
        rows, context = case_data()
        result = lab.analyze(rows, context)
        self.assertEqual(result["event_count"], 21)
        self.assertEqual(rules_for(result, "198.51.100."), ["request-volume"])
        self.assertEqual(rules_for(result, "203.0.113."), ["watched-path-variety"])
        self.assertEqual(rules_for(result, "192.0.2."), [])
        self.assertFalse(result["compromise_assessed"])

    def test_post_login_200_is_not_a_compromise_or_sensitive_path_rule(self):
        rows, context = case_data()
        login = next(row for row in rows if row["target"] == "/login")
        result = lab.analyze([login], context)
        self.assertEqual(result["review_items"], [])
        self.assertEqual(result["sources"][0]["status_counts"], {"200": 1})
        self.assertEqual(result["sources"][0]["method_counts"], {"POST": 1})
        self.assertFalse(result["compromise_assessed"])

    def test_sensitive_200_adds_question_without_establishing_content(self):
        rows, context = case_data("soft-200")
        result = lab.analyze(rows, context)
        self.assertEqual(rules_for(result, "203.0.113."), ["watched-path-variety", "watched-path-200"])
        match = next(item for item in result["review_items"] if item["rule"] == "watched-path-200")
        self.assertEqual(match["event_ids"], ["HTTP-0017"])
        self.assertIn("does not establish", match["meaning"])
        self.assertFalse(result["compromise_assessed"])

    def test_missing_interval_hides_rule_match_and_keeps_warning(self):
        rows, context = case_data("logging-gap")
        result = lab.analyze(rows, context)
        self.assertEqual(result["event_count"], 18)
        self.assertEqual(rules_for(result, "203.0.113."), [])
        self.assertEqual(result["coverage"], "known-gap")
        self.assertIn("lower bounds", result["coverage_warning"])
        self.assertEqual(len(result["gaps"]), 1)

    def test_crawler_only_still_has_volume_but_no_path_prompt(self):
        rows, context = case_data("crawler-only")
        result = lab.analyze(rows, context)
        self.assertEqual(result["event_count"], 16)
        self.assertEqual([item["rule"] for item in result["review_items"]], ["request-volume"])

    def test_volume_threshold_boundary(self):
        rows, context = case_data("crawler-only")
        self.assertEqual(lab.analyze(rows, context, volume_threshold=12)["review_item_count"], 1)
        self.assertEqual(lab.analyze(rows, context, volume_threshold=13)["review_item_count"], 0)

    def test_repeated_path_and_different_queries_do_not_inflate_variety(self):
        rows, context = case_data()
        selected = [row for row in rows if row["source_ip"].startswith("203.0.113.")]
        for index, row in enumerate(selected):
            row["target"] = f"/admin?view={index}"
            row["status"] = "403"
        result = lab.analyze(selected, context)
        self.assertEqual(result["sources"][0]["watched_paths"], ["/admin"])
        self.assertEqual(result["review_items"], [])

    def test_watch_match_is_exact_and_case_sensitive(self):
        rows, context = case_data()
        row = rows[0]
        for target in ("/admin/", "/Admin", "/admin-help", "/guides?next=admin"):
            row["target"] = target
            row["status"] = "200"
            result = lab.analyze([row], context, path_threshold=1)
            self.assertEqual(result["review_items"], [], target)
        row["target"] = "/admin?view=1"
        self.assertEqual(lab.analyze([row], context, path_threshold=1)["review_item_count"], 2)

    def test_separate_addresses_are_not_combined(self):
        rows, context = case_data()
        selected = [row for row in rows if row["target"] in lab.WATCH_PATHS]
        for index, row in enumerate(selected):
            row["source_ip"] = f"192.0.2.{index + 1}"
        result = lab.analyze(selected, context)
        self.assertEqual(result["review_items"], [])

    def test_user_agent_does_not_merge_or_exempt_sources(self):
        rows, context = case_data()
        for row in rows:
            row["user_agent"] = "PracticeSameLabel/9"
        result = lab.analyze(rows, context)
        self.assertEqual(len(result["sources"]), 3)
        self.assertEqual(rules_for(result, "203.0.113."), ["watched-path-variety"])

    def test_file_order_does_not_change_analysis(self):
        rows, context = case_data()
        self.assertEqual(lab.analyze(rows, context), lab.analyze(list(reversed(rows)), context))

    def test_head_zero_body_is_valid_and_preserves_method(self):
        rows, context = case_data()
        head = next(row for row in rows if row["method"] == "HEAD")
        result = lab.analyze([head], context)
        self.assertEqual(result["sources"][0]["method_counts"], {"HEAD": 1})
        self.assertEqual(result["sources"][0]["status_counts"], {"200": 1})
        head["body_bytes"] = "1"
        with self.assertRaisesRegex(ValueError, "HEAD"):
            lab.validate_events([head])


class InputTests(unittest.TestCase):
    def test_reject_invalid_fields_values_and_unsupported_forms(self):
        rows, unused = case_data()
        for field, value in (
            ("synthetic", "false"), ("source_ip", "10.0.0.1"), ("host", "practice.invalid"),
            ("method", "DELETE"), ("target", "https://practice.test/admin"),
            ("target", "//practice.test/admin"), ("target", "/%2e%2e/admin"),
            ("target", "/../admin"), ("status", "099"), ("status", "600"),
            ("body_bytes", "-1"), ("body_bytes", "01"), ("user_agent", "LiveBrowser"),
            ("timestamp", "2032-06-31T09:00:00Z"), ("event_id", "HTTP-1"),
        ):
            with self.subTest(field=field, value=value):
                row = dict(rows[0])
                row[field] = value
                with self.assertRaises(ValueError):
                    lab.validate_events([row])
        with self.assertRaises(ValueError):
            lab.validate_events([dict(rows[0], extra="unexpected")])
        with self.assertRaises(ValueError):
            lab.validate_events([rows[0], rows[0]])
        with self.assertRaises(ValueError):
            lab.validate_events([])

    def test_reject_invalid_thresholds(self):
        rows, context = case_data()
        for value in (0, -1, True, 1.5, 10001):
            with self.assertRaises(ValueError):
                lab.analyze(rows, context, volume_threshold=value)
            with self.assertRaises(ValueError):
                lab.analyze(rows, context, path_threshold=value)

    def test_reject_context_with_unexplained_or_contradictory_gap(self):
        rows, context = case_data("logging-gap")
        broken = copy.deepcopy(context)
        broken["gaps"] = []
        with self.assertRaises(ValueError):
            lab.analyze(rows, broken)
        broken = copy.deepcopy(context)
        broken["gaps"][0]["start"] = context["collection_start"]
        with self.assertRaisesRegex(ValueError, "no retained records"):
            lab.analyze(rows, broken)
        broken = copy.deepcopy(context)
        broken["host"] = "different.test"
        with self.assertRaises(ValueError):
            lab.analyze(rows, broken)

    def test_collection_endpoints_are_inclusive(self):
        rows, context = case_data()
        selected = [dict(rows[0]), dict(rows[1])]
        selected[0]["timestamp"] = context["collection_start"]
        selected[1]["timestamp"] = context["collection_end"]
        self.assertEqual(lab.analyze(selected, context)["event_count"], 2)
        selected[1]["timestamp"] = "2099-01-01T00:00:00Z"
        with self.assertRaises(ValueError):
            lab.analyze(selected, context)


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        lab.RUNS.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="http-test-", dir=lab.RUNS)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_reference_fixture_matches_regeneration(self):
        self.assertEqual(lab.check_case(lab.ROOT / "fixture")["events"], 21)

    def test_all_scenarios_are_deterministic_lf_and_have_matching_hashes(self):
        for scenario in lab.SCENARIOS:
            for seed in (0, 53, 72, 2147483647):
                files = lab.make_case(seed, scenario)
                self.assertEqual(files, lab.make_case(seed, scenario))
                for data in files.values():
                    self.assertNotIn(b"\r", data)
                    self.assertTrue(data.endswith(b"\n"))
                manifest = json.loads(files["manifest.json"])
                for name, expected in manifest["sha256"].items():
                    self.assertEqual(lab.digest(files[name]), expected)

    def test_changed_data_and_rewritten_hash_still_fail_regeneration(self):
        case = self.root / "case"
        lab.save_case(case, lab.make_case(72, "mixed"))
        path = case / "access.csv"
        path.write_bytes(path.read_bytes().replace(b"/robots.txt", b"/different.txt"))
        manifest = json.loads((case / "manifest.json").read_bytes())
        manifest["sha256"]["access.csv"] = lab.digest(path.read_bytes())
        (case / "manifest.json").write_bytes(lab.json_bytes(manifest))
        with self.assertRaisesRegex(ValueError, "seeded regeneration"):
            lab.check_case(case)

    def test_report_checks_calculations_context_hash_and_settings(self):
        case = self.root / "case"
        lab.save_case(case, lab.make_case(72, "soft-200"))
        report = lab.make_report(case, volume_threshold=13, path_threshold=4)
        path = self.root / "report.json"
        lab.save_report(path, report)
        self.assertEqual(lab.check_case(case, path)["report"], "PASS")
        for field, value in (("review_item_count", 99), ("compromise_assessed", True),
                             ("inputs_sha256", {}), ("coverage", "known-gap")):
            tampered = dict(report)
            tampered[field] = value
            path.write_bytes(lab.json_bytes(tampered))
            with self.assertRaises(ValueError):
                lab.check_case(case, path)

    def test_existing_case_and_notes_are_preserved(self):
        case = self.root / "case"
        lab.save_case(case, lab.make_case(72, "mixed"))
        notes = case / "my-notes.txt"
        notes.write_bytes(b"keep my observations\n")
        before = {path.name: path.read_bytes() for path in case.iterdir()}
        with self.assertRaises(FileExistsError):
            lab.save_case(case, lab.make_case(73, "logging-gap"))
        self.assertEqual(before, {path.name: path.read_bytes() for path in case.iterdir()})
        with self.assertRaises(FileExistsError):
            lab.save_report(notes, {"new": True})
        self.assertEqual(notes.read_bytes(), b"keep my observations\n")

    def test_fixture_escape_and_runs_root_outputs_are_refused(self):
        for path in (lab.ROOT / "fixture" / "new.json", lab.ROOT / "new.json",
                     lab.RUNS, lab.RUNS / ".." / "outside.json"):
            with self.assertRaises(ValueError):
                lab.writable_path(path)

    def test_malformed_csv_is_rejected(self):
        path = self.root / "broken.csv"
        path.write_bytes(b"event_id,timestamp\nHTTP-0001,2032-01-01T00:00:00Z\n")
        with self.assertRaises(ValueError):
            lab.load_events(path)


if __name__ == "__main__":
    unittest.main()
