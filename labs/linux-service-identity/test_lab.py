import copy
import json
import unittest
import lab

def sample(): return json.loads((lab.ROOT / "fixtures/guided.json").read_text())

class IdentityTests(unittest.TestCase):
    def test_inactive(self):
        c=sample(); c["data"]["service"].update(state="inactive", observed_user="")
        self.assertEqual(lab.analyse(c)["decisions"]["s1"], "not-running")

    def test_default_root_and_exact_target(self):
        c=sample(); c["data"]["service"].update(configured_user="",observed_user="root")
        c["data"]["requests"][0]["run_as"]="root"
        answer=lab.analyse(c)["decisions"]
        self.assertEqual(answer["s1"],"identity-matches")
        self.assertEqual(answer["q1"],"not-listed")

    def test_empty_arguments_not_any_arguments(self):
        c=sample(); c["data"]["rules"][0]["arguments"]=[]
        self.assertEqual(lab.analyse(c)["decisions"]["q1"],"not-listed")
        c["data"]["requests"][0]["arguments"]=[]
        self.assertEqual(lab.analyse(c)["decisions"]["q1"],"allowed-by-listed-rule")

    def test_validation(self):
        for field,value in [("state","starting"),("observed_user","")]:
            c=sample();c["data"]["service"][field]=value
            with self.assertRaises(ValueError): lab.analyse(c)
        c=sample(); c["data"]["rules"][0]["arguments"]=["*"]
        with self.assertRaises(ValueError): lab.analyse(c)
        c=sample();c["data"]["requests"][0]["id"]="s1"
        with self.assertRaises(ValueError): lab.analyse(c)
        c=sample(); c["data"]["rules"].append(copy.deepcopy(c["data"]["rules"][0]))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_no_input_change(self):
        c=sample();before=copy.deepcopy(c);lab.analyse(c);self.assertEqual(c,before)

if __name__ == "__main__": unittest.main()
