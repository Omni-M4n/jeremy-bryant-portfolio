"""Independent expectations for responsibility allocation and evidence boundaries."""
import copy
import json
import unittest
from lab import analyse, ROOT


def load(name="guided"):
    return json.loads((ROOT / "fixtures" / f"{name}.json").read_text(encoding="utf-8"))


class DomainTests(unittest.TestCase):
    def test_explicit_references(self):
        for name in ("guided", "changed", "challenge"):
            with self.subTest(case=name):
                expected = json.loads((ROOT / "reference" / f"{name}.json").read_text(encoding="utf-8"))
                self.assertEqual(analyse(load(name)), expected)

    def test_os_owner_changes_by_model(self):
        for model, owner in (("IaaS", "customer"), ("PaaS", "provider"), ("SaaS", "provider")):
            case = load()
            case["data"]["services"][0]["model"] = model
            self.assertEqual(analyse(case)["decisions"]["guest"].split(":")[0], owner)

    def test_deployed_code_and_saas_binary_have_different_owners(self):
        for model, owner in (("IaaS", "customer"), ("PaaS", "customer"), ("SaaS", "provider")):
            case = load("changed")
            case["data"]["services"][0]["model"] = model
            self.assertEqual(analyse(case)["decisions"]["app-code"].split(":")[0], owner)

    def test_tenant_access_stays_customer_for_every_model(self):
        for model in ("IaaS", "PaaS", "SaaS"):
            case = load()
            case["data"]["services"][0]["model"] = model
            self.assertEqual(analyse(case)["decisions"]["access"], "customer:owner-matches:evidence-missing")

    def test_passing_evidence_does_not_fix_wrong_assignment(self):
        case = load()
        case["data"]["controls"][1]["evidence"] = "pass"
        self.assertEqual(analyse(case)["decisions"]["guest"], "customer:correct-owner:evidence-pass")

    def test_missing_evidence_is_not_failed_control(self):
        self.assertEqual(analyse(load())["decisions"]["access"], "customer:owner-matches:evidence-missing")

    def test_backup_contract_is_not_inferred_from_model_or_claim(self):
        case = load("challenge")
        case["data"]["controls"][3]["evidence"] = "pass"
        self.assertEqual(analyse(case)["decisions"]["copy"], "unspecified:clarify-agreement:evidence-pass")
        case["data"]["services"][0]["backup_copy_owner"] = "customer"
        self.assertEqual(analyse(case)["decisions"]["copy"], "customer:correct-owner:evidence-pass")

    def test_shared_is_not_a_complete_atomic_assignment(self):
        self.assertEqual(analyse(load("challenge"))["decisions"]["app-code"], "provider:correct-owner:evidence-pass")

    def test_input_preserved(self):
        case = load()
        before = copy.deepcopy(case)
        analyse(case)
        self.assertEqual(case, before)

    def test_each_service_uses_its_own_agreement(self):
        case = load()
        service = copy.deepcopy(case["data"]["services"][0])
        service.update(id="managed-vm", backup_copy_owner="provider")
        case["data"]["services"].append(service)
        control = copy.deepcopy(case["data"]["controls"][3])
        control.update(id="managed-copy", service_id="managed-vm", claimed_owner="provider")
        case["data"]["controls"].append(control)
        result = analyse(case)["decisions"]
        self.assertEqual(result["copy"], "customer:owner-matches:evidence-missing")
        self.assertEqual(result["managed-copy"], "provider:owner-matches:evidence-missing")

    def test_invalid_input_is_rejected(self):
        changes = [
            lambda c: c["data"].update(extra=True),
            lambda c: c["data"]["services"][0].update(model="cloud"),
            lambda c: c["data"]["services"][0].update(backup_copy_owner="shared"),
            lambda c: c["data"]["controls"][0].update(service_id="absent"),
            lambda c: c["data"]["controls"][0].update(task=[]),
            lambda c: c["data"]["controls"][0].update(evidence=True),
            lambda c: c["data"]["controls"][0].update(evidence_ref=""),
            lambda c: c["data"]["controls"][1].update(id="host"),
            lambda c: c["data"]["controls"][1].update(task="physical-host-patching"),
            lambda c: c["data"].update(controls=[]),
            lambda c: c.update(synthetic=False),
        ]
        for index, change in enumerate(changes):
            with self.subTest(change=index):
                case = load()
                change(case)
                with self.assertRaises(ValueError):
                    analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
