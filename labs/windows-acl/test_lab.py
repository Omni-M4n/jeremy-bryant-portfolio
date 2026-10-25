import copy
import json
import unittest
import lab

def sample():
    return json.loads((lab.ROOT / "fixtures/guided.json").read_text())

class AclTests(unittest.TestCase):
    def test_empty_acl_denies(self):
        c = sample(); c["data"]["file_aces"] = []
        self.assertEqual(lab.analyse(c)["decisions"], {"q1":"deny", "q2":"deny", "q3":"deny"})

    def test_nonmatching_identity(self):
        c = sample(); c["data"]["token"] = ["visitor"]
        self.assertEqual(lab.analyse(c)["decisions"]["q1"], "deny")

    def test_parent_delete_route(self):
        c = sample()
        c["data"]["file_aces"] = [{"trustee":"reader","kind":"deny","inherited":False,"rights":["delete"]}]
        c["data"]["parent_aces"] = [{"trustee":"reader","kind":"allow","inherited":False,"rights":["delete-child"]}]
        self.assertEqual(lab.analyse(c)["decisions"]["q3"], "allow")

    def test_explicit_allow_before_inherited_deny(self):
        entries = [{"trustee":"reader","kind":"allow","inherited":False,"rights":["read"]}, {"trustee":"reader","kind":"deny","inherited":True,"rights":["read"]}]
        c = sample(); c["data"]["file_aces"] = entries
        self.assertEqual(lab.analyse(c)["decisions"]["q1"], "allow")
        c["data"]["file_aces"] = list(reversed(entries))
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_invalid_and_unchanged(self):
        c = sample(); before = copy.deepcopy(c); lab.analyse(c)
        self.assertEqual(c, before)
        for field, value in [("token", ["reader", "reader"]), ("file_aces", None), ("requests", [{"id":"q1","right":"execute"}])]:
            bad = sample(); bad["data"][field] = value
            with self.assertRaises(ValueError): lab.analyse(bad)
        c["data"]["requests"].append(c["data"]["requests"][0])
        with self.assertRaises(ValueError): lab.analyse(c)

if __name__ == "__main__": unittest.main()
