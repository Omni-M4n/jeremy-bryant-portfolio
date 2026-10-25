import json
import copy
import unittest
from urllib.parse import urlencode
from lab import App, Companion, exercise
from practice import running, send

class CsrfTests(unittest.TestCase):
    def test_origin_and_token_are_both_needed(self):
        with running(App()) as port:
            origin=f'http://127.0.0.1:{port}'
            cookie=send(port,'POST','/login')[2]['set-cookie'].split(';')[0]
            token=send(port,'GET','/token',headers={'Cookie':cookie})[1]['token']
            def change(source,proof,route='/protected'):
                headers={'Content-Type':'application/x-www-form-urlencoded','Cookie':cookie}
                if source is not None: headers['Origin']=source
                data={'preference':'gold'}
                if proof is not None: data['token']=proof
                return send(port,'POST',route,urlencode(data),headers)
            self.assertEqual(change(origin,None)[0],403)
            self.assertEqual(change(origin,'wrong')[0],403)
            self.assertEqual(change(origin,'\u00e9')[0],403)
            self.assertEqual(change(None,token)[0],403)
            self.assertEqual(change(origin+'0',token)[0],403)
            self.assertEqual(send(port,'GET','/state',headers={'Cookie':cookie})[1],{'preference':'grey'})
            self.assertEqual(change(origin,token)[0],200)
            self.assertEqual(change(origin+'0',None,'/open')[0],200)
            self.assertEqual(send(port,'GET','/protected')[0],401)
            self.assertNotIn('access-control-allow-origin',send(port,'GET','/token',headers={'Cookie':cookie})[2])

    def test_pair_pages_and_form_validation(self):
        with running(App()) as port:
            with running(Companion(port)) as other:
                self.assertNotEqual(port,other)
                body=send(other,'GET','/')[1]
                self.assertIn(f'action="http://127.0.0.1:{port}/protected"',body)
                self.assertNotIn('name="token"',body)
            cookie=send(port,'POST','/login')[2]['set-cookie'].split(';')[0]
            self.assertIn('name="token"',send(port,'GET','/form',headers={'Cookie':cookie})[1])
            self.assertEqual(send(port,'POST','/open','preference=blue&preference=gold',{'Cookie':cookie,'Content-Type':'application/x-www-form-urlencoded'})[0],400)

    def test_stale_token_and_redaction(self):
        row=dict(route='protected',preference='blue',origin='same',token='previous',cookie=True)
        result=exercise({'rotate':True,'requests':[row]})
        self.assertEqual(result['checks'],[{'status':403,'preference_after':'grey'}])
        self.assertNotIn('csrf_training=',json.dumps(result))
        with self.assertRaises(ValueError): exercise({'rotate':False,'requests':[row]})

    def test_malformed_cookie_preserves_the_preference(self):
        app = App()
        with running(app) as port:
            cookie = send(port,'POST','/login')[2]['set-cookie'].split(';')[0]
            before = copy.deepcopy(app.sessions)
            status, value, _ = send(port,'GET','/state',headers={'Cookie':'a@b=c'})
            self.assertEqual((status,value),(400,{'error':'invalid-request'}))
            self.assertEqual(app.sessions,before)
            self.assertEqual(send(port,'GET','/state',headers={'Cookie':cookie})[1],{'preference':'grey'})

if __name__ == '__main__': unittest.main()
