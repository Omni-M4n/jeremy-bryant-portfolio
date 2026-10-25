import json
import unittest
from lab import analyse, ROOT

class Checks(unittest.TestCase):
    def case(self,name="guided"):
        return json.loads((ROOT/"fixtures"/(name+".json")).read_text())
    def test_repeated_range_not_loss_verdict(self):
        d=analyse(self.case())["decisions"]
        self.assertEqual(d["repetition"],"repeated-range-observed");self.assertEqual(d["timing"],"request-ack-to-response:10ms")
    def test_response_interval(self):
        self.assertEqual(analyse(self.case("changed"))["decisions"]["timing"],"request-ack-to-response:2000ms")
    def test_capture_gap_and_reset(self):
        d=analyse(self.case("challenge"))["decisions"]
        self.assertEqual(d["acknowledgement"],"unseen-bytes-acknowledged");self.assertEqual(d["termination"],"reset-observed")
    def test_zero_interval_is_valid(self):
        c=self.case();c["data"]["packets"][-1]["at_ms"]=210
        self.assertEqual(analyse(c)["decisions"]["timing"],"request-ack-to-response:0ms")
    def test_valid_out_of_order_ranges_fill_gap(self):
        c=self.case();p=c["data"]["packets"];p[0].update(seq=1050,length=50);p[1].update(seq=1000,length=50)
        d=analyse(c)["decisions"];self.assertEqual(d["repetition"],"no-repeat-in-extract");self.assertEqual(d["acknowledgement"],"no-unseen-ack-in-extract")
    def test_reject_malformed_and_unsupported(self):
        for change in (lambda c:c["data"]["packets"][1].update(seq=1050),lambda c:c["data"]["packets"][1].update(at_ms=-1),lambda c:c["data"].update(capture_drops=True),lambda c:c["data"]["packets"][2].update(ack=999),lambda c:c["data"]["packets"][0].update(length=0)):
            c=self.case();change(c)
            with self.assertRaises(ValueError):analyse(c)
    def test_reject_data_or_ack_beyond_single_request(self):
        c=self.case();c["data"]["packets"][0]["length"]=101
        with self.assertRaises(ValueError):analyse(c)
        c=self.case();c["data"]["packets"][2]["ack"]=1101
        with self.assertRaises(ValueError):analyse(c)
    def test_reject_conflicting_packet_artifact_without_mutating_input(self):
        c=self.case();c["data"]["packets"][-1]["at_ms"]=221
        c["artifacts"]={"frames.csv":"id,at_ms,side,kind,seq,length,ack\nf04,220,server,data,5000,20,\n"}
        before=json.dumps(c,sort_keys=True)
        with self.assertRaisesRegex(ValueError,"only packet evidence"):
            analyse(c)
        self.assertEqual(json.dumps(c,sort_keys=True),before)
    def test_single_input_timestamp_edit_changes_interval(self):
        c=self.case();c["data"]["packets"][-1]["at_ms"]=221
        self.assertEqual(c["artifacts"],{})
        self.assertEqual(analyse(c)["decisions"]["timing"],"request-ack-to-response:11ms")
    def test_even_matching_legacy_mirror_is_rejected(self):
        c=self.case()
        header="id,at_ms,side,kind,seq,length,ack\n"
        rows=[",".join("" if r[k] is None else str(r[k]) for k in ("id","at_ms","side","kind","seq","length","ack")) for r in c["data"]["packets"]]
        c["artifacts"]={"frames.csv":header+"\n".join(rows)+"\n"}
        with self.assertRaisesRegex(ValueError,"artifacts must be empty"):
            analyse(c)

if __name__=="__main__":unittest.main()
