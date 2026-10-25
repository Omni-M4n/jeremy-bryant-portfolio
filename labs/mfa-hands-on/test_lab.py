"""Independent boundary and invalid-input tests for mfa-hands-on."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import lab
import service


class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((Path(__file__).parent / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_analysis_preserves_input(self):
        c = self.case()
        before = copy.deepcopy(c)
        lab.analyse(c)
        self.assertEqual(c, before)

    def test_rfc6238_known_vector(self):
        import base64
        import service
        seed = base64.b32encode(b"12345678901234567890").decode()
        self.assertEqual(service.totp(seed, 59, 8), "94287082")
        self.assertEqual(service.totp(seed, 1111111109, 8), "07081804")

    def test_full_lifecycle_and_used_code(self):
        import service
        state = service.fresh()
        saved = copy.deepcopy(state)
        proof = service.totp(state["secret"], 60)
        state, event = service.transition(state, "confirm", 60, "training-pass", proof)
        self.assertEqual(event["result"], "accept")
        self.assertFalse(saved["enrolled"])
        state, event = service.transition(state, "challenge", 60, "training-pass", proof)
        self.assertEqual(event["result"], "reject")
        proof = service.totp(state["secret"], 90)
        state, event = service.transition(state, "challenge", 90, "wrong", proof)
        self.assertEqual(event["result"], "reject")
        state, event = service.transition(state, "challenge", 90, "training-pass", proof)
        self.assertEqual(event["result"], "accept")
        self.assertEqual(state["sessions"], 1)
        old_secret, recovery = state["secret"], state["recovery"]
        state, event = service.transition(state, "recover", 120, "training-pass", recovery)
        self.assertEqual(event["result"], "accept")
        self.assertEqual(state["sessions"], 0)
        self.assertFalse(state["enrolled"])
        self.assertNotEqual(state["secret"], old_secret)
        proof = service.totp(state["secret"], 150)
        state, event = service.transition(state, "confirm", 150, "training-pass", proof)
        self.assertEqual(event["result"], "accept")
        state, event = service.transition(state, "recover", 180, "training-pass", recovery)
        self.assertEqual(event["result"], "reject")

    def test_code_expires_at_step_edge(self):
        import service
        state = service.fresh()
        state["secret"] = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        proof = service.totp(state["secret"], 59)
        state, event = service.transition(state, "confirm", 60, "training-pass", proof)
        self.assertEqual(event["result"], "reject")

    def test_invalid_clock_and_unknown_fields(self):
        import service
        state = service.fresh()
        state["last_at"] = 60
        for at in [59, True, -1]:
            with self.assertRaises(ValueError):
                service.transition(state, "confirm", at, "training-pass", "123456")
        state["extra"] = 1
        with self.assertRaises(ValueError):
            service.validate(state)

    def test_bad_flags_and_missing_record(self):
        c = self.case()
        c["data"]["records"][0]["password_ok"] = "yes"
        with self.assertRaises(ValueError):
            lab.analyse(c)
        c["data"]["records"] = []
        with self.assertRaises(ValueError):
            lab.analyse(c)

    def test_contradictory_state_and_unmatched_unicode_proof(self):
        import service
        state = service.fresh()
        state["sessions"] = 1
        with self.assertRaises(ValueError):
            service.validate(state)
        state = service.fresh()
        state, event = service.transition(state, "confirm", 60, "training-pass", "\u00e9")
        self.assertEqual(event["result"], "reject")

    def test_observed_accept_needs_all_requirements(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"], {"q1": "investigate-mismatch", "q2": "investigate-mismatch", "q3": "matches-model"})


class StateFileTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mfa-test-", dir=Path(__file__).parent)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.folder = self.root / "run" / "account-01"
        self.path = self.folder / "state.json"
        self.outside = self.root / "outside-dummy-state.json"

    def cli(self, command, *options):
        output, errors = io.StringIO(), io.StringIO()
        args = ["service.py", command, "--folder", "run/account-01", *options]
        with patch.object(service, "ROOT", self.root), patch.object(sys, "argv", args), redirect_stdout(output), redirect_stderr(errors):
            code = service.cli()
        return code, output.getvalue(), errors.getvalue()

    def write_state(self, state):
        self.folder.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(service.encoded(state))

    def make_alias(self):
        os.link(self.path, self.outside)
        self.assertEqual(self.path.stat().st_nlink, 2)

    def test_hardlinked_actions_leave_both_names_unchanged(self):
        for operation in ("confirm", "challenge", "recover"):
            for valid_proof in (False, True):
                with self.subTest(operation=operation, valid_proof=valid_proof):
                    state = service.fresh()
                    if operation != "confirm":
                        state, _ = service.transition(state, "confirm", 30, service.PASSWORD, service.totp(state["secret"], 30))
                    proof = state["recovery"] if operation == "recover" else service.totp(state["secret"], 60)
                    password = service.PASSWORD if valid_proof else "wrong"
                    proof = proof if valid_proof else "bad-proof"
                    self.write_state(state)
                    self.make_alias()
                    before = self.path.read_bytes()
                    try:
                        code, output, errors = self.cli(operation, "--at", "60", "--password", password, "--proof", proof)
                        self.assertEqual(code, 2)
                        self.assertEqual(output, "")
                        self.assertIn("hard-linked state", errors)
                        self.assertEqual(self.path.read_bytes(), before)
                        self.assertEqual(self.outside.read_bytes(), before)
                    finally:
                        self.outside.unlink()

    def test_hardlinked_state_refused_before_read_or_cleanup(self):
        self.write_state(service.fresh())
        self.make_alias()
        before = self.path.read_bytes()
        for command in ("device", "evidence", "clean"):
            with self.subTest(command=command), patch.object(service, "read_json") as reader:
                code, _, errors = self.cli(command)
                self.assertEqual(code, 2)
                self.assertIn("hard-linked state", errors)
                reader.assert_not_called()
                self.assertEqual(self.path.read_bytes(), before)
                self.assertEqual(self.outside.read_bytes(), before)

    def test_link_added_after_read_is_refused_before_write(self):
        state = service.fresh()
        self.write_state(state)
        before = self.path.read_bytes()
        original_transition = service.transition

        def add_alias(*args):
            result = original_transition(*args)
            self.make_alias()
            return result

        with patch.object(service, "transition", side_effect=add_alias):
            code, _, errors = self.cli("confirm", "--at", "60", "--password", "wrong", "--proof", "bad-proof")
        self.assertEqual(code, 2)
        self.assertIn("hard-linked state", errors)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.outside.read_bytes(), before)

    def test_single_link_cli_lifecycle_and_cleanup(self):
        code, setup, _ = self.cli("new")
        self.assertEqual(code, 0)
        recovery = json.loads(setup)["dummy_recovery_code"]
        state = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(self.path.stat().st_nlink, 1)
        code, proof, _ = self.cli("device", "--at", "60")
        self.assertEqual(code, 0)
        self.assertEqual(proof.strip(), service.totp(state["secret"], 60))
        expected = [("confirm", 60, service.PASSWORD, proof.strip(), 0),
                    ("challenge", 60, service.PASSWORD, proof.strip(), 1),
                    ("challenge", 90, "wrong", service.totp(state["secret"], 90), 1),
                    ("challenge", 90, service.PASSWORD, service.totp(state["secret"], 90), 0),
                    ("recover", 120, service.PASSWORD, recovery, 0)]
        for operation, at, password, proof, expected_code in expected:
            code, _, _ = self.cli(operation, "--at", str(at), "--password", password, "--proof", proof)
            self.assertEqual(code, expected_code)
        state = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertFalse(state["enrolled"])
        self.assertEqual(state["sessions"], 0)
        code, proof, _ = self.cli("device", "--at", "150")
        self.assertEqual(code, 0)
        self.assertEqual(self.cli("confirm", "--at", "150", "--password", service.PASSWORD, "--proof", proof.strip())[0], 0)
        self.assertEqual(self.cli("recover", "--at", "180", "--password", service.PASSWORD, "--proof", recovery)[0], 1)
        code, evidence, _ = self.cli("evidence")
        self.assertEqual(code, 0)
        self.assertEqual([event["result"] for event in json.loads(evidence)["events"]], ["accept", "reject", "reject", "accept", "accept", "accept", "reject"])
        self.assertEqual(self.cli("clean")[0], 0)
        self.assertFalse(self.folder.exists())


if __name__ == "__main__":
    unittest.main()
