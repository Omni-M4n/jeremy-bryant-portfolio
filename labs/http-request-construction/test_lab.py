import unittest
from unittest.mock import patch
from lab import App, exercise, fields
from practice import running, send

class RequestTests(unittest.TestCase):
    def test_encoding_and_repeats(self):
        self.assertEqual(fields('v=a%2Bb&v=a+b&empty='), {'v':['a+b','a b'],'empty':['']})
        self.assertEqual(fields('word=caf%C3%A9'), {'word':['café']})
        for raw in ('a=%ZZ', 'a=%FF', 'a', '&', '&'.join('x=1' for _ in range(9))):
            with self.assertRaises((ValueError, UnicodeError)):
                fields(raw)

    def test_wire_query_body_and_methods(self):
        with running(App()) as port:
            status, body, _ = send(port,'POST','/inspect?item=pear','item=plum',{'Content-Type':'application/x-www-form-urlencoded'})
            self.assertEqual(status,200)
            self.assertEqual((body['query'],body['form']),({'item':['pear']},{'item':['plum']}))
            self.assertEqual(send(port,'GET','/inspect','x=1')[0],400)
            self.assertEqual(send(port,'POST','/inspect','{}',{'Content-Type':'application/json'})[0],415)
            self.assertEqual(send(port,'PUT','/inspect')[0],405)
            self.assertEqual(send(port,'GET','/inspect?x=%ZZ')[0],400)

    def test_plan_rejects_header_injection(self):
        row=dict(method='GET',target='/inspect',body='',content_type='',note='x\r\nOther: y')
        with self.assertRaises(ValueError): exercise({'requests':[row]})
        with self.assertRaises(ValueError): exercise({'requests':[], 'extra':True})

    def test_bad_targets_stop_before_network_use(self):
        bad = ['/inspect?item=red apple', '/inspect?x=\t', '/inspect?x=\x7f',
               '/inspect?word=café', '/inspection', '//other.test/inspect',
               '/inspect#fragment', '/inspect#', '/inspect?item=red%20apple#',
               'http://other.test/inspect']
        for target in bad:
            row = dict(method='GET',target=target,body='',content_type='',note='')
            with self.subTest(target=target), patch('lab.running') as server:
                with self.assertRaises(ValueError): exercise({'requests':[row]})
                server.assert_not_called()

    def test_encoded_space_is_sent_and_decoded(self):
        row = dict(method='GET',target='/inspect?item=red%20apple',body='',content_type='',note='')
        result = exercise({'requests':[row]})['checks'][0]
        self.assertEqual(result['status'],200)
        self.assertEqual(result['response']['query'],{'item':['red apple']})

    def test_encoded_hash_remains_query_data(self):
        row = dict(method='GET',target='/inspect?item=red%23apple',body='',content_type='',note='')
        result = exercise({'requests':[row]})['checks'][0]
        self.assertEqual(result['status'],200)
        self.assertEqual(result['response']['query'],{'item':['red#apple']})

if __name__ == '__main__': unittest.main()
