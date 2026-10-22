"""Shared CLI safety and worksheet semantics, independent of any domain lab."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import foundation_runtime as runtime


def case(case_id="guided"):
    return {"schema_version": 1, "lab_id": "test-example", "case_id": case_id,
            "title": "Fictional fixture", "synthetic": True,
            "context": {"question": "Which record needs review?"},
            "data": {"id": "event-1"}, "artifacts": {"evidence.txt": "event-1: review\n"}}


def analyse(value):
    return {"decisions": {value["data"]["id"]: "review"},
            "observations": ["The supplied event needs review."],
            "limitations": ["No incident is established."]}


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "fixtures").mkdir()
        (self.root / "reference").mkdir()
        for name in runtime.CASE_IDS:
            (self.root / "fixtures" / f"{name}.json").write_bytes(runtime.encoded(case(name)))
            (self.root / "reference" / f"{name}.json").write_bytes(runtime.encoded(analyse(case(name))))

    def cli(self, *args):
        output = io.StringIO()
        error = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = runtime.main(self.root, "test-example", analyse, args)
        return code, output.getvalue(), error.getvalue()

    def test_prepare_preserves_inputs_and_materialises_readable_evidence(self):
        before = (self.root / "fixtures/guided.json").read_bytes()
        self.assertEqual(self.cli("prepare", "--out", "run/first")[0], 0)
        target = self.root / "run/first"
        self.assertEqual((target / "evidence.txt").read_bytes(), b"event-1: review\n")
        self.assertEqual(runtime.read_json(target / "answers.json")["decisions"], {"event-1": ""})
        self.assertEqual(before, (self.root / "fixtures/guided.json").read_bytes())

    def test_existing_attempt_and_notes_are_not_overwritten(self):
        self.cli("prepare", "--out", "run/first")
        notes = self.root / "run/first/notes.txt"
        notes.write_text("my first attempt", encoding="utf-8")
        self.assertEqual(self.cli("prepare", "--out", "run/first")[0], 2)
        self.assertEqual(notes.read_text(), "my first attempt")

    def test_output_must_be_below_run_without_traversal(self):
        for output in ("run", "fixtures/new", "run/../elsewhere", str(self.root / "absolute")):
            with self.subTest(output=output):
                self.assertEqual(self.cli("prepare", "--out", output)[0], 2)

    def test_unsafe_and_reserved_artifact_names_are_rejected(self):
        for name in ("../outside.txt", "a/b.txt", "case.json", "answers.json", "notes.txt", "con.txt", "nul.txt"):
            value = case()
            value["artifacts"] = {name: "text"}
            with self.subTest(name=name), self.assertRaises(ValueError):
                runtime.validate_case(value, "test-example")

    def test_cross_lab_and_real_data_envelopes_are_rejected(self):
        for field, value in (("lab_id", "other-lab"), ("synthetic", False), ("schema_version", True), ("case_id", "unknown")):
            candidate = case()
            candidate[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.validate_case(candidate, "test-example")

    def test_mutating_analyser_is_rejected(self):
        def mutating(value):
            value["data"]["id"] = "changed"
            return analyse(value)
        with self.assertRaisesRegex(ValueError, "modified"):
            runtime.analyse_checked(case(), "test-example", mutating)

    def test_duplicate_keys_and_nonfinite_numbers_are_rejected(self):
        file = self.root / "bad.json"
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            file.write_text(text, encoding="utf-8")
            with self.subTest(text=text), self.assertRaises(ValueError):
                runtime.read_json(file)

    def test_oversized_input_is_rejected(self):
        file = self.root / "large.json"
        file.write_bytes(b" " * (runtime.MAX_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "1 MB"):
            runtime.read_json(file)

    def test_blank_worksheet_is_incomplete(self):
        actual, code = runtime.check_answers(analyse(case()), {"decisions": {"event-1": ""}, "explanation": "", "evidence": []})
        self.assertEqual(code, 1)
        self.assertFalse(actual["decision_match"])
        self.assertEqual(actual["learner_mastery"], "not assessed")

    def test_matching_fields_still_require_written_evidence_and_human_review(self):
        answer = {"decisions": {"event-1": "review"}, "explanation": "", "evidence": []}
        self.assertEqual(runtime.check_answers(analyse(case()), answer)[1], 1)
        answer.update(explanation="The supplied event needs checking.", evidence=["event-1"])
        result, code = runtime.check_answers(analyse(case()), answer)
        self.assertEqual(code, 0)
        self.assertEqual(result["learner_mastery"], "not assessed")

    def test_extra_or_missing_decisions_cannot_pass(self):
        for decisions in ({}, {"event-1": "review", "extra": "review"}):
            result, code = runtime.check_answers(analyse(case()), {"decisions": decisions, "explanation": "note", "evidence": ["event-1"]})
            self.assertEqual(code, 1)
            self.assertTrue(result["differences"])

    def test_reference_difference_is_reported(self):
        altered = analyse(case())
        altered["decisions"]["event-1"] = "ignore"
        (self.root / "reference/changed.json").write_bytes(runtime.encoded(altered))
        code, output, _ = self.cli("verify")
        self.assertEqual(code, 1)
        self.assertEqual([r["matches_reference"] for r in json.loads(output)["cases"]], [True, False, True])

    def test_reference_case_id_mismatch_is_error(self):
        (self.root / "fixtures/changed.json").write_bytes(runtime.encoded(case("guided")))
        self.assertEqual(self.cli("verify")[0], 2)

    def test_cli_commands_and_invalid_input_exit_codes(self):
        for command in ("cases", "show", "analyse", "verify"):
            with self.subTest(command=command):
                self.assertEqual(self.cli(command)[0], 0)
        self.assertEqual(self.cli("show", "--case", str(self.root / "absent.json"))[0], 2)


if __name__ == "__main__":
    unittest.main()
