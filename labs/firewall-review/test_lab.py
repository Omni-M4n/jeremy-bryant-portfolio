"""Meaningful model, malformed-input, reproduction and CLI checks."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import lab


class FirewallLabTests(unittest.TestCase):
    def setUp(self):
        self.scenario, self.starting, self.solution = lab.make_case()

    def packet(self, probe_id="portal-client"):
        probe = next(p for p in self.scenario["probes"] if p["id"] == probe_id)
        return {field: probe[field] for field in ("id", *lab.FIELDS)}

    def decide(self, policy, packet):
        return lab.evaluate(policy, {"schema_version": 1, "packets": [packet]})[0]

    def cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(lab.ROOT / "lab.py"), *map(str, args)],
                              capture_output=True, text=True, cwd=cwd, timeout=20)

    def test_case_families_require_different_corrections(self):
        expected = {
            "shadowed-deny": (set(), {"restricted-portal"}),
            "narrow-service": (set(), {"management-client", "management-wrong-port",
                                        "portal-wrong-destination", "portal-wrong-port", "telemetry-tcp"}),
            "missing-access": ({"archive-backup"}, set()),
            "protocol-mix": ({"telemetry-udp", "telemetry-new-source-port"}, {"telemetry-tcp"}),
        }
        for case in lab.CASES:
            with self.subTest(case=case):
                scenario, starting, solution = lab.make_case(case)
                failed = lab.check(starting, scenario)
                self.assertFalse(failed["passed"])
                self.assertEqual((set(failed["missing_access"]), set(failed["excess_access"])), expected[case])
                fixed = lab.check(solution, scenario)
                self.assertTrue(fixed["passed"])
                self.assertEqual(fixed["legitimate_preserved"], 9 if case == "missing-access" else 8)

    def test_deny_all_fails_by_blocking_legitimate_traffic(self):
        result = lab.check({"schema_version": 1, "rules": []}, self.scenario)
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["missing_access"]), 8)
        self.assertEqual(result["excess_access"], [])

    def test_first_match_not_deny_override_or_most_specific(self):
        packet = self.packet("restricted-portal")
        before = self.decide(self.starting, packet)
        after = self.decide(self.solution, packet)
        self.assertEqual((before["action"], before["rule_id"], before["position"]), ("allow", "portal", 1))
        self.assertEqual((after["action"], after["rule_id"], after["position"]), ("deny", "restricted-tcp", 1))

    def test_protocol_and_direction_are_separate(self):
        for probe_id, action in (("telemetry-udp", "allow"), ("telemetry-tcp", "deny"),
                                 ("portal-client", "allow"), ("portal-udp", "deny"),
                                 ("reverse-direction", "deny")):
            with self.subTest(probe=probe_id):
                self.assertEqual(self.decide(self.solution, self.packet(probe_id))["action"], action)

    def test_source_and_destination_ports_not_interchangeable(self):
        packet = self.packet("telemetry-source-port-trap")
        self.assertEqual(self.decide(self.solution, packet)["action"], "deny")
        custom = {"schema_version": 1, "rules": [lab.rule("one-tuple", "allow", "udp", packet["source"],
                   packet["destination"], 5515, source_port=5514)]}
        self.assertEqual(self.decide(custom, packet)["action"], "allow")
        packet["source_port"] = 5515
        self.assertEqual(self.decide(custom, packet)["action"], "deny")

    def test_cidr_edges_exact_host_and_default_deny(self):
        packet = self.packet()
        policy = {"schema_version": 1, "rules": [lab.rule("subnet", "allow", "tcp", "192.0.2.0/25",
                   packet["destination"], 443)]}
        for suffix, expected in ((0, "allow"), (127, "allow"), (128, "deny"), (255, "deny")):
            packet["source"] = f"192.0.2.{suffix}"
            self.assertEqual(self.decide(policy, packet)["action"], expected)
        policy["rules"][0]["source"] = "192.0.2.128/32"
        packet["source"] = "192.0.2.128"
        self.assertEqual(self.decide(policy, packet)["action"], "allow")
        policy["rules"][0]["source"] = "192.0.2.128"
        self.assertEqual(self.decide(policy, packet)["action"], "allow")
        packet["destination"] = "203.0.113.19"
        result = self.decide(policy, packet)
        self.assertEqual((result["action"], result["rule_id"], result["position"]), ("deny", None, None))

    def test_strict_policy_validation(self):
        changes = [("protocol", "TCP"), ("protocol", "any"), ("protocol", []),
                   ("action", "accept"), ("action", True), ("id", "Bad ID"),
                   ("source", "192.0.2.1/24"), ("source", "192.0.2.0/255.255.255.0"),
                   ("source", "192.0.2.1/033"), ("source", "192.000.2.1"),
                   ("source", "10.0.0.0/8"), ("source", "0.0.0.0/0"),
                   ("source", "::1"), ("source", "*"), ("source", None),
                   ("destination_port", 0), ("destination_port", 65536),
                   ("destination_port", True), ("destination_port", 443.0),
                   ("destination_port", "443"), ("source_port", [1, 10])]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                policy = copy.deepcopy(self.solution)
                policy["rules"][-1][field] = value
                with self.assertRaises(lab.InputError):
                    lab.validate_policy(policy)
        for malformed in ([], {"schema_version": True, "rules": []},
                          {"schema_version": 1, "rules": [], "default": "allow"},
                          {"schema_version": 1, "rules": self.solution["rules"] * 2},
                          {"schema_version": 1, "rules": [None]},
                          {"schema_version": 1, "rules": [{}] * 65}):
            with self.subTest(value=malformed):
                with self.assertRaises(lab.InputError):
                    lab.validate_policy(malformed)

    def test_invalid_unreachable_rule_is_error(self):
        policy = copy.deepcopy(self.starting)
        policy["rules"][-1]["protocol"] = "all"
        with self.assertRaises(lab.InputError):
            self.decide(policy, self.packet())

    def test_packet_and_scenario_validation(self):
        for field, value in (("source", "192.0.2.0/24"), ("source_port", "*"),
                             ("destination_port", False), ("destination", "8.8.8.8")):
            packet = self.packet()
            packet[field] = value
            with self.subTest(field=field), self.assertRaises(lab.InputError):
                self.decide(self.solution, packet)
        packet = self.packet()
        with self.assertRaises(lab.InputError):
            lab.validate_packets({"schema_version": 1, "packets": [packet, packet]})
        for field, value in (("seed", True), ("seed", -1), ("case", []), ("requirements", [])):
            scenario = copy.deepcopy(self.scenario)
            scenario[field] = value
            with self.subTest(field=field), self.assertRaises(lab.InputError):
                lab.validate_scenario(scenario)
        scenario = copy.deepcopy(self.scenario)
        scenario["probes"][0]["expected"] = True
        with self.assertRaises(lab.InputError):
            lab.validate_scenario(scenario)

    def test_json_rejects_duplicates_constants_encoding_and_size(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for value in (b'{"rules":[],"rules":[]}', b'{"v":NaN}', b'{"v":Infinity}',
                          b'not JSON', b'\xff', b' ' * (lab.MAX_BYTES + 1)):
                path.write_bytes(value)
                with self.subTest(value=value[:30]), self.assertRaises(lab.InputError):
                    lab.read_json(path)
            # Python 3.11+ limits integer decoding; either supported runtime
            # behaviour must still end as a controlled schema/input error.
            path.write_bytes(b'{"schema_version":' + b'9' * 5000 + b',"rules":[]}')
            with self.assertRaises(lab.InputError):
                lab.validate_policy(lab.read_json(path))

    def test_generation_preserves_notes_and_existing_fixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            notes = path / "my-notes.txt"
            notes.write_bytes(b"preserve me\n")
            with self.assertRaises(lab.InputError):
                lab.write_case(path, "shadowed-deny", 17)
            self.assertEqual(notes.read_bytes(), b"preserve me\n")
            self.assertEqual(list(path.iterdir()), [notes])
            target = path / "fresh"
            lab.write_case(target, "shadowed-deny", 17)
            before = {p.name: p.read_bytes() for p in target.iterdir()}
            with self.assertRaises(lab.InputError):
                lab.write_case(target, "shadowed-deny", 18)
            self.assertEqual(before, {p.name: p.read_bytes() for p in target.iterdir()})

    def test_fixture_bytes_reproduce_and_are_lf(self):
        for case in lab.CASES:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "case"
                lab.write_case(path, case, 17)
                expected = lab.ROOT / "fixtures" / case
                self.assertEqual(sorted(p.name for p in path.iterdir()), sorted(p.name for p in expected.iterdir()))
                for generated in path.iterdir():
                    self.assertNotIn(b"\r", generated.read_bytes())
                    self.assertEqual(generated.read_bytes(), (expected / generated.name).read_bytes())
        self.assertNotEqual(lab.make_case(seed=17), lab.make_case(seed=18))
        for case in lab.CASES:
            for seed in (0, 29, 71, 2**32 - 1):
                scenario, starting, solution = lab.make_case(case, seed)
                self.assertFalse(lab.check(starting, scenario)["passed"])
                self.assertTrue(lab.check(solution, scenario)["passed"])

    def test_cli_contract_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "practice"
            result = self.cli("generate", "--run", target, "--case", "protocol-mix", "--json", cwd=directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["case"], "protocol-mix")
            self.assertEqual(self.cli("generate", "--run", target).returncode, 2)
            result = self.cli("check", "--run", target, "--json", cwd=directory)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(result.stdout)["excess_access"], ["telemetry-tcp"])
            self.assertEqual(self.cli("check", "--run", target, "--policy", target / "solution-policy.json").returncode, 0)
            result = self.cli("evaluate", "--policy", target / "solution-policy.json", "--packets", target / "packets.json", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(json.loads(result.stdout)["decisions"]), 22)
            (target / "practice-policy.json").write_bytes(b'{"schema_version":1,"rules":[{}]}')
            malformed = self.cli("check", "--run", target, "--json")
            self.assertEqual(malformed.returncode, 2)
            self.assertEqual(malformed.stdout, "")
            self.assertIn("Input error", malformed.stderr)
            self.assertEqual(self.cli("evaluate", "--policy", target / "absent", "--packets", target / "packets.json").returncode, 2)
            invalid_target = Path(directory) / "invalid-seed"
            self.assertEqual(self.cli("generate", "--run", invalid_target, "--seed", -1).returncode, 2)
            self.assertFalse(invalid_target.exists())
        protected = self.cli("generate", "--run", lab.ROOT / "fixtures" / "must-not-exist")
        self.assertEqual(protected.returncode, 2)
        self.assertFalse((lab.ROOT / "fixtures" / "must-not-exist").exists())
        self.assertEqual(self.cli("--help").returncode, 0)

    def test_manifest_matches_shipped_bytes(self):
        result = self.cli("manifest", "--verify", "--json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(result.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
