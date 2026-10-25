import copy
import json
import unittest
from unittest.mock import patch
from lab import ROOT, analyse


class ShellTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((ROOT / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def record(self, kind, name="guided"):
        case = self.case(name)
        record = next(r for r in case["data"]["records"] if r["kind"] == kind)
        case["data"]["records"] = [record]
        return case, record

    def decision(self, case):
        return next(iter(analyse(case)["decisions"].values()))

    def test_quotes_repair_actual_argument_count(self):
        case, record = self.record("path")
        self.assertEqual(self.decision(case), "repair-path-quoting")
        record["arguments"] = ["notes with spaces.txt"]
        self.assertEqual(self.decision(case), "requested-file-resolved")

    def test_cwd_and_missing_are_distinct(self):
        case, record = self.record("path")
        record["arguments"] = ["notes with spaces.txt"]
        record["cwd"] = "/lab/other"
        self.assertEqual(self.decision(case), "check-working-directory")
        record["cwd"] = "/lab/run"
        record["existing_files"] = []
        self.assertEqual(self.decision(case), "requested-file-missing")

    def test_windows_root_relative_bases_rejected(self):
        # These are independent of the current drive only when a drive is given.
        for field in ("cwd", "wanted", "existing_files"):
            with self.subTest(field=field):
                case, record = self.record("path", "changed")
                record[field] = [r"\Lab\run\notes with spaces.txt"] if field == "existing_files" else r"\Lab\run"
                with self.assertRaises(ValueError):
                    analyse(case)
        case, record = self.record("path", "changed")
        record.update(cwd=r"\Lab\run", wanted=r"\Lab\run\notes with spaces.txt",
                      arguments=["notes with spaces.txt"], existing_files=[r"\Lab\run\notes with spaces.txt"])
        with self.assertRaises(ValueError):
            analyse(case)

    def test_windows_drive_rooted_mixed_case_and_separators(self):
        case, record = self.record("path", "changed")
        record.update(cwd="C:/Lab/Run", wanted=r"c:\lab\run\notes with spaces.txt",
                      arguments=[r".\notes with spaces.txt"], existing_files=["C:/LAB/RUN/notes with spaces.txt"])
        self.assertEqual(self.decision(case), "requested-file-resolved")
        record["arguments"] = ["c:/LAB/Run/notes with spaces.txt"]
        self.assertEqual(self.decision(case), "requested-file-resolved")

    def test_windows_unc_share_supported(self):
        case, record = self.record("path", "changed")
        record.update(cwd=r"\\files.test\practice\run", wanted=r"\\files.test\practice\run\notes with spaces.txt",
                      arguments=["notes with spaces.txt"], existing_files=["//FILES.TEST/practice/run/notes with spaces.txt"])
        self.assertEqual(self.decision(case), "requested-file-resolved")
        record["arguments"] = ["//files.test/practice/run/notes with spaces.txt"]
        self.assertEqual(self.decision(case), "requested-file-resolved")
        record["cwd"] = r"\\files.test\practice"
        record["arguments"] = [r"run\notes with spaces.txt"]
        self.assertEqual(self.decision(case), "requested-file-resolved")

    def test_windows_incomplete_unc_and_device_bases_rejected(self):
        for value in (r"\\files.test", "\\\\files.test\\", r"\\\files.test\practice", r"\\files.test\..\run",
                      r"\\?\C:\Lab", r"\\.\C:\Lab", r"C:Lab\run", "C:", "/Lab/run"):
            with self.subTest(value=value):
                case, record = self.record("path", "changed")
                record["cwd"] = value
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_windows_omitted_drive_state_arguments_rejected(self):
        for value in (r"C:notes with spaces.txt", r"D:notes with spaces.txt", "C:", r"\Lab\run\notes with spaces.txt",
                      "/Lab/run/notes with spaces.txt", r"\\files.test", r"\\?\C:\Lab\note.txt"):
            with self.subTest(value=value):
                case, record = self.record("path", "changed")
                record["arguments"] = [value]
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_windows_validation_does_not_depend_on_isabs_version(self):
        case, record = self.record("path", "changed")
        record["cwd"] = r"C:\Lab\run"
        with patch("lab.ntpath.isabs", side_effect=AssertionError("version-dependent predicate used")):
            self.assertEqual(self.decision(case), "requested-file-resolved")
            record["cwd"] = r"\Lab\run"
            with self.assertRaises(ValueError):
                analyse(case)

    def test_grep_one_is_empty_result(self):
        case, record = self.record("search")
        self.assertEqual(self.decision(case), "no-matching-lines")
        record.update(exit_status=2, stderr="cannot read supplied file")
        self.assertEqual(self.decision(case), "search-command-error")

    def test_partial_matches_with_grep_error_not_success(self):
        case, record = self.record("search")
        record.update(exit_status=2, match_count=1, stderr="second file missing")
        self.assertEqual(self.decision(case), "search-command-error")

    def test_cmdlet_ignores_stale_native_exit(self):
        case, record = self.record("search", "changed")
        self.assertEqual(record["last_native_exit"], 9)
        self.assertEqual(self.decision(case), "no-matching-lines")
        record.update(success=False, stderr="Access denied")
        self.assertEqual(self.decision(case), "search-command-error")

    def test_pipeline_last_status_and_pipefail(self):
        case, record = self.record("pipeline", "challenge")
        self.assertEqual(self.decision(case), "earlier-nonzero-hidden")
        record.update(pipefail=True, reported_status=1)
        self.assertEqual(self.decision(case), "pipeline-nonzero-review-stage")
        record.update(statuses=[2, 1, 0], reported_status=1)
        self.assertEqual(self.decision(case), "pipeline-nonzero-review-stage")

    def test_capacity_exact_boundary_and_one_short(self):
        case, record = self.record("capacity")
        record.update(available_bytes=100, required_bytes=100)
        self.assertEqual(self.decision(case), "stated-space-budget-met")
        record["available_bytes"] = 99
        self.assertEqual(self.decision(case), "stated-space-budget-short")

    def test_unknown_service_not_stopped(self):
        case, record = self.record("service")
        record.update(query_succeeded=False, state=None)
        self.assertEqual(self.decision(case), "service-query-inconclusive")

    def test_listener_ipv6_wildcard_and_unknown_owner(self):
        case, record = self.record("listener")
        record.update(bind="::", owner_pid=None)
        self.assertEqual(self.decision(case), "wildcard-listener-review")
        record["bind"] = "::1"
        self.assertEqual(self.decision(case), "listener-owner-unresolved")

    def test_listener_mismatched_pid(self):
        case, record = self.record("listener")
        record["owner_pid"] = record["expected_pid"] + 1
        self.assertEqual(self.decision(case), "listener-pid-mismatch")

    def test_process_name_not_enough(self):
        case, record = self.record("process")
        record["pid"] = record["expected_pid"] + 1
        self.assertEqual(self.decision(case), "process-pid-mismatch")

    def test_contradictions_rejected(self):
        for kind, updates, name in [("search", {"exit_status": 0}, "guided"),
                                     ("pipeline", {"reported_status": 2}, "challenge"),
                                     ("service", {"query_succeeded": False}, "guided"),
                                     ("capacity", {"available_bytes": True}, "guided"),
                                     ("listener", {"port": 65536}, "guided")]:
            with self.subTest(kind=kind):
                case, record = self.record(kind, name)
                record.update(updates)
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_duplicate_unknown_extra_rejected(self):
        case = self.case()
        case["data"]["records"].append(copy.deepcopy(case["data"]["records"][0]))
        with self.assertRaises(ValueError):
            analyse(case)
        case, record = self.record("capacity")
        record["kind"] = "execute"
        with self.assertRaises(ValueError):
            analyse(case)
        record["kind"] = "capacity"
        record["extra"] = 1
        with self.assertRaises(ValueError):
            analyse(case)

    def test_input_preserved(self):
        case = self.case()
        before = copy.deepcopy(case)
        analyse(case)
        self.assertEqual(case, before)

    def test_unhashable_enum_rejected_cleanly(self):
        for kind, field in (("service", "state"), ("listener", "bind")):
            case, record = self.record(kind)
            record[field] = []
            with self.assertRaises(ValueError):
                analyse(case)
        case = self.case()
        case["data"]["shell"] = []
        with self.assertRaises(ValueError):
            analyse(case)


if __name__ == "__main__":
    unittest.main()
