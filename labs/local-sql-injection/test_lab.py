import unittest
from urllib.parse import urlencode
from lab import App, exercise, lookup
from practice import running, send

class SqlTests(unittest.TestCase):
    def test_rows_and_legitimate_quotes(self):
        self.assertEqual(lookup('Mira','bound'),[(1,'Mira','Clouds')])
        self.assertEqual(lookup('Mira','joined'),[(1,'Mira','Clouds')])
        self.assertEqual(lookup("O'Reed",'bound'),[(2,"O'Reed",'Rivers')])
        self.assertEqual(lookup("Mira' OR '1'='1",'bound'),[])
        self.assertEqual([r[0] for r in lookup("Mira' OR '1'='1",'joined')],[1,2,3])
        self.assertEqual(lookup('Missing','bound'),[])

    def test_wire_error_has_no_sql_or_paths(self):
        with running(App()) as port:
            status, body, _ = send(port,'GET','/joined?' + urlencode({'name':"O'Reed"}))
            self.assertEqual((status,body),(400,{'error':'query-not-valid'}))
            self.assertEqual(send(port,'GET','/bound?name=Mira&name=Tao')[0],400)
            self.assertEqual(send(port,'GET','/bound?other=Mira')[0],400)

    def test_narrow_read_only_input_contract(self):
        for name in ('Tao', 'DELETE FROM readers', '', 'x'*100):
            with self.assertRaises(ValueError): lookup(name,'joined')
        with self.assertRaises(ValueError): lookup('Mira','unknown')
        with self.assertRaises(ValueError): exercise({'name':'Mira','extra':1})

if __name__ == '__main__': unittest.main()
