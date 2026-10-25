import unittest
from lab import App, exercise, validate
from practice import running, send

class ApiTests(unittest.TestCase):
    def test_boundaries_types_and_extra_fields(self):
        self.assertEqual(validate({'name':'x','count':1}),{'name':'x','count':1})
        self.assertEqual(validate({'name':'x'*20,'count':5})['count'],5)
        self.assertEqual(validate({'name':'café','count':1})['name'],'café')
        for value in ({'name':'','count':1},{'name':'x'*21,'count':1},{'name':'x','count':True},{'name':'x','count':1.0},{'name':'x','count':0},{'name':'x','count':6},{'name':'x','count':None},{'name':'x','count':1,'admin':True},[],{'name':'\n','count':1}):
            with self.assertRaises(ValueError): validate(value)

    def test_json_wire_and_bounded_size(self):
        with running(App()) as port:
            headers={'Content-Type':'application/json'}
            for raw in ('{','{"name":"x","count":NaN}','{"name":"x","count":1,"count":2}'):
                status,body,_=send(port,'POST','/order',raw,headers)
                self.assertEqual((status,body),(400,{'error':'invalid-json'}))
            base='{"name":"x","count":1}'
            self.assertEqual(send(port,'POST','/order',base+' '*(256-len(base)),headers)[0],201)
            self.assertEqual(send(port,'POST','/order',base+' '*(257-len(base)),headers)[0],413)
            self.assertEqual(send(port,'POST','/order',base,{'Content-Type':'text/plain'})[0],415)
            self.assertEqual(send(port,'POST','/order','[]',headers)[0],422)

    def test_plan_limit(self):
        with self.assertRaises(ValueError): exercise({'requests':[{'body':'x'*513,'content_type':'application/json'}]})

if __name__ == '__main__': unittest.main()
