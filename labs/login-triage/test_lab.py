"""Checks of timing semantics and input handling, not learner grading."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

import lab


def event(identifier, second, outcome="failure", user="practice-check", source="192.0.2.10"):
    base = datetime(2032, 1, 1, tzinfo=timezone.utc)
    return {"event_id": f"SYN-{identifier:04d}", "timestamp": lab.stamp(base + timedelta(seconds=second)),
            "user": user, "source_ip": source, "outcome": outcome,
            "reason": "invalid_password" if outcome == "failure" else "accepted", "synthetic": "true"}


class TimingTests(unittest.TestCase):
    def test_exact_threshold_and_one_below(self):
        rows = [event(index + 1, index * 30) for index in range(5)]
        self.assertEqual(lab.analyze(rows[:4])["candidate_window_count"], 0)
        result = lab.analyze(rows)
        self.assertEqual(result["candidate_window_count"], 1)
        self.assertEqual(result["candidates"][0]["failure_count"], 5)

    def test_inclusive_window_boundary(self):
        rows = [event(1, 0), event(2, 300)]
        self.assertEqual(lab.analyze(rows, threshold=2)["candidate_window_count"], 1)
        rows[1] = event(2, 301)
        self.assertEqual(lab.analyze(rows, threshold=2)["candidate_window_count"], 0)

    def test_success_is_not_a_failure_and_does_not_reset_window(self):
        rows = [event(1, 0), event(2, 30, "success"), event(3, 60)]
        self.assertEqual(lab.analyze(rows, threshold=3)["candidate_window_count"], 0)
        candidate = lab.analyze(rows, threshold=2)["candidates"][0]
        self.assertEqual(candidate["failure_event_ids"], ["SYN-0001", "SYN-0003"])
        self.assertEqual(candidate["linked_successes"], [])

    def test_success_link_boundary_and_same_second(self):
        rows = [event(1, 10), event(2, 10, "success"), event(3, 130, "success"), event(4, 131, "success")]
        result = lab.analyze(rows, threshold=1)
        self.assertEqual([row["event_id"] for row in result["candidates"][0]["linked_successes"]], ["SYN-0003"])
        self.assertEqual(lab.analyze(rows, threshold=1, success_seconds=0)["candidates"][0]["linked_successes"], [])

    def test_same_second_failures_form_one_complete_window(self):
        rows = [event(1, 10), event(2, 10), event(3, 10)]
        result = lab.analyze(rows, threshold=2)
        self.assertEqual(result["candidate_window_count"], 1)
        self.assertEqual(result["candidates"][0]["failure_count"], 3)

    def test_out_of_order_input_has_identical_result(self):
        rows = [event(1, 0), event(2, 40), event(3, 80), event(4, 100, "success")]
        self.assertEqual(lab.analyze(rows, threshold=3), lab.analyze(list(reversed(rows)), threshold=3))

    def test_accounts_and_addresses_are_not_combined(self):
        rows = [event(1, 0), event(2, 20, user="practice-other"), event(3, 40, source="192.0.2.11")]
        self.assertEqual(lab.analyze(rows, threshold=2)["candidate_window_count"], 0)

    def test_success_requires_same_account_and_address(self):
        rows = [event(1, 0), event(2, 20, "success", source="192.0.2.11"),
                event(3, 20, "success", user="practice-other"), event(4, 30, "success")]
        linked = lab.analyze(rows, threshold=1)["candidates"][0]["linked_successes"]
        self.assertEqual([value["event_id"] for value in linked], ["SYN-0004"])

    def test_overlapping_windows_are_explicit(self):
        rows = [event(index + 1, index * 40) for index in range(6)]
        result = lab.analyze(rows)
        self.assertEqual(result["candidate_window_count"], 2)
        self.assertEqual(result["candidate_pair_count"], 1)
        self.assertEqual([value["failure_count"] for value in result["candidates"]], [5, 6])


class InputTests(unittest.TestCase):
    def test_invalid_settings(self):
        for settings in ({"threshold": 0}, {"threshold": True}, {"threshold": 1.5},
                         {"window_seconds": 0}, {"window_seconds": 86401}, {"success_seconds": -1}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                lab.analyze([event(1, 0)], **settings)

    def test_invalid_events(self):
        changes = ({"timestamp": "2032-01-01T00:00:00"}, {"timestamp": "2032-02-30T00:00:00Z"},
                   {"outcome": "unknown"}, {"reason": "accepted"}, {"source_ip": "10.0.0.1"},
                   {"source_ip": "not-an-address"}, {"user": "real-name"}, {"synthetic": "false"},
                   {"synthetic": True}, {"event_id": "event-1"})
        for change in changes:
            row = event(1, 0)
            row.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                lab.validate_events([row])

    def test_missing_extra_duplicate_and_empty_events(self):
        missing = event(1, 0)
        missing.pop("reason")
        extra = event(1, 0)
        extra["unexpected"] = "value"
        for rows in ([], [missing], [extra], [event(1, 0), event(1, 20)], [None]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                lab.validate_events(rows)

    def test_invalid_seed_and_scenario(self):
        for seed, scenario in ((-1, "baseline"), (True, "baseline"), (1, "unknown")):
            with self.subTest(seed=seed, scenario=scenario), self.assertRaises(ValueError):
                lab.make_case(seed, scenario)

    def test_output_cannot_escape_runs_or_replace_fixture(self):
        for path in ("fixture/auth.csv", "../outside.json", "runs/../../outside.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                lab.writable_path(path)


class FixtureTests(unittest.TestCase):
    def setUp(self):
        lab.RUNS.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="test-", dir=lab.RUNS)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_committed_fixture_is_reproducible(self):
        result = lab.verify_case(lab.ROOT / "fixture")
        self.assertEqual(result["events"], 19)
        self.assertEqual(result["files_verified"], 4)

    def test_scenario_changes_affect_findings(self):
        for scenario, expected_windows, expected_links in (("baseline", 2, 2), ("late-success", 2, 0), ("distributed", 0, 0)):
            with self.subTest(scenario=scenario):
                case = self.directory / scenario
                lab.save_case(case, lab.make_case(41, scenario))
                result = lab.make_report(case / "auth.csv")
                self.assertEqual(result["candidate_window_count"], expected_windows)
                self.assertEqual(sum(len(row["linked_successes"]) for row in result["candidates"]), expected_links)
                self.assertEqual(lab.load_events(case / "auth.csv"), lab.load_events(case / "auth.jsonl"))

    def test_wider_window_includes_stale_service(self):
        result = lab.make_report(lab.ROOT / "fixture" / "auth.csv", window_seconds=3600)
        self.assertEqual(result["candidate_pair_count"], 2)
        self.assertEqual(result["candidate_window_count"], 4)

    def test_report_verification_and_tamper_detection(self):
        case = self.directory / "case"
        lab.save_case(case, lab.make_case(72, "baseline"))
        report = lab.make_report(case / "auth.csv")
        report_path = self.directory / "report.json"
        report_path.write_text(lab.json_text(report), encoding="utf-8")
        self.assertEqual(lab.verify_case(case, report_path)["report"], "PASS")
        report["candidates"][0]["failure_count"] += 1
        report_path.write_text(lab.json_text(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "recalculation"):
            lab.verify_case(case, report_path)

    def test_data_tampering_fails_even_if_manifest_hash_changed(self):
        case = self.directory / "case"
        lab.save_case(case, lab.make_case(41, "baseline"))
        data = (case / "auth.csv").read_bytes().replace(b"invalid_password", b"wrong_password", 1)
        (case / "auth.csv").write_bytes(data)
        manifest = json.loads((case / "manifest.json").read_text(encoding="utf-8"))
        manifest["sha256"]["auth.csv"] = lab.digest(data)
        (case / "manifest.json").write_text(lab.json_text(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "seeded regeneration"):
            lab.verify_case(case)

    def test_malformed_csv_and_jsonl_fail(self):
        bad_csv = self.directory / "bad.csv"
        bad_jsonl = self.directory / "bad.jsonl"
        bad_csv.write_text("timestamp,user\n2032-01-01,practice-x\n", encoding="utf-8")
        bad_jsonl.write_text('{"event_id":', encoding="utf-8")
        for path in (bad_csv, bad_jsonl):
            with self.subTest(path=path), self.assertRaises(ValueError):
                lab.load_events(path)

    def test_duplicate_json_fields_are_rejected(self):
        row = lab.load_events(lab.ROOT / "fixture" / "auth.jsonl")[0]
        path = self.directory / "duplicate.jsonl"
        for value in (row["outcome"], "success" if row["outcome"] == "failure" else "failure"):
            text = '{"outcome":' + json.dumps(value) + ',' + json.dumps(row)[1:]
            path.write_text(text + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON field"):
                lab.load_events(path)


if __name__ == "__main__":
    unittest.main()
