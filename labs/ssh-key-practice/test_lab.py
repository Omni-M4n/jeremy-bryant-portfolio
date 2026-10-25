import copy
import json
import unittest
import lab

def sample(): return json.loads((lab.ROOT / "fixtures/guided.json").read_text())

class SshEvidenceTests(unittest.TestCase):
    def test_unverified_host_stops_trial_acceptance(self):
        c=sample();c["data"]["host_fingerprint_match"]=False
        self.assertEqual(lab.analyse(c)["decisions"]["t1"],"host-unverified-stop")

    def test_different_user_is_not_intended(self):
        c=sample();c["data"]["trials"][0]["user"]="visitor"
        self.assertEqual(lab.analyse(c)["decisions"]["t1"],"unexpected-key-access")

    def test_not_run_and_recovery(self):
        c=sample();c["data"]["trials"][0].update(result="not-run",method="none")
        c["data"]["recovery_console_tested"]=False
        self.assertEqual(lab.analyse(c)["decisions"]["t1"],"not-tested")
        self.assertEqual(lab.analyse(c)["decisions"]["r1"],"recovery-not-tested")

    def test_invalid_evidence(self):
        for change in [{"result":"auth-rejected","method":"publickey"},{"result":"accepted","method":"none"},{"method":"keyboard-interactive"},{"id":"r1"}]:
            c=sample();c["data"]["trials"][0].update(change)
            with self.assertRaises(ValueError): lab.analyse(c)
        c=sample();c["data"]["host_fingerprint_match"]=1
        with self.assertRaises(ValueError): lab.analyse(c)

    def test_no_input_change(self):
        c=sample();before=copy.deepcopy(c);lab.analyse(c);self.assertEqual(c,before)

if __name__ == "__main__": unittest.main()
