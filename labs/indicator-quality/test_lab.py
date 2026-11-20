"""Table-driven checks for the indicator-quality teaching model."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab


class IndicatorQualityTests(unittest.TestCase):
    def fixture(self, case_id="guided"):
        return json.loads(
            (lab.ROOT / "fixtures" / f"{case_id}.json").read_text(encoding="utf-8")
        )

    def single(self, **updates):
        case = self.fixture()
        row = case["data"]["records"][0]
        row.update(updates)
        case["data"]["records"] = [row]
        return case

    def decision(self, **updates):
        return lab.analyse(self.single(**updates))["decisions"]["i1"]

    def test_all_fixed_references(self):
        for case_id in ("guided", "changed", "challenge"):
            with self.subTest(case_id=case_id):
                expected = json.loads(
                    (lab.ROOT / "reference" / f"{case_id}.json").read_text(encoding="utf-8")
                )
                self.assertEqual(lab.analyse(self.fixture(case_id)), expected)

    def test_precedence_table(self):
        cases = (
            ({"valid_until": "2026-01-15T00:00:00Z", "contradicted": True,
              "source": "copied", "confidence": None, "scope": "shared-service"},
             "review-expiry"),
            ({"contradicted": True, "source": "copied", "confidence": None,
              "scope": "shared-service"}, "review-conflict"),
            ({"source": "copied", "confidence": 95, "scope": "shared-service"},
             "seek-support"),
            ({"source": "direct", "confidence": None, "scope": "shared-service"},
             "seek-support"),
            ({"source": "direct", "confidence": 69, "scope": "shared-service"},
             "seek-support"),
            ({"source": "direct", "confidence": 70, "scope": "shared-service"},
             "narrow-scope"),
            ({"source": "direct", "confidence": 70, "scope": "single-host"},
             "retain-as-context"),
        )
        for updates, expected in cases:
            with self.subTest(updates=updates):
                self.assertEqual(self.decision(**updates), expected)

    def test_expiry_equality_is_expired(self):
        self.assertEqual(
            self.decision(valid_until="2026-01-15T00:00:00Z"),
            "review-expiry",
        )

    def test_confidence_boundary(self):
        self.assertEqual(self.decision(confidence=70), "retain-as-context")
        self.assertEqual(self.decision(confidence=69), "seek-support")

    def test_review_date_before_seven_days_uses_expiry(self):
        observation = lab.analyse(self.single(valid_until="2026-01-20T00:00:00Z"))[
            "observations"
        ][0]
        self.assertIn("review_date=2026-01-20T00:00:00Z", observation)

    def test_review_date_at_seven_days_uses_same_boundary(self):
        observation = lab.analyse(self.single(valid_until="2026-01-22T00:00:00Z"))[
            "observations"
        ][0]
        self.assertIn("review_date=2026-01-22T00:00:00Z", observation)

    def test_review_date_after_seven_days_uses_as_of_plus_seven(self):
        observation = lab.analyse(self.single(valid_until="2026-01-22T00:00:01Z"))[
            "observations"
        ][0]
        self.assertIn("review_date=2026-01-22T00:00:00Z", observation)

    def test_review_date_near_year_9999_does_not_overflow(self):
        for as_of, expiry, expected in (
            ("9999-12-29T00:00:00Z", "9999-12-30T00:00:00Z", "9999-12-30T00:00:00Z"),
            ("9999-12-23T00:00:00Z", "9999-12-30T00:00:00Z", "9999-12-30T00:00:00Z"),
            ("9999-12-01T00:00:00Z", "9999-12-30T00:00:00Z", "9999-12-08T00:00:00Z"),
        ):
            case = self.single(valid_until=expiry)
            case["data"]["as_of"] = as_of
            with self.subTest(as_of=as_of, expiry=expiry):
                result = lab.analyse(case)
                self.assertEqual(result["decisions"], {"i1": "retain-as-context"})
                self.assertIn(f"review_date={expected}", result["observations"][0])

    def test_non_context_decisions_review_as_of(self):
        for updates in (
            {"valid_until": "2026-01-15T00:00:00Z"},
            {"contradicted": True},
            {"source": "copied"},
            {"scope": "shared-service"},
        ):
            with self.subTest(updates=updates):
                observation = lab.analyse(self.single(**updates))["observations"][0]
                self.assertIn("review_date=2026-01-15T00:00:00Z", observation)

    def test_observation_preserves_every_supplied_basis_and_output(self):
        observation = lab.analyse(self.fixture())["observations"][0]
        for text in (
            "value=mail.test", "type=domain", "evidence_id=r1",
            "observed_at=2026-01-10T00:00:00Z",
            "reported_at=2026-01-11T00:00:00Z",
            "valid_until=2026-01-20T00:00:00Z",
            "as_of=2026-01-15T00:00:00Z", "supplied conflict=false",
            "source=direct", "stated confidence=80", "scope=single-host",
            "decision=retain-as-context", "review_date=2026-01-20T00:00:00Z",
        ):
            with self.subTest(text=text):
                self.assertIn(text, observation)

    def test_input_is_not_modified(self):
        case = self.fixture()
        before = deepcopy(case)
        lab.analyse(case)
        self.assertEqual(case, before)

    def test_returned_results_are_isolated(self):
        first = lab.analyse(self.fixture())
        first["decisions"]["i1"] = "poisoned"
        first["observations"][0] = "poisoned"
        first["limitations"].append("poisoned")
        second = lab.analyse(self.fixture())
        self.assertEqual(second["decisions"]["i1"], "retain-as-context")
        self.assertTrue(second["observations"][0].startswith("i1: value=mail.test"))
        self.assertNotIn("poisoned", second["limitations"])
        self.assertIsNot(first["limitations"], second["limitations"])

    def test_context_requires_exact_question_object(self):
        invalid_contexts = (
            {},
            {"question": "Which decision applies?", "extra": "no"},
            {"other": "Which decision applies?"},
            [],
        )
        for context in invalid_contexts:
            case = self.fixture()
            case["context"] = context
            with self.subTest(context=context), self.assertRaises(ValueError):
                lab.analyse(case)

    def test_context_question_is_bounded_trimmed_printable_ascii(self):
        invalid_questions = ("", " ", " leading", "trailing ", "line\nbreak", "tab\there",
                             "escape\x1btext", "caf\N{LATIN SMALL LETTER E WITH ACUTE}", "x" * 201, 7)
        for value in invalid_questions:
            case = self.fixture()
            case["context"]["question"] = value
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                lab.analyse(case)
        case = self.fixture()
        case["context"]["question"] = "Q" * 200
        lab.analyse(case)

    def test_valid_ascii_test_domains_include_multiple_labels_and_limits(self):
        longest = ".".join(("a" * 63, "b" * 63, "c" * 63, "d" * 56, "test"))
        self.assertEqual(len(longest), 253)
        for value in ("mail.test", "mx.mail.test", "a-1.example.test", longest):
            with self.subTest(value=value):
                self.assertEqual(self.decision(value=value, type="domain"), "retain-as-context")

    def test_invalid_test_domains_fail_closed(self):
        too_long = ".".join(("a" * 63, "b" * 63, "c" * 63, "d" * 57, "test"))
        invalid = (
            ".test", "mail..test", "-mail.test", "mail-.test", "a" * 64 + ".test",
            too_long, "mail.example", "mail.test.", "mail_test.test", "MAIL.test",
            "mail.TEST", "m\N{LATIN SMALL LETTER A WITH ACUTE}il.test", 7,
        )
        for value in invalid:
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                lab.analyse(self.single(value=value, type="domain"))

    def test_rfc5737_ipv4_blocks_are_accepted(self):
        for value in ("192.0.2.0", "192.0.2.255", "198.51.100.1", "203.0.113.255"):
            with self.subTest(value=value):
                self.assertEqual(self.decision(value=value, type="ipv4"), "retain-as-context")

    def test_non_rfc5737_or_malformed_addresses_are_rejected(self):
        for value in ("127.0.0.1", "10.0.0.1", "2001:db8::1", "192.0.2.01",
                      "192.0.2", "192.0.2.256", "", 7, True):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                lab.analyse(self.single(value=value, type="ipv4"))

    def test_cli_sanitizes_invalid_ipv4_errors(self):
        payloads = ("192.0.2.1\nFORGED\x1b[31m", "192.0.2.1\N{RIGHT-TO-LEFT OVERRIDE}", "9" * 900_000)
        expected = "Input error: use an RFC 5737 documentation IPv4 address\n"
        for payload in payloads:
            case = self.single(value=payload, type="ipv4")
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "case.json"
                path.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(lab.ROOT / "lab.py"), "analyse", "--case", str(path)],
                    cwd=lab.ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            with self.subTest(payload_length=len(payload)):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stderr, expected)
                self.assertTrue(result.stderr.isascii())
                self.assertEqual(len(result.stderr.splitlines()), 1)
                self.assertNotIn(payload[:20], result.stderr)

    def test_data_and_record_schemas_are_exact(self):
        mutations = []
        case = self.fixture(); case["data"]["extra"] = True; mutations.append(case)
        case = self.fixture(); del case["data"]["as_of"]; mutations.append(case)
        case = self.fixture(); case["data"]["records"][0]["extra"] = True; mutations.append(case)
        case = self.fixture(); del case["data"]["records"][0]["scope"]; mutations.append(case)
        for index, case in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(ValueError):
                lab.analyse(case)

    def test_artifacts_must_be_exactly_empty(self):
        case = self.fixture()
        case["artifacts"] = {"report.txt": "not authoritative"}
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_record_list_bounds_and_type(self):
        for records in ([], self.fixture()["data"]["records"] * 16, {}, None):
            case = self.fixture()
            case["data"]["records"] = records
            with self.subTest(kind=type(records).__name__, length=len(records) if hasattr(records, "__len__") else None), self.assertRaises(ValueError):
                lab.analyse(case)
        case = self.fixture()
        case["data"]["records"] = [deepcopy(case["data"]["records"][0]) for _ in range(30)]
        for index, row in enumerate(case["data"]["records"]):
            row["id"] = f"i{index}"
            row["evidence_id"] = f"r{index}"
        lab.analyse(case)

    def test_record_and_evidence_ids_are_unique(self):
        case = self.fixture()
        case["data"]["records"][1]["id"] = "i1"
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_same_value_with_unique_evidence_remains_independent_rows(self):
        case = self.fixture()
        case["data"]["records"][1]["value"] = case["data"]["records"][0]["value"]
        result = lab.analyse(case)
        self.assertEqual(result["decisions"], {
            "i1": "retain-as-context",
            "i2": "seek-support",
        })
        self.assertEqual(len(result["observations"]), 2)
        self.assertIn("does not link records across sources", " ".join(result["limitations"]))
        case = self.fixture()
        case["data"]["records"][1]["evidence_id"] = "r1"
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_ids_use_the_exact_bounded_lexical_form(self):
        for field in ("id", "evidence_id"):
            for value in ("", "1record", "Upper", "under_score", "space here", "a" * 41, 7):
                case = self.fixture()
                case["data"]["records"][0][field] = value
                with self.subTest(field=field, value=repr(value)), self.assertRaises(ValueError):
                    lab.analyse(case)

    def test_enums_booleans_and_confidence_are_exact(self):
        invalid = (
            ("type", "url"), ("source", "unknown"), ("scope", "global"),
            ("contradicted", 1), ("contradicted", "false"),
            ("confidence", -1), ("confidence", 101), ("confidence", True),
            ("confidence", 70.0), ("confidence", "70"),
        )
        for field, value in invalid:
            case = self.fixture()
            case["data"]["records"][0][field] = value
            with self.subTest(field=field, value=repr(value)), self.assertRaises((ValueError, TypeError)):
                lab.analyse(case)

    def test_timestamps_use_exact_real_utc_seconds(self):
        invalid = (
            "2026-01-10", "2026-01-10T00:00:00+00:00", "2026-01-10T00:00:00.000Z",
            "2026-02-30T00:00:00Z", "0000-01-01T00:00:00Z", "2026-01-10T24:00:00Z", 7,
        )
        for field in ("as_of", "observed_at", "reported_at", "valid_until"):
            for value in invalid:
                case = self.fixture()
                target = case["data"] if field == "as_of" else case["data"]["records"][0]
                target[field] = value
                with self.subTest(field=field, value=repr(value)), self.assertRaises((ValueError, TypeError)):
                    lab.analyse(case)

    def test_timestamp_ordering_is_enforced(self):
        invalid_updates = (
            {"observed_at": "2026-01-12T00:00:00Z", "reported_at": "2026-01-11T00:00:00Z"},
            {"reported_at": "2026-01-16T00:00:00Z"},
            {"valid_until": "2026-01-10T00:00:00Z"},
            {"reported_at": "2026-01-14T00:00:00Z", "valid_until": "2026-01-13T00:00:00Z"},
        )
        for updates in invalid_updates:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                lab.analyse(self.single(**updates))

    def test_equal_observed_reported_and_reported_expiry_are_supported(self):
        case = self.single(
            observed_at="2026-01-10T00:00:00Z",
            reported_at="2026-01-10T00:00:00Z",
            valid_until="2026-01-10T00:00:00Z",
        )
        with self.assertRaises(ValueError):
            lab.analyse(case)
        self.assertEqual(
            self.decision(
                observed_at="2026-01-09T00:00:00Z",
                reported_at="2026-01-10T00:00:00Z",
                valid_until="2026-01-10T00:00:00Z",
            ),
            "review-expiry",
        )

    def test_limitations_state_supplied_and_nonoperational_boundaries(self):
        limitations = " ".join(lab.analyse(self.fixture())["limitations"])
        for phrase in (
            "synthetic and supplied", "No lookup", "reputation check", "blocking action",
            "attribution", "does not verify provenance", "source reliability", "truth",
            "corroboration", "does not link records across sources", "not STIX requirements",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, limitations)


if __name__ == "__main__":
    unittest.main()
