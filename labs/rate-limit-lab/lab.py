"""Three requests in a short, shared window. Never a load test."""
from pathlib import Path
import math
import time
from practice import exact, main, reply, running, send
ROOT = Path(__file__).resolve().parent
LAB_ID = "rate-limit-lab"
LIMIT, WINDOW = 3, 2.0

class App:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.started = None
        self.used = 0

    def __call__(self, request):
        if request.path != "/ticket":
            return reply(404,{"error":"route"})
        if request.method != "GET":
            return reply(405,{"error":"method"},{"Allow":"GET"})
        now = self.clock()
        if self.started is None or now >= self.started + WINDOW:
            self.started, self.used = now, 0
        if self.used >= LIMIT:
            delay = max(1, math.ceil(self.started + WINDOW - now))
            return reply(429,{"remaining":0},{"Retry-After":str(delay)})
        self.used += 1
        return reply(200,{"remaining":LIMIT - self.used})

def exercise(data):
    exact(data, "steps")
    steps = data["steps"]
    if not isinstance(steps,list) or not 1 <= len(steps) <= 8 or not all(isinstance(s,str) and s in ("ticket","other","post","wait") for s in steps) or steps.count("wait") > 1:
        raise ValueError("use up to eight known steps with at most one wait")
    checks, evidence = [], []
    with running(App()) as port:
        start = time.monotonic()
        for step in steps:
            if step == "wait":
                time.sleep(WINDOW + .15)
                continue
            method, target = ("POST","/ticket") if step == "post" else ("GET","/other" if step == "other" else "/ticket")
            status, value, headers = send(port,method,target)
            checks.append({"step":step,"status":status,"remaining":value.get("remaining"),"retry_after_present":"retry-after" in headers})
            evidence.append({"elapsed_seconds":round(time.monotonic()-start,3),"method":method,"path":target,
                             "status":status,"body":value,"retry_after":headers.get("retry-after")})
    return {"checks":checks,"evidence":evidence,"requests_sent":len(checks)}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, App, exercise))
