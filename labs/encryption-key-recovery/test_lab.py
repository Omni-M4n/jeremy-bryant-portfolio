"""Known vectors and independently specified recovery dependency boundaries."""
import copy
import json
import unittest
from lab import analyse, ROOT

ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def load(name="guided"):
    return json.loads((ROOT / "fixtures" / f"{name}.json").read_text(encoding="utf-8"))


class DomainTests(unittest.TestCase):
    def test_explicit_references(self):
        for name in ("guided", "changed", "challenge"):
            with self.subTest(case=name):
                expected = json.loads((ROOT / "reference" / f"{name}.json").read_text(encoding="utf-8"))
                self.assertEqual(analyse(load(name)), expected)

    def test_rfc4648_known_base64_vectors(self):
        for source, encoded in (("", ""), ("f", "Zg=="), ("fo", "Zm8="), ("foo", "Zm9v"), ("foobar", "Zm9vYmFy")):
            with self.subTest(source=source):
                case = load()
                case["data"]["samples"][0].update(source_text=source, supplied_output=encoded, goal="transport")
                self.assertEqual(analyse(case)["decisions"]["encoded-note"], "base64:matches:fits-stated-goal")

    def test_known_empty_sha256_and_empty_text_are_not_missing(self):
        case = load()
        case["data"]["samples"][1].update(source_text="", supplied_output=EMPTY)
        case["data"]["backups"][0].update(restored_text="", baseline_sha256=EMPTY)
        result = analyse(case)["decisions"]
        self.assertEqual(result["digest-note"], "sha256:matches:fits-stated-goal")
        self.assertEqual(result["blue-copy"], "restore-verified-in-supplied-evidence")

    def test_newline_changes_bytes_and_digest(self):
        result = analyse(load("changed"))["decisions"]
        self.assertEqual(result["newline-encoding"], "base64:matches:fits-stated-goal")
        self.assertEqual(result["newline-digest"], "sha256:differs:fits-stated-goal")

    def test_unicode_is_utf8_not_character_count(self):
        case = load()
        case["data"]["samples"][0].update(source_text="é", supplied_output="w6k=", goal="transport")
        self.assertEqual(analyse(case)["decisions"]["encoded-note"], "base64:matches:fits-stated-goal")
        self.assertIn("2 UTF-8 bytes", analyse(case)["observations"][0])

    def test_neither_encoding_nor_hashing_meets_confidentiality_goal(self):
        case = load()
        case["data"]["samples"][1]["goal"] = "confidentiality"
        result = analyse(case)["decisions"]
        self.assertEqual(result["encoded-note"], "base64:matches:wrong-purpose")
        self.assertEqual(result["digest-note"], "sha256:matches:wrong-purpose")

    def test_replacement_key_and_duplicate_ciphertext_do_not_replace_required_key(self):
        result = analyse(load("changed"))["decisions"]
        self.assertEqual(result["archive-copy"], "required-key-unavailable")
        self.assertEqual(result["replica-copy"], "required-key-unavailable")

    def test_access_and_content_evidence_are_separate(self):
        result = analyse(load("challenge"))["decisions"]
        self.assertEqual(result["backup-c1"], "key-access-denied")
        self.assertEqual(result["backup-c2"], "restored-content-unverified")
        self.assertEqual(result["backup-c3"], "restored-content-mismatch")
        self.assertEqual(result["backup-c4"], "key-state-unknown")

    def test_key_state_and_permission_boundaries(self):
        cases = (("available", "allowed", "restore-unproven"),
                 ("available", "unknown", "key-access-unknown"),
                 ("disabled", "allowed", "key-disabled-review-recovery"),
                 ("unknown", "allowed", "key-state-unknown"))
        for state, access, expected in cases:
            with self.subTest(state=state, access=access):
                case = load()
                case["data"]["keys"][0].update(state=state, access=access)
                case["data"]["backups"][0].update(attempt="not-run", restored_text=None)
                self.assertEqual(analyse(case)["decisions"]["blue-copy"], expected)

    def test_absent_ciphertext_and_changed_ciphertext_are_not_missing_key(self):
        case = load()
        row = case["data"]["backups"][0]
        row.update(ciphertext_present=False, ciphertext_check="not-checked", attempt="not-run", restored_text=None)
        self.assertEqual(analyse(case)["decisions"]["blue-copy"], "ciphertext-missing")
        row.update(ciphertext_present=True, ciphertext_check="differs")
        self.assertEqual(analyse(case)["decisions"]["blue-copy"], "ciphertext-changed-investigate")

    def test_valid_key_does_not_guarantee_success(self):
        case = load()
        case["data"]["backups"][0].update(attempt="failure", restored_text=None)
        self.assertEqual(analyse(case)["decisions"]["blue-copy"], "decrypt-failed-investigate")

    def test_changed_ciphertext_is_flagged_even_with_matching_supplied_plaintext(self):
        case = load()
        case["data"]["backups"][0]["ciphertext_check"] = "differs"
        self.assertEqual(analyse(case)["decisions"]["blue-copy"], "ciphertext-changed-investigate")
        self.assertIn("restored_check=matches", analyse(case)["observations"][2])

    def test_content_comparison_can_support_restore_without_ciphertext_baseline(self):
        case = load()
        case["data"]["backups"][0]["ciphertext_check"] = "not-checked"
        self.assertEqual(analyse(case)["decisions"]["blue-copy"], "restore-verified-in-supplied-evidence")
        self.assertIn("ciphertext_check=not-checked", analyse(case)["observations"][2])

    def test_inputs_preserved(self):
        case = load()
        before = copy.deepcopy(case)
        analyse(case)
        self.assertEqual(case, before)

    def test_invalid_and_contradictory_inputs_rejected(self):
        changes = [
            lambda c: c["data"].update(extra=True),
            lambda c: c["data"]["samples"][0].update(method="rot13"),
            lambda c: c["data"]["samples"][0].update(supplied_output="Y WJj"),
            lambda c: c["data"]["samples"][0].update(supplied_output="Zh=="),
            lambda c: c["data"]["samples"][0].update(source_text="a" * 1025),
            lambda c: c["data"]["samples"][1].update(supplied_output=ABC.upper()),
            lambda c: c["data"]["backups"][0].update(key_id="unlisted"),
            lambda c: c["data"]["backups"][0].update(ciphertext_present=1),
            lambda c: c["data"]["backups"][0].update(ciphertext_present=False),
            lambda c: c["data"]["backups"][0].update(attempt="not-run"),
            lambda c: c["data"]["backups"][0].update(baseline_sha256=""),
            lambda c: c["data"]["keys"][0].update(state="lost"),
            lambda c: c["data"]["keys"][0].update(access="denied"),
            lambda c: c["data"]["samples"][1].update(id="encoded-note"),
            lambda c: c["data"]["backups"][0].update(id="encoded-note"),
            lambda c: c["data"]["keys"].append(copy.deepcopy(c["data"]["keys"][0])),
            lambda c: c.update(lab_id="another-lab"),
        ]
        for index, change in enumerate(changes):
            with self.subTest(change=index):
                case = load()
                change(case)
                with self.assertRaises(ValueError):
                    analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
