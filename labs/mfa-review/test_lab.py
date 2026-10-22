"""Boundary checks for the fictional domain model; no network required."""
import copy
import json
import unittest
from pathlib import Path
from lab import analyse, ROOT


def load(name="guided"):
    return json.loads((ROOT / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))


class DomainTests(unittest.TestCase):
    def test_all_reference_outputs_are_explicit_and_match(self):
        for name in ("guided", "changed", "challenge"):
            with self.subTest(case=name):
                expected = json.loads((ROOT / "reference" / (name + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(analyse(load(name)), expected)

    def test_analysis_preserves_supplied_evidence(self):
        case = load()
        before = copy.deepcopy(case)
        analyse(case)
        self.assertEqual(case, before)

    def test_rejects_unknown_data_fields(self):
        case = load()
        case["data"]["unexpected"] = "do not ignore"
        with self.assertRaises(ValueError):
            analyse(case)

    def test_rejects_wrong_envelope(self):
        case = load()
        case["synthetic"] = False
        with self.assertRaises(ValueError):
            analyse(case)

    def test_enrolment_does_not_imply_enforcement(self):
        self.assertEqual(analyse(load())["decisions"]["helpdesk-user"], "enforce-mfa;repair-recovery")

    def test_service_account_is_not_a_blanket_exemption(self):
        self.assertEqual(analyse(load())["decisions"]["nightly-export"], "disable-interactive-login;assign-owner;replace-static-workload-credential;monitor-workload-use")

    def test_short_lived_federation_still_rejects_password(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["mixed-workload"], "replace-static-workload-credential")

    def test_exception_expiry_is_inclusive(self):
        case = load()
        self.assertEqual(analyse(case)["decisions"]["emergency-owner"], "exception-current")
        case["data"]["as_of"] = "2026-10-24"
        self.assertEqual(analyse(case)["decisions"]["emergency-owner"], "enrol-mfa;use-phishing-resistant-mfa")

    def test_emergency_test_age_boundary(self):
        case = load()
        row = case["data"]["accounts"][3]
        row["test_age_days"] = 90
        self.assertEqual(analyse(case)["decisions"]["emergency-owner"], "exception-current")
        row["test_age_days"] = 91
        self.assertEqual(analyse(case)["decisions"]["emergency-owner"], "test-emergency-access")

    def test_exception_does_not_waive_storage_or_monitoring(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["unmonitored-emergency"], "monitor-emergency-use;secure-emergency-material")

    def test_privileged_human_needs_key_in_this_policy(self):
        self.assertEqual(analyse(load())["decisions"]["platform-admin"], "use-phishing-resistant-mfa")

    def test_boolean_age_is_rejected(self):
        case = load()
        case["data"]["accounts"][3]["test_age_days"] = True
        with self.assertRaises(ValueError):
            analyse(case)

    def test_wrong_type_methods_and_duplicate_methods_rejected(self):
        for methods in (["federated-workload"], ["totp", "totp"], [{"type":"totp"}]):
            with self.subTest(methods=methods):
                case = load()
                case["data"]["accounts"][0]["methods"] = methods
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_human_cannot_claim_emergency_exception(self):
        case = load()
        case["data"]["accounts"][0]["exception_until"] = "2026-12-31"
        with self.assertRaises(ValueError):
            analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
