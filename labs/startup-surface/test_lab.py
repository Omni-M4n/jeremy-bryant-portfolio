import copy
import json
import unittest
import lab

def sample(): return json.loads((lab.ROOT / "fixtures/guided.json").read_text())

class StartupTests(unittest.TestCase):
    def test_missing_and_new(self):
        c=sample();c["data"]["observed"]=[];c["data"]["approvals"]=[]
        self.assertEqual(lab.analyse(c)["decisions"],{"e1":"missing-follow-up"})
        c=sample();c["data"]["baseline"]=[];c["data"]["approvals"]=[]
        self.assertEqual(set(lab.analyse(c)["decisions"].values()),{"unexplained-addition"})

    def test_command_identity_owner_changes(self):
        for field,value in [("command","C:/Other/note.exe"),("identity","LocalSystem"),("owner","other")]:
            c=sample();c["data"]["observed"][0][field]=value
            self.assertEqual(lab.analyse(c)["decisions"]["e1"],"unexplained-change")

    def test_stale_approval_rejected(self):
        c=sample();c["data"]["approvals"][0]["sha256"]="e"*64
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_invalid(self):
        for field,value in [("sha256","abcd"),("mechanism","other")]:
            c=sample();c["data"]["observed"][0][field]=value
            with self.assertRaises(ValueError): lab.analyse(c)
        c=sample();c["data"]["observed"].append(copy.deepcopy(c["data"]["observed"][0]))
        with self.assertRaises(ValueError): lab.analyse(c)
        c=sample();c["data"]={"baseline":[],"observed":[],"approvals":[]}
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_no_input_change(self):
        c=sample();before=copy.deepcopy(c);lab.analyse(c);self.assertEqual(c,before)

    def test_control_characters_rejected_in_all_evidence_fields(self):
        controls = [chr(n) for n in range(32)] + [chr(n) for n in range(127, 160)]
        controls += ["\u2028", "\u2029", "\u200b"]
        for field in ("command", "identity", "owner"):
            for character in controls:
                with self.subTest(field=field, codepoint=ord(character)):
                    c=sample()
                    c["data"]["observed"][0][field] += character + "hidden"
                    with self.assertRaises(ValueError): lab.analyse(c)

    def test_printable_values_with_spaces_remain_valid(self):
        c=sample()
        for collection in ("baseline", "observed"):
            c["data"][collection][0].update(command='"C:/Lab Tools/timer.exe" --wait 10',
                                           identity="Lab Reader", owner="Lab Admin")
        self.assertEqual(lab.analyse(c)["decisions"]["e1"], "matches-baseline")
        c["data"]["observed"][0]["command"]='"C:/Lab Tools/timer.exe" --wait 20'
        self.assertEqual(lab.analyse(c)["decisions"]["e1"], "unexplained-change")

if __name__ == "__main__": unittest.main()
