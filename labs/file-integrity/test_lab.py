"""Tests for evidence classification, baseline limits, and bounded file handling."""

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import lab


class IntegrityLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def case(self, variant="mixed", name="practice", seed=23):
        run = self.root / name
        lab.generate(run, variant, seed)
        lab.baseline(run, "reference", "baseline.json")
        return run

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lab.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_mixed_case_has_one_approved_and_three_unexplained_changes(self):
        result = lab.check(self.case(), "baseline.json")
        self.assertFalse(result["passed"])
        self.assertEqual(result["baseline_status"], "matches-exercise-anchor")
        self.assertEqual(result["counts"], {"unchanged": 1, "approved": 1, "unexpected": 3})
        observed = {row["path"]: (row["change"], row["assessment"]) for row in result["observations"]}
        self.assertEqual(observed["docs/notice.txt"], ("modified", "approved"))
        self.assertEqual(observed["config/service.txt"], ("modified", "unexpected"))
        self.assertEqual(observed["docs/temporary-note.txt"], ("added", "unexpected"))
        self.assertEqual(observed["reports/archive.txt"], ("deleted", "unexpected"))

    def test_approved_change_is_not_an_alert(self):
        result = lab.check(self.case("approved"), "baseline.json")
        self.assertTrue(result["passed"])
        self.assertEqual(result["counts"], {"unchanged": 3, "approved": 1, "unexpected": 0})

    def test_approved_addition_and_deletion_do_not_become_alerts(self):
        result = lab.check(self.case("replacement"), "baseline.json")
        self.assertTrue(result["passed"])
        approved = {(row["path"], row["change"]) for row in result["observations"] if row["assessment"] == "approved"}
        self.assertEqual(approved, {("docs/notice.txt", "modified"),
                                    ("reports/archive.txt", "deleted"), ("reports/current.txt", "added")})

    def test_suspect_baseline_hides_earlier_change_but_does_not_pass(self):
        run = self.case("suspect-baseline")
        result = lab.check(run, "baseline.json")
        self.assertFalse(result["passed"])
        self.assertEqual(result["baseline_status"], "unverified-no-anchor")
        self.assertEqual(result["counts"]["unexpected"], 0)
        row = next(row for row in result["observations"] if row["path"] == "config/service.txt")
        self.assertEqual(row["change"], "unchanged")
        self.assertIn(b"remote_access=enabled", (run / "current/config/service.txt").read_bytes())

    def test_using_current_as_baseline_cannot_silence_anchor_warning(self):
        run = self.case()
        lab.baseline(run, "current", "current-baseline.json")
        result = lab.check(run, "current-baseline.json")
        self.assertEqual(result["counts"]["unexpected"], 0)
        self.assertEqual(result["baseline_status"], "does-not-match-exercise-anchor")
        self.assertFalse(result["passed"])

    def test_approval_requires_exact_before_and_after_hashes(self):
        run = self.case("approved")
        (run / "current/docs/notice.txt").write_bytes(b"Opening time: 11:00\n")
        result = lab.check(run, "baseline.json")
        self.assertEqual(result["counts"]["unexpected"], 1)
        self.assertEqual(result["unused_approvals"], ["docs/notice.txt"])
        before = lab.load_json(run / "baseline.json")
        after = lab.inventory_tree(run / "current")
        approval = lab.load_json(run / "approvals.json")
        approval["changes"][0]["after_sha256"] = after["files"]["docs/notice.txt"]["sha256"]
        approval["changes"][0]["before_sha256"] = "0" * 64
        rows, _ = lab.compare(before, after, approval)
        self.assertEqual(next(row for row in rows if row["path"] == "docs/notice.txt")["assessment"], "unexpected")

    def test_complete_current_file_removal_is_reported(self):
        run = self.case()
        for path in (run / "current").rglob("*"):
            if path.is_file():
                path.unlink()
        result = lab.check(run, "baseline.json")
        self.assertEqual(result["counts"], {"unchanged": 0, "approved": 0, "unexpected": 4})
        self.assertTrue(all(row["change"] == "deleted" for row in result["observations"]))

    def test_path_traversal_absolute_paths_and_windows_names_rejected(self):
        for name in ("../outside.txt", "/outside.txt", "c:/secret.txt", "folder\\secret.txt",
                     "a//b.txt", "a/./b.txt", "a/../b.txt", "con.txt", "a/aux", "a.", "UPPER.txt"):
            with self.subTest(name=name), self.assertRaises(lab.InputError):
                lab.relative_name(name)
        run = self.case()
        with self.assertRaises(lab.InputError):
            lab.baseline(run, "reference", "../escaped.json")
        before = lab.load_json(run / "baseline.json")
        before["files"]["../outside.txt"] = next(iter(before["files"].values()))
        with self.assertRaises(lab.InputError):
            lab.validate_inventory(before)

    def test_duplicate_keys_and_invalid_baseline_shapes_rejected(self):
        bad = self.root / "bad.json"
        bad.write_bytes(b'{"schema_version":1,"schema_version":1}')
        with self.assertRaises(lab.InputError):
            lab.load_json(bad)
        valid = lab.load_json(self.case() / "baseline.json")
        for mutation in (lambda x: x.update(schema_version=True),
                         lambda x: x["files"]["docs/contact.txt"].update(bytes=-1),
                         lambda x: x["files"]["docs/contact.txt"].update(sha256="bad"),
                         lambda x: x["files"].update(docs={"bytes": 0, "sha256": "0" * 64})):
            value = copy.deepcopy(valid)
            mutation(value)
            with self.assertRaises(lab.InputError):
                lab.validate_inventory(value)

    def test_duplicate_approvals_rejected(self):
        value = lab.load_json(self.case() / "approvals.json")
        value["changes"].append(dict(value["changes"][0]))
        with self.assertRaises(lab.InputError):
            lab.validate_approvals(value)

    def test_generate_and_baseline_refuse_overwrite_without_touching_files(self):
        run = self.case()
        original = (run / "baseline.json").read_bytes()
        with self.assertRaises(lab.InputError):
            lab.generate(run, "approved", 3)
        with self.assertRaises(lab.InputError):
            lab.baseline(run, "current", "baseline.json")
        self.assertEqual((run / "baseline.json").read_bytes(), original)
        empty = self.root / "already-there"
        empty.mkdir()
        with self.assertRaises(lab.InputError):
            lab.generate(empty, "mixed", 3)
        self.assertEqual(list(empty.iterdir()), [])

    def test_requires_generated_sandbox_and_existing_parent(self):
        with self.assertRaises(lab.InputError):
            lab.baseline(self.root, "reference", "baseline.json")
        with self.assertRaises(lab.InputError):
            lab.generate(self.root / "missing" / "run", "mixed", 23)

    def test_linked_file_and_linked_directory_rejected_when_supported(self):
        run = self.case()
        outside = self.root / "outside.txt"
        outside.write_bytes(b"do not read this\n")
        link = run / "current" / "linked.txt"
        try:
            link.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symbolic link creation unavailable: {exc}")
        with self.assertRaises(lab.InputError):
            lab.check(run, "baseline.json")
        link.unlink()
        link = run / "current" / "linked-folder"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(lab.InputError):
            lab.check(run, "baseline.json")

    def test_windows_reparse_attribute_rejected_without_traversal(self):
        fake = mock.Mock(st_mode=stat_mode_directory(), st_file_attributes=0x400)
        with mock.patch.object(Path, "lstat", return_value=fake), self.assertRaises(lab.InputError):
            lab.safe_path(self.root)

    def test_hard_link_rejected_when_supported(self):
        run = self.case()
        target = self.root / "outside.txt"
        target.write_bytes(b"outside dummy content\n")
        try:
            os.link(target, run / "current/linked.txt")
        except OSError as exc:
            self.skipTest(f"hard link creation unavailable: {exc}")
        with self.assertRaises(lab.InputError):
            lab.check(run, "baseline.json")

    def test_size_limit_rejected(self):
        run = self.case()
        (run / "current/too-large.txt").write_bytes(b"x" * (lab.MAX_BYTES + 1))
        with self.assertRaises(lab.InputError):
            lab.check(run, "baseline.json")

    def test_generation_is_deterministic_with_lf_bytes_and_seed_changes_data(self):
        one = self.case("mixed", "one", 23)
        two = self.case("mixed", "two", 23)
        three = self.case("mixed", "three", 71)
        for path in one.rglob("*"):
            if path.is_file():
                relative = path.relative_to(one)
                self.assertEqual(path.read_bytes(), (two / relative).read_bytes())
                self.assertNotIn(b"\r", path.read_bytes())
        self.assertNotEqual((one / "baseline.json").read_bytes(), (three / "baseline.json").read_bytes())

    def test_baseline_json_reformatting_does_not_change_anchor(self):
        run = self.case("approved")
        value = lab.load_json(run / "baseline.json")
        (run / "baseline.json").write_text(json.dumps(value), encoding="utf-8")
        self.assertTrue(lab.check(run, "baseline.json")["passed"])

    def test_exit_codes_and_json_error_channel(self):
        for variant, expected in (("approved", 0), ("mixed", 1), ("replacement", 0), ("suspect-baseline", 1)):
            run = self.case(variant, variant)
            code, out, err = self.cli("check", "--run", str(run), "--json")
            self.assertEqual(code, expected)
            self.assertEqual(json.loads(out)["command"], "check")
            self.assertEqual(err, "")
        code, out, err = self.cli("check", "--run", str(run), "--baseline", "../escape.json", "--json")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("error", json.loads(err))


def stat_mode_directory():
    import stat
    return stat.S_IFDIR | 0o755


if __name__ == "__main__":
    unittest.main()
