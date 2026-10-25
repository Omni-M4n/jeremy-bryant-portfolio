import copy
import json
import io
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import lab
import practice

def sample(): return json.loads((lab.ROOT / "fixtures/guided.json").read_text())

class PatchTests(unittest.TestCase):
    def outcome(self, **changes):
        c=sample();c["data"]["changes"][0].update(changes)
        return lab.analyse(c)["decisions"]["p1"]

    def test_priority_and_boundaries(self):
        self.assertEqual(self.outcome(source="unverified",install_exit=1),"source-unverified")
        self.assertEqual(self.outcome(install_exit=1),"install-error-investigate")
        self.assertEqual(self.outcome(smoke="not-run"),"need-smoke-test")
        self.assertEqual(self.outcome(smoke="fail"),"regression-recovery-needed")
        self.assertEqual(self.outcome(rollback_version="1.0",rollback_smoke="pass"),"update-and-rollback-verified")
        self.assertEqual(self.outcome(rollback_version="1.0",rollback_smoke="fail"),"update-verified-rollback-incomplete")

    def test_exact_versions(self):
        self.assertEqual(self.outcome(installed_version="1.10"),"version-not-confirmed")

    def test_invalid(self):
        for change in [{"install_exit":True},{"rollback_smoke":"pass"},{"target_version":"1.0"},{"smoke":"unknown"}]:
            with self.assertRaises(ValueError): self.outcome(**change)
        c=sample();c["data"]["changes"] *= 2
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_actual_temporary_files(self):
        for broken in [False,True]:
            receipt=practice.exercise(broken)
            self.assertEqual(receipt["update_smoke_passed"],not broken)
            self.assertTrue(receipt["rollback_bytes_match"])
            self.assertTrue(receipt["rollback_smoke_passed"])
            self.assertTrue(receipt["temporary_directory_removed"])
            self.assertNotEqual(receipt["before_sha256"],receipt["applied_sha256"])

    def test_no_input_change(self):
        c=sample();before=copy.deepcopy(c);lab.analyse(c);self.assertEqual(c,before)

    def test_receipt_aliases_fail_before_writes(self):
        invalid = [
            "run/NUL.json", "run/nUl.extra.json", "run/CON.json", "run/prn.json",
            "run/AUX.json", "run/COM1.json", "run/lPt9.json", "run/COM\u00b9.json",
            "run/NUL/receipt.json", "run/receipt.json:extra.json",
            "run/folder:stream/receipt.json", "run/folder./receipt.json",
            "run/folder /receipt.json", "run/receipt.json.", "run/receipt.json ",
            "run/./receipt.json", "run/../receipt.json", "run//receipt.json",
            "run/hidden\x00.json", "run/hidden\r.json", "run/hidden\t.json",
            "run/what?.json", "run/a|b.json", "run/a*.json",
        ]
        for name in invalid:
            with self.subTest(name=name), patch.object(practice, "exercise") as exercise:
                with patch.object(Path, "mkdir") as mkdir, patch.object(Path, "write_bytes") as write:
                    with patch.object(sys, "argv", ["practice.py", "--receipt", name]):
                        with self.assertRaises(ValueError): practice.main()
                    exercise.assert_not_called()
                    mkdir.assert_not_called()
                    write.assert_not_called()

    def test_valid_nested_receipts_and_existing_refusal(self):
        run_root = lab.ROOT / "run"
        run_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="receipt-tests-", dir=run_root) as temporary:
            area = Path(temporary)
            self.assertIn(run_root.resolve(), area.resolve().parents)
            with patch.object(practice, "ROOT", area):
                for broken, name in [(False, "run/COM10/Receipt_01.json"),
                                     (True, "run/Nested-2/receipt.extra.json")]:
                    args = ["practice.py", "--receipt", name] + (["--regression"] if broken else [])
                    output = io.StringIO()
                    with patch.object(sys, "argv", args), redirect_stdout(output): practice.main()
                    saved = json.loads((area / name).read_text())
                    self.assertEqual(saved, json.loads(output.getvalue()))
                    self.assertEqual(saved["update_smoke_passed"], not broken)
                    self.assertTrue(saved["rollback_bytes_match"])
                    self.assertTrue(saved["temporary_directory_removed"])
                    before = (area / name).read_bytes()
                    with patch.object(practice, "exercise") as exercise, patch.object(sys, "argv", args):
                        with self.assertRaises(ValueError): practice.main()
                        exercise.assert_not_called()
                    self.assertEqual((area / name).read_bytes(), before)

if __name__ == "__main__": unittest.main()
