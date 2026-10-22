
"""Meaningful boundaries and malformed-input checks; fixtures have fixed answers."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab


class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((lab.ROOT / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def sync(self, case):
        if lab.LAB_ID == "asset-discovery":
            case["artifacts"] = {"scan.xml": case["data"]["nmap_xml"]}
        elif lab.LAB_ID == "tcp-handshake":
            case["artifacts"] = {"packets.csv": lab.packet_csv(case["data"]["flows"])}
        elif lab.LAB_ID == "http-header-review":
            case["artifacts"] = {"headers.txt": lab.rendered(case["data"]["responses"])}
        elif lab.LAB_ID == "email-triage":
            case["artifacts"] = {"headers.txt": lab.rendered(case["data"]["messages"])}
        return case

    def test_fixed_reference_cases(self):
        for name in ("guided", "changed", "challenge"):
            with self.subTest(case=name):
                expected = json.loads((lab.ROOT / "reference" / (name + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(lab.analyse(self.case(name)), expected)

    def test_analysis_preserves_input(self):
        case = self.case()
        before = deepcopy(case)
        lab.analyse(case)
        self.assertEqual(case, before)

    def test_unknown_data_field_rejected(self):
        case = self.case()
        case["data"]["unexpected"] = True
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_missing_envelope_rejected(self):
        case = self.case()
        del case["synthetic"]
        with self.assertRaises(ValueError):
            lab.analyse(case)


    def test_hsts_threshold_boundary(self):
        case = self.case()
        row = case["data"]["responses"][0]
        row["headers"] = row["headers"].replace("31536000", "31535999")
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["booking"], "requirement-gaps:hsts-duration")

    def test_default_src_is_not_frame_ancestors(self):
        case = self.case()
        row = case["data"]["responses"][0]
        row["headers"] = row["headers"].replace("; frame-ancestors 'none'", "")
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["booking"], "requirement-gaps:frame-ancestors")

    def test_header_names_case_insensitive_cookie_names_sensitive(self):
        case = self.case()
        row = case["data"]["responses"][0]
        row["headers"] = row["headers"].replace("X-Content-Type-Options", "x-content-type-options").replace("session=", "Session=")
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["booking"], "requirement-gaps:session-cookie")

    def test_secure_and_httponly_are_independent(self):
        case = self.case()
        row = case["data"]["responses"][0]
        row["headers"] = row["headers"].replace("; Secure", "")
        self.assertEqual(lab.analyse(self.sync(case))["decisions"]["booking"], "requirement-gaps:cookie-secure")

    def test_duplicate_singleton_and_fold_rejected(self):
        for text in ("X-Test: one\nX-Test: two\n", "X-Test: one\n continuation\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                lab.headers(text)

    def test_cookie_duplicates_and_unknown_forms_rejected(self):
        for value in ("session=x; Secure; Secure", "session=x; Expires=Tomorrow", "session=x; Secure=yes"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                lab.parse_cookie(value)

    def test_duplicate_csp_directive_rejected(self):
        with self.assertRaises(ValueError):
            lab.parse_csp("frame-ancestors 'self'; frame-ancestors 'none'")

    def test_invalid_hsts_age_rejected(self):
        for value in ("max-age=-1", "max-age=abc", "max-age=1; max-age=2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                lab.parse_hsts(value)

    def test_artifact_disagreement_rejected(self):
        case = self.case()
        case["artifacts"]["headers.txt"] += "wrong"
        with self.assertRaises(ValueError):
            lab.analyse(case)


if __name__ == "__main__":
    unittest.main(verbosity=2)
