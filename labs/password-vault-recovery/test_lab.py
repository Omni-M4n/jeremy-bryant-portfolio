"""Independent boundary and invalid-input tests for password-vault-recovery."""
import copy
import json
from pathlib import Path
import unittest
import lab


class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((Path(__file__).parent / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_analysis_preserves_input(self):
        c = self.case()
        before = copy.deepcopy(c)
        lab.analyse(c)
        self.assertEqual(c, before)

    def test_length_boundary_and_unique_labels(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"], {"e1": "meets-practice-checks", "e2": "below-practice-length", "backup": "meets-practice-checks"})

    def test_duplicate_labels_and_plaintext(self):
        result = lab.analyse(self.case("changed"))["decisions"]
        self.assertTrue(result["e1"].startswith("reused+"))
        self.assertEqual(result["backup"], "plaintext-exposure")

    def test_tested_missing_copy_is_contradictory(self):
        c = self.case()
        c["data"]["backup"].update(copy_exists=False, unlock_test=True)
        with self.assertRaises(ValueError):
            lab.analyse(c)

    def test_bad_length_and_account(self):
        for field, value in [("length", True), ("account", "example.com")]:
            c = self.case()
            c["data"]["entries"][0][field] = value
            with self.assertRaises(ValueError):
                lab.analyse(c)

    def test_actual_dummy_backup_restore_and_cleanup(self):
        import tempfile
        import vault
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "practice"
            vault.operate(folder, "init")
            original = (folder / "store.json").read_bytes()
            vault.operate(folder, "backup")
            vault.operate(folder, "hold")
            self.assertFalse((folder / "store.json").exists())
            self.assertEqual((folder / "held-original.json").read_bytes(), original)
            vault.operate(folder, "restore")
            self.assertEqual((folder / "store.json").read_bytes(), original)
            self.assertTrue(vault.operate(folder, "verify")["matches_backup"])
            vault.operate(folder, "export")
            self.assertEqual((folder / "export.json").read_bytes(), original)
            vault.operate(folder, "clean")
            self.assertFalse(folder.exists())

    def test_overwrite_and_unexpected_cleanup_refused(self):
        import tempfile
        import vault
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "practice"
            vault.operate(folder, "init")
            with self.assertRaises(ValueError):
                vault.operate(folder, "init")
            vault.operate(folder, "backup")
            with self.assertRaises(ValueError):
                vault.operate(folder, "backup")
            (folder / "other.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaises(ValueError):
                vault.operate(folder, "clean")
            self.assertTrue((folder / "other.txt").exists())


if __name__ == "__main__":
    unittest.main()
