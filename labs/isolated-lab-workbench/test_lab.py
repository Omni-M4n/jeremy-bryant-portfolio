import copy
import hashlib
import json
import unittest
from lab import ROOT, analyse


class WorkbenchTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((ROOT / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_guided_decisions(self):
        result = analyse(self.case())["decisions"]
        self.assertEqual(result["network"], "disconnected-boundary-supported")
        self.assertEqual(result["rollback"], "dummy-file-rollback-demonstrated")
        self.assertEqual(result["review"], "supplied-evidence-complete")

    def test_literal_marker_hashes_match_recorded_states(self):
        baseline = hashlib.sha256(b"BASELINE\n").hexdigest()
        edited = hashlib.sha256(b"CHANGED\n").hexdigest()
        expected = {"guided": (baseline, edited, baseline),
                    "changed": (baseline, edited, edited),
                    "challenge": (baseline, baseline, baseline)}
        for name, values in expected.items():
            with self.subTest(case=name):
                restore = self.case(name)["data"]["restore"]
                self.assertEqual(tuple(restore[key] for key in
                                       ("baseline_sha256", "changed_sha256", "restored_sha256")), values)

    def test_changed_has_independent_failures(self):
        result = analyse(self.case("changed"))["decisions"]
        self.assertEqual(result["network"], "network-boundary-violated")
        self.assertEqual(result["host-paths"], "host-transfer-path-present")
        self.assertEqual(result["rollback"], "restored-bytes-mismatch")

    def test_missing_adapter_is_unknown(self):
        case = self.case()
        case["data"]["adapters"].pop()
        self.assertEqual(analyse(case)["decisions"]["network"], "adapter-inventory-incomplete")

    def test_known_connected_adapter_overrides_missing(self):
        case = self.case("changed")
        case["data"]["adapters"].pop()
        self.assertEqual(analyse(case)["decisions"]["network"], "network-boundary-violated")

    def test_not_attached_allowed(self):
        case = self.case()
        case["data"]["adapters"][0]["mode"] = "not-attached"
        self.assertEqual(analyse(case)["decisions"]["network"], "disconnected-boundary-supported")

    def test_host_only_not_same_boundary(self):
        case = self.case()
        case["data"]["adapters"][7]["mode"] = "host-only"
        self.assertEqual(analyse(case)["decisions"]["network"], "network-boundary-violated")

    def test_default_route_conflicts(self):
        case = self.case()
        case["data"]["guest"]["default_routes"] = 1
        self.assertEqual(analyse(case)["decisions"]["network"], "guest-evidence-conflicts")

    def test_non_loopback_address_conflicts(self):
        case = self.case()
        case["data"]["guest"]["non_loopback_addresses"] = ["2001:db8::8"]
        self.assertEqual(analyse(case)["decisions"]["network"], "guest-evidence-conflicts")

    def test_positive_and_negative_connection_required(self):
        case = self.case()
        case["data"]["loopback"]["refused_after_stop"] = False
        self.assertEqual(analyse(case)["decisions"]["connectivity"], "loopback-stop-check-failed")
        case["data"]["loopback"]["body"] = "WRONG\n"
        self.assertEqual(analyse(case)["decisions"]["connectivity"], "loopback-positive-failed")

    def test_snapshot_identity_before_matching_bytes(self):
        case = self.case()
        case["data"]["restore"]["snapshot_vm"] = "another-vm"
        self.assertEqual(analyse(case)["decisions"]["rollback"], "snapshot-identity-mismatch")

    def test_no_change_does_not_prove_rollback(self):
        case = self.case()
        restore = case["data"]["restore"]
        restore["changed_sha256"] = restore["baseline_sha256"]
        self.assertEqual(analyse(case)["decisions"]["rollback"], "change-not-demonstrated")

    def test_write_through_disk_excluded(self):
        case = self.case()
        case["data"]["restore"]["disk_mode"] = "write-through"
        self.assertEqual(analyse(case)["decisions"]["rollback"], "disk-outside-snapshot-model")

    def test_missing_restore_evidence(self):
        case = self.case()
        case["data"]["restore"]["restored_sha256"] = None
        self.assertEqual(analyse(case)["decisions"]["rollback"], "restore-evidence-incomplete")

    def test_bad_slot_mode_hash_and_type_rejected(self):
        for mutation in (lambda d: d["adapters"].append(dict(d["adapters"][0])),
                         lambda d: d["adapters"][0].update(slot=True),
                         lambda d: d["adapters"][0].update(mode="magic"),
                         lambda d: d["restore"].update(baseline_sha256="abc"),
                         lambda d: d.update(disposable=1),
                         lambda d: d["guest"].update(non_loopback_addresses=["127.0.0.1"])):
            with self.subTest(mutation=mutation):
                case = self.case()
                mutation(case["data"])
                with self.assertRaises(ValueError):
                    analyse(case)

    def test_no_input_mutation(self):
        case = self.case()
        before = copy.deepcopy(case)
        analyse(case)
        self.assertEqual(case, before)

    def test_unhashable_invalid_enums_rejected_cleanly(self):
        for group, field in (("loopback", "bind_address"), ("restore", "disk_mode")):
            case = self.case()
            case["data"][group][field] = []
            with self.assertRaises(ValueError):
                analyse(case)


if __name__ == "__main__":
    unittest.main()
