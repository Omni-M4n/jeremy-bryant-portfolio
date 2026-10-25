import json
import unittest
from lab import App, TTL, exercise
from practice import Request, running, send

class SessionTests(unittest.TestCase):
    def test_exact_expiry_and_rotation(self):
        clock = [100.0]
        app = App(lambda: clock[0])
        def call(method, path, cookie="", body=b""):
            result = app(Request(method, path, {"cookie": cookie, "content-type": "application/json"}, body, "http://127.0.0.1:8765"))
            return result
        body = b'{"account":"reader","password":"training-only"}'
        first = call("POST", "/login", body=body)[2]["Set-Cookie"].split(";")[0]
        clock[0] = 100 + TTL - .001
        self.assertEqual(call("GET", "/profile", first)[0], 200)
        clock[0] = 100 + TTL
        self.assertEqual(call("GET", "/profile", first)[0], 401)
        second = call("POST", "/login", body=body)[2]["Set-Cookie"].split(";")[0]
        third = call("POST", "/login", second, body)[2]["Set-Cookie"].split(";")[0]
        self.assertNotEqual(second, third)
        self.assertEqual(call("GET", "/profile", second)[0], 401)
        self.assertEqual(call("GET", "/profile", third)[0], 200)
        self.assertEqual(call("POST", "/logout", third)[0], 200)
        self.assertEqual(call("GET", "/profile", third)[0], 401)

    def test_wire_rejection_and_redaction(self):
        with running(App()) as port:
            self.assertEqual(send(port, "POST", "/login", "{}")[0], 415)
            status, value, _ = send(port, "POST", "/login", "{", {"Content-Type":"application/json"})
            self.assertEqual((status, value), (400, {"error":"invalid-request"}))
            duplicate = '{"account":"reader","password":"wrong","password":"training-only"}'
            self.assertEqual(send(port, "POST", "/login", duplicate, {"Content-Type":"application/json"})[0], 400)
            self.assertEqual(send(port, "GET", "/profile", headers={"Host":"outside.test"})[0], 400)
            self.assertEqual(send(port, "POST", "/login", "x" * 4097)[0], 413)
        result = exercise({"steps":["login","logout","old-profile"]})
        self.assertEqual([r["status"] for r in result["checks"]], [200,200,401])
        self.assertNotIn("training_session=", json.dumps(result))

    def test_invalid_plans(self):
        for value in ({"steps":["unknown"]}, {"steps":[]}, {"steps":[True]}, {"steps":["wait","wait"]}, {"steps":["login"],"extra":1}):
            with self.assertRaises(ValueError):
                exercise(value)

    def test_malformed_cookie_does_not_change_a_session(self):
        app = App(lambda: 100.0)
        with running(app) as port:
            body = '{"account":"reader","password":"training-only"}'
            cookie = send(port,'POST','/login',body,{'Content-Type':'application/json'})[2]['set-cookie'].split(';')[0]
            before = dict(app.sessions)
            status, value, _ = send(port,'GET','/profile',headers={'Cookie':'a@b=c'})
            self.assertEqual((status,value),(400,{'error':'invalid-request'}))
            self.assertEqual(app.sessions,before)
            self.assertEqual(send(port,'GET','/profile',headers={'Cookie':cookie})[0],200)

if __name__ == "__main__":
    unittest.main()
