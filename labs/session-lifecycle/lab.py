"""Short-lived fictional sessions. Tokens stay only in process memory."""
from http.cookies import CookieError, SimpleCookie
from pathlib import Path
import json
import secrets
import time
from practice import exact, main, reply, running, send, strict_json

ROOT = Path(__file__).resolve().parent
LAB_ID = "session-lifecycle"
TTL = 2.0

class App:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.sessions = {}

    def __call__(self, request):
        cookie = SimpleCookie()
        try:
            cookie.load(request.headers.get("cookie", ""))
        except CookieError:
            return reply(400, {"error": "invalid-request"})
        token = cookie["training_session"].value if "training_session" in cookie else ""
        now = self.clock()
        self.sessions = {key: deadline for key, deadline in self.sessions.items() if now < deadline}
        if request.path == "/login" and request.method == "POST":
            if request.headers.get("content-type") != "application/json":
                return reply(415, {"error": "json-required"})
            value = strict_json(request.body)
            exact(value, "account password")
            if value != {"account": "reader", "password": "training-only"}:
                return reply(401, {"state": "signed-out"})
            self.sessions.pop(token, None)
            token = secrets.token_urlsafe(24)
            self.sessions[token] = now + TTL
            return reply(200, {"state": "signed-in", "lifetime_seconds": TTL},
                         {"Set-Cookie": f"training_session={token}; Path=/; HttpOnly; SameSite=Strict"})
        if request.path == "/profile" and request.method == "GET":
            return reply(200 if token in self.sessions else 401,
                         {"state": "signed-in" if token in self.sessions else "signed-out"})
        if request.path == "/logout" and request.method == "POST":
            self.sessions.pop(token, None)
            return reply(200, {"state": "signed-out"},
                         {"Set-Cookie": "training_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict"})
        return reply(404, {"error": "route"})

def exercise(data):
    exact(data, "steps")
    steps = data["steps"]
    if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
        raise ValueError("use 1-8 steps")
    allowed = {"login", "wrong-login", "profile", "logout", "wait", "old-profile"}
    if any(step not in allowed for step in steps if isinstance(step, str)) or not all(isinstance(s, str) for s in steps):
        raise ValueError("unknown step")
    if steps.count("wait") > 1:
        raise ValueError("at most one short wait")
    checks, evidence = [], []
    current = old = ""
    with running(App()) as port:
        started = time.monotonic()
        for index, step in enumerate(steps, 1):
            if step == "wait":
                time.sleep(TTL + .15)
                continue
            headers = {"Cookie": old if step == "old-profile" else current}
            method, path, body = "GET", "/profile", ""
            if step in {"login", "wrong-login"}:
                method, path = "POST", "/login"
                headers["Content-Type"] = "application/json"
                body = json.dumps({"account": "reader", "password": "training-only" if step == "login" else "different"})
            elif step == "logout":
                method, path = "POST", "/logout"
            status, value, response_headers = send(port, method, path, body, headers)
            if step == "login" and status == 200:
                old, current = current, response_headers["set-cookie"].split(";", 1)[0]
            elif step == "logout":
                old, current = current, ""
            checks.append({"step": step, "status": status, "state": value.get("state")})
            evidence.append({"row": index, "method": method, "path": path,
                             "cookie": "[redacted]" if headers["Cookie"] else "absent",
                             "status": status, "body": value,
                             "elapsed_seconds": round(time.monotonic() - started, 3)})
    return {"checks": checks, "evidence": evidence, "tokens_saved": False}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, App, exercise))
