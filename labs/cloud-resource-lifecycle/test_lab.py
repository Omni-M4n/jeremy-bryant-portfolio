"""Independent boundary and invalid-input tests for cloud-resource-lifecycle."""
import copy
import json
from pathlib import Path
import unittest
import lab


class LabTests(unittest.TestCase):
    def case(self, name="guided"):
        return json.loads((Path(__file__).parent / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))

    def test_analysis_preserves_input(self):
        c = self.case()
        before = copy.deepcopy(c)
        lab.analyse(c)
        self.assertEqual(c, before)

    def test_due_date_and_residual_cost(self):
        result = lab.analyse(self.case())["decisions"]
        self.assertEqual(result["r1"], "review-due")
        self.assertEqual(result["cost"], "residual-cost")

    def test_alert_at_exact_threshold(self):
        self.assertEqual(lab.analyse(self.case("changed"))["decisions"]["budget"], "alert-threshold-reached")

    def test_reverse_dependency_order_then_complete_plan(self):
        c = self.case("changed")
        self.assertEqual(lab.analyse(c)["decisions"]["plan"], "blocked")
        c["data"]["delete_order"] = ["r1", "r2"]
        result = lab.analyse(c)["decisions"]
        self.assertEqual(result["plan"], "order-valid-in-model")
        self.assertEqual(result["cost"], "zero-model-cost")

    def test_retention_holds_even_without_dependencies(self):
        self.assertEqual(lab.analyse(self.case("challenge"))["decisions"]["plan"], "blocked")

    def test_cycles_unknown_dependencies_and_negative_cost(self):
        c = self.case()
        c["data"]["resources"][1]["depends_on"] = ["r1"]
        with self.assertRaises(ValueError):
            lab.analyse(c)
        c["data"]["resources"][1]["depends_on"] = ["r9"]
        with self.assertRaises(ValueError):
            lab.analyse(c)
        c = self.case()
        c["data"]["resources"][0]["daily_units"] = -1
        with self.assertRaises(ValueError):
            lab.analyse(c)

    def test_duplicate_deletion_and_boolean_cost(self):
        c = self.case()
        c["data"]["delete_order"] = ["r1", "r1"]
        with self.assertRaises(ValueError):
            lab.analyse(c)
        c = self.case()
        c["data"]["spent_units"] = True
        with self.assertRaises(ValueError):
            lab.analyse(c)


if __name__ == "__main__":
    unittest.main()
