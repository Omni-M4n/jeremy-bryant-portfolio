import unittest
from lab import App, exercise
from practice import Request, running, send

class RateTests(unittest.TestCase):
    def test_threshold_exact_reset_and_retry_rounding(self):
        now=[10.0]
        app=App(lambda:now[0])
        request=Request('GET','/ticket',{},b'','http://127.0.0.1:8765')
        self.assertEqual([app(request)[0] for _ in range(4)],[200,200,200,429])
        self.assertEqual(app(request)[2]['Retry-After'],'2')
        now[0]=11.999
        self.assertEqual(app(request)[0],429)
        self.assertEqual(app(request)[2]['Retry-After'],'1')
        now[0]=12.0
        self.assertEqual(app(request)[0],200)
        self.assertEqual(app.used,1)

    def test_other_route_does_not_use_allowance(self):
        with running(App()) as port:
            self.assertEqual(send(port,'GET','/other')[0],404)
            self.assertEqual(send(port,'POST','/ticket')[0],405)
            self.assertEqual([send(port,'GET','/ticket')[0] for _ in range(4)],[200,200,200,429])

    def test_plan_bounds(self):
        for steps in ([], ['ticket']*9, ['wait','wait'], ['unknown'], [True]):
            with self.assertRaises(ValueError): exercise({'steps':steps})

if __name__ == '__main__': unittest.main()
