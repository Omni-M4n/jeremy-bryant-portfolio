"""Acceptance checks for the fictional model, business access, and CLI contract."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import lab


class AccessReviewTests(unittest.TestCase):
    def setUp(self):
        self.scenario, self.expected, self.starting, self.solution = lab.make_case()

    def identity_for(self, role, scenario=None):
        case = scenario or self.scenario
        return next(entry["id"] for entry in case["identities"] if entry["role"] == role)

    def test_full_matrix_agrees_with_independent_business_access_table(self):
        report, intake, archive = [entry["id"] for entry in self.scenario["resources"]]
        required = {
            ("report-reader", report, "read"),
            ("intake-operator", intake, "read"),
            ("intake-operator", intake, "write"),
            ("archive-custodian", report, "read"),
            ("archive-custodian", archive, "read"),
            ("archive-custodian", archive, "write"),
            ("archive-custodian", archive, "delete"),
        }
        roles = {entry["id"]: entry["role"] for entry in self.scenario["identities"]}
        self.assertEqual(len(self.expected["decisions"]), 27)
        self.assertEqual(sum(row["allowed"] for row in self.expected["decisions"]), 7)
        for row in self.expected["decisions"]:
            with self.subTest(row=row):
                wanted = (roles[row["identity"]], row["resource"], row["action"]) in required
                self.assertEqual(row["allowed"], wanted)
                self.assertEqual(lab.allowed(self.scenario, self.solution, row["identity"],
                                             row["resource"], row["action"]), wanted)

    def test_corrected_policy_keeps_business_access_and_removes_excess(self):
        before = lab.check_policy(self.scenario, self.starting, self.expected)
        self.assertFalse(before["passed"])
        self.assertEqual(before["allowed"], 27)
        self.assertEqual(before["excess_allowed"], 20)
        self.assertEqual(before["missing_required"], 0)
        after = lab.check_policy(self.scenario, self.solution, self.expected)
        self.assertTrue(after["passed"])
        self.assertEqual((after["allowed"], after["denied"]), (7, 20))
        review = lab.review_policies(self.scenario, self.starting, self.solution, self.expected)
        self.assertTrue(review["passed"])
        self.assertEqual(review["required_retained"], 7)
        self.assertEqual(review["unwanted_removed"], 20)
        self.assertEqual(review["required_removed"], 0)

    def test_removing_required_delete_is_detected(self):
        policy = deepcopy(self.solution)
        archive = self.scenario["resources"][2]["id"]
        grant = next(grant for grant in policy["grants"] if grant["resource"] == archive)
        grant["actions"].remove("delete")
        review = lab.review_policies(self.scenario, self.starting, policy, self.expected)
        self.assertFalse(review["passed"])
        self.assertEqual(review["required_removed"], 1)
        self.assertEqual(review["missing_required"], 1)
        self.assertEqual(review["excess_allowed"], 0)
        self.assertEqual(review["mismatches"][0]["action"], "delete")

    def test_one_excess_permission_fails_even_when_all_required_access_remains(self):
        policy = deepcopy(self.solution)
        next(grant for grant in policy["grants"] if grant["role"] == "report-reader")["actions"].append("write")
        review = lab.review_policies(self.scenario, self.solution, policy, self.expected)
        self.assertFalse(review["passed"])
        self.assertEqual(review["required_retained"], 7)
        self.assertEqual(review["excess_allowed"], 1)
        self.assertEqual(review["unwanted_introduced"], 1)

    def test_empty_policy_defaults_to_deny_and_fails_business_needs(self):
        policy = {"schema_version": 1, "grants": []}
        result = lab.check_policy(self.scenario, policy, self.expected)
        self.assertEqual((result["allowed"], result["denied"]), (0, 27))
        self.assertEqual(result["missing_required"], 7)
        self.assertFalse(result["passed"])
        review = lab.review_policies(self.scenario, policy, self.solution, self.expected)
        self.assertEqual(review["required_restored"], 7)
        self.assertEqual(review["required_retained"], 0)
        self.assertTrue(review["passed"])

    def test_unassigned_roles_are_checked_against_business_rules(self):
        scenario = deepcopy(self.scenario)
        scenario["roles"].append({"id": "dormant-role", "purpose": "Future duty under review"})
        resource = scenario["resources"][0]["id"]
        policy = deepcopy(self.solution)
        policy["grants"].append({"role": "dormant-role", "resource": resource, "actions": ["read", "write", "delete"]})
        excess = lab.check_policy(scenario, policy, self.expected)
        self.assertFalse(excess["passed"])
        self.assertEqual(excess["role_excess_allowed"], 3)
        self.assertEqual(excess["excess_allowed"], 0)
        self.assertFalse(lab.review_policies(scenario, self.solution, policy, self.expected)["passed"])
        scenario["business_rules"].append({"role": "dormant-role", "resource": resource, "actions": ["read"], "reason": "Future assigned reader requires read"})
        missing = lab.check_policy(scenario, self.solution, self.expected)
        self.assertFalse(missing["passed"])
        self.assertEqual(missing["role_missing_required"], 1)
        policy["grants"][-1]["actions"] = ["read"]
        self.assertTrue(lab.check_policy(scenario, policy, self.expected)["passed"])

    def test_unfamiliar_case_has_independent_read_write_delete_actions(self):
        scenario, expected, starting, solution = lab.make_case("unfamiliar", 71)
        report, intake, archive, quarantine = [entry["id"] for entry in scenario["resources"]]
        submitter = self.identity_for("submitter", scenario)
        expiry = self.identity_for("expiry-operator", scenario)
        manager = self.identity_for("quarantine-manager", scenario)
        reviewer = self.identity_for("case-reviewer", scenario)
        self.assertTrue(lab.allowed(scenario, solution, submitter, intake, "write"))
        self.assertFalse(lab.allowed(scenario, solution, submitter, intake, "read"))
        self.assertFalse(lab.allowed(scenario, solution, submitter, intake, "delete"))
        self.assertTrue(lab.allowed(scenario, solution, expiry, archive, "read"))
        self.assertTrue(lab.allowed(scenario, solution, expiry, archive, "delete"))
        self.assertFalse(lab.allowed(scenario, solution, expiry, archive, "write"))
        for action in lab.ACTIONS:
            self.assertTrue(lab.allowed(scenario, solution, manager, quarantine, action))
            self.assertFalse(lab.allowed(scenario, solution, manager, report, action))
        self.assertTrue(lab.allowed(scenario, solution, reviewer, report, "read"))
        self.assertTrue(lab.allowed(scenario, solution, reviewer, intake, "read"))
        self.assertFalse(lab.allowed(scenario, solution, reviewer, report, "write"))
        report = lab.review_policies(scenario, starting, solution, expected)
        self.assertEqual((report["total_decisions"], report["required_retained"], report["unwanted_removed"]),
                         (48, 8, 40))

    def test_shared_role_grants_apply_to_both_identities(self):
        scenario = deepcopy(self.scenario)
        scenario["identities"].append({"id": "second-reader", "role": "report-reader"})
        report_store = scenario["resources"][0]["id"]
        self.assertTrue(lab.allowed(scenario, self.solution, "second-reader", report_store, "read"))
        self.assertFalse(lab.allowed(scenario, self.solution, "second-reader", report_store, "write"))

    def test_unknown_query_values_are_input_errors_not_valid_denials(self):
        identity = self.scenario["identities"][0]["id"]
        resource = self.scenario["resources"][0]["id"]
        for query in (("unknown-user", resource, "read"), (identity, "unknown-store", "read"),
                      (identity, resource, "READ"), (identity, resource, "*"),
                      (identity, resource, []), ([], resource, "read")):
            with self.subTest(query=query), self.assertRaises(lab.InputError):
                lab.allowed(self.scenario, self.solution, *query)

    def test_malformed_policies_are_rejected(self):
        policies = [[], {}, {"schema_version": True, "grants": []},
                    {"schema_version": 1, "grants": None}]
        for field, value in (("role", "unknown-role"), ("resource", "unknown-store"),
                             ("role", []), ("actions", []), ("actions", ["read", "read"]),
                             ("actions", ["*"]), ("actions", ["Read"]), ("actions", [["read"]])):
            policy = deepcopy(self.solution)
            policy["grants"][0][field] = value
            policies.append(policy)
        duplicate = deepcopy(self.solution)
        duplicate["grants"].append(deepcopy(duplicate["grants"][0]))
        policies.append(duplicate)
        explicit_deny = deepcopy(self.solution)
        explicit_deny["grants"][0]["effect"] = "deny"
        policies.append(explicit_deny)
        for policy in policies:
            with self.subTest(policy=policy), self.assertRaises(lab.InputError):
                lab.check_policy(self.scenario, policy, self.expected)

    def test_malformed_scenarios_are_rejected(self):
        cases = []
        for collection in ("roles", "resources", "identities", "business_rules"):
            scenario = deepcopy(self.scenario)
            scenario[collection].append(deepcopy(scenario[collection][0]))
            cases.append(scenario)
        for field, value in (("seed", True), ("seed", -1), ("variant", []), ("roles", [])):
            scenario = deepcopy(self.scenario)
            scenario[field] = value
            cases.append(scenario)
        unknown = deepcopy(self.scenario)
        unknown["identities"][0]["role"] = "absent-role"
        cases.append(unknown)
        for scenario in cases:
            with self.subTest(scenario=scenario), self.assertRaises(lab.InputError):
                lab.validate_scenario(scenario)

    def test_expected_matrix_must_be_complete_unique_and_match_business_rules(self):
        matrices = []
        missing = deepcopy(self.expected)
        missing["decisions"].pop()
        matrices.append(missing)
        duplicate = deepcopy(self.expected)
        duplicate["decisions"][-1] = deepcopy(duplicate["decisions"][0])
        matrices.append(duplicate)
        for field, value in (("allowed", "true"), ("identity", "absent-person"),
                             ("action", "*"), ("resource", [])):
            expected = deepcopy(self.expected)
            expected["decisions"][0][field] = value
            matrices.append(expected)
        contradiction = deepcopy(self.expected)
        contradiction["decisions"][0]["allowed"] = not contradiction["decisions"][0]["allowed"]
        matrices.append(contradiction)
        for expected in matrices:
            with self.subTest(expected=expected), self.assertRaises(lab.InputError):
                lab.check_policy(self.scenario, self.solution, expected)


class FileAndCliTests(unittest.TestCase):
    def setUp(self):
        test_root = lab.ROOT / "run-tests"
        test_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="access-review-", dir=test_root)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(lab.ROOT / "lab.py"), *map(str, args)],
                              cwd=lab.ROOT, text=True, capture_output=True, check=False)

    def test_generator_is_reproducible_and_seeded_names_change(self):
        first, second, third = (self.path / name for name in ("first", "second", "third"))
        lab.generate(first, "guided", 17)
        lab.generate(second, "guided", 17)
        lab.generate(third, "guided", 29)
        for name in lab.FILES:
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
        self.assertNotEqual((first / "scenario.json").read_bytes(), (third / "scenario.json").read_bytes())
        for seed in (0, 17, 29, 71, 2**32 - 1):
            for variant in ("guided", "hints", "unfamiliar"):
                scenario, expected, starting, solution = lab.make_case(variant, seed)
                self.assertTrue(lab.review_policies(scenario, starting, solution, expected)["passed"])

    def test_shipped_fixture_matches_generator_recipe(self):
        generated = self.path / "fixture-copy"
        lab.generate(generated, "guided", 17)
        for name in lab.FILES:
            self.assertEqual((generated / name).read_bytes(),
                             (lab.ROOT / "fixtures" / "worked-example" / name).read_bytes())

    def test_existing_practice_work_is_not_overwritten(self):
        run = self.path / "protected"
        lab.generate(run, "guided", 17)
        practice = run / "practice-policy.json"
        practice.write_text("personal practice work", encoding="utf-8")
        before = {path.name: path.read_bytes() for path in run.iterdir()}
        with self.assertRaises(lab.InputError):
            lab.generate(run, "unfamiliar", 71)
        self.assertEqual(before, {path.name: path.read_bytes() for path in run.iterdir()})

    def test_cli_generation_check_and_review_exit_contract(self):
        run = self.path / "cli"
        result = self.cli("generate", "--run", run, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["expected_allowed"], 7)
        overbroad = self.cli("check", "--run", run, "--json")
        self.assertEqual(overbroad.returncode, 1, overbroad.stderr)
        self.assertEqual(json.loads(overbroad.stdout)["excess_allowed"], 20)
        corrected = self.cli("check", "--run", run, "--policy", run / "solution-policy.json", "--json")
        self.assertEqual(corrected.returncode, 0, corrected.stderr)
        review = self.cli("review", "--run", run, "--after", run / "solution-policy.json", "--json")
        self.assertEqual(review.returncode, 0, review.stderr)
        self.assertEqual(json.loads(review.stdout)["required_retained"], 7)
        self.assertEqual(json.loads(review.stdout)["unwanted_removed"], 20)
        invalid = self.cli("generate", "--run", self.path / "bad-seed", "--seed", -1, "--json")
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("error", json.loads(invalid.stderr))

    def test_cli_malformed_input_exits_two_without_traceback(self):
        run = self.path / "malformed"
        lab.generate(run, "guided", 17)
        for content in ('{"schema_version":1,"grants":',
                        '{"schema_version":1,"schema_version":1,"grants":[]}',
                        '{"schema_version":NaN,"grants":[]}',
                        '{"schema_version":1,"grants":[{"role":[]}]}',
                        '[]', '\ufffd'):
            with self.subTest(content=content):
                (run / "practice-policy.json").write_text(content, encoding="utf-8")
                result = self.cli("check", "--run", run, "--json")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("error", json.loads(result.stderr))
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
