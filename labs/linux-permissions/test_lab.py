"""Boundary and invalid-evidence tests for the offline teaching model."""
import copy
import json
from pathlib import Path
import unittest
import lab

class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((Path(__file__).parent / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_preserves_input(self):
        case = self.case()
        before = copy.deepcopy(case)
        lab.analyse(case)
        self.assertEqual(case, before)

    def test_rejects_unknown_data_field(self):
        case = self.case()
        case["data"]["unsupported"] = 1
        with self.assertRaises(ValueError):
            lab.analyse(case)

    def test_owner_has_no_fallback(self):
        result = lab.analyse(self.case("changed"))["decisions"]
        self.assertEqual(result["read-notes"], "denied-by-mode")
        self.assertEqual(result["write-notes"], "denied-by-mode")

    def test_ancestor_search_blocks_permissive_file(self):
        result = lab.analyse(self.case("challenge"))["decisions"]
        self.assertEqual(result["read-notes"], "denied-by-mode")
        self.assertEqual(result["write-notes"], "denied-by-mode")

    def test_directory_list_search_and_create_differ(self):
        result = lab.analyse(self.case())["decisions"]
        self.assertEqual(result["list-drop"], "denied-by-mode")
        self.assertEqual(result["search-drop"], "allowed-by-mode")
        self.assertEqual(result["create-drop"], "allowed-by-mode")
        case = self.case(); case["data"]["nodes"][3]["mode"] = "732"
        result = lab.analyse(case)["decisions"]
        self.assertEqual(result["create-drop"], "denied-by-mode")
        self.assertEqual(result["search-drop"], "denied-by-mode")

    def test_directory_read_can_list_names_without_target_search(self):
        case = self.case(); case["data"]["nodes"][3]["mode"] = "734"
        result = lab.analyse(case)["decisions"]
        self.assertEqual(result["list-drop"], "allowed-by-mode")
        self.assertEqual(result["search-drop"], "denied-by-mode")

    def test_rejects_missing_ancestor_and_noncanonical_path(self):
        case = self.case(); del case["data"]["nodes"][1]
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case(); case["data"]["nodes"][2]["path"] = "/srv/../notes.txt"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_rejects_privileged_actor_special_bits_and_wrong_type(self):
        case = self.case(); case["data"]["actor"]["name"] = "root"
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case(); case["data"]["nodes"][3]["mode"] = "1733"
        with self.assertRaises(ValueError): lab.analyse(case)
        case = self.case(); case["data"]["requests"][0]["operation"] = "list-dir"
        with self.assertRaises(ValueError): lab.analyse(case)

    def test_other_class_when_not_owner_or_group(self):
        case = self.case(); case["data"]["actor"]["groups"] = []
        case["data"]["nodes"][1]["mode"] = "755"
        case["data"]["nodes"][2]["mode"] = "604"
        self.assertEqual(lab.analyse(case)["decisions"]["read-notes"], "allowed-by-mode")

if __name__ == "__main__":
    unittest.main()
