#!/usr/bin/env python3
"""Loopback-only, fictional object-access exercise. See README.md for contract."""
from __future__ import annotations

import argparse
import copy
import html
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

ROOT = Path(__file__).absolute().parent
HOST = "127.0.0.1"
ACCOUNTS = {"ada": "Ada Finch", "ben": "Ben Reed"}
SCENARIOS = {
    "guided": {
        "101": {"owner": "ada", "title": "Paper lantern", "note": "Fictional order: 2 blue paper lanterns."},
        "102": {"owner": "ben", "title": "Cardboard moon", "note": "Fictional order: 1 silver cardboard moon."},
        "103": {"owner": "ada", "title": "Felt clouds", "note": "Fictional order: 4 white felt clouds."},
    },
    "changed": {
        "101": {"owner": "ben", "title": "Paper lantern", "note": "Fictional reassignment: Ben now owns this order."},
        "102": {"owner": "ada", "title": "Cardboard moon", "note": "Fictional reassignment: Ada now owns this order."},
        "103": {"owner": "ben", "title": "Felt clouds", "note": "Fictional reassignment: Ben owns a second order."},
    },
}
WORKSHEET = """# Manual Burp evidence worksheet

Status: pending hands-on completion. Software tests do not fill this worksheet.
Date / learner:
Mode / scenario / URL:
Burp version:
My prediction before sending:
Scope confirmed as the single loopback URL:
Intercepted request number in Proxy history:

Record one row per manual request. Keep a stable account cookie within each
comparison; label it Ada or Ben instead of pasting the token into these notes.

| Mode | Account | Requested ID | Expected status | Actual status | Body evidence / owner | Burp evidence file |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

Capture: request line, Host, account label, response status, X-Lab-Mode,
X-Lab-Scenario and relevant JSON body. Save screenshots or copied request and
response text into this run folder. Tokens are disposable lab tokens only.

Explain:
1. Which one field changed between the own and cross-user requests?
2. What evidence identifies the requester and the record's rightful owner?
3. Why is a hidden link insufficient? Where must the check occur?
4. Did both accounts keep necessary access after the fix?
5. How did unknown ID, invalid ID and missing session differ from denial?
6. What is NOT demonstrated by this toy application or by its software tests?
7. State one next test and why it would help.

Teach-back reviewer / questions / corrections:
Later recall date / unaided explanation:
Handover: I manually tested [scope] using [actions]. I observed [evidence].
The result supports [bounded conclusion]. I have not yet tested [limits].
"""


def reject_links(path: Path) -> None:
    """Reject symlinks and Windows junction/reparse components without resolving."""
    path = path.absolute()
    for component in [*reversed(path.parents), path]:
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Linked/reparse paths are not allowed: " + str(component))


def create_run(out: str, root: Path = ROOT) -> Path:
    """Only a fresh direct run child; no absolute paths, traversal or overwrite."""
    normalized = out.replace("\\", "/")
    if not re.fullmatch(r"run/[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", normalized):
        raise ValueError("--out must be a fresh direct child such as run/attempt-01")
    name = normalized.split("/")[1]
    if name.upper() in {"CON", "PRN", "AUX", "NUL", *("COM" + str(i) for i in range(1, 10)), *("LPT" + str(i) for i in range(1, 10))}:
        raise ValueError("Reserved output name")
    root = root.absolute()
    reject_links(root)
    run = root / "run"
    reject_links(run)
    run.mkdir(exist_ok=True)
    dest = run / name
    reject_links(dest)
    dest.mkdir(exist_ok=False)
    return dest


def write_new(path: Path, value: str) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(value)


class LabServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True
    block_on_close = True

    def __init__(self, mode: str, scenario: str, port: int, run: Path):
        if mode not in ("vulnerable", "fixed") or scenario not in SCENARIOS:
            raise ValueError("Unsupported mode or scenario")
        if type(port) is not int or not (port == 0 or 1024 <= port <= 65535):
            raise ValueError("Port must be 1024..65535 (0 is for software tests only)")
        reject_links(run)
        self.mode = mode
        self.scenario = scenario
        self.records = copy.deepcopy(SCENARIOS[scenario])
        self.sessions = {secrets.token_hex(24): account for account in ACCOUNTS}
        self.event_lock = threading.Lock()
        self.events = None
        super().__init__((HOST, port), Handler)
        try:
            self.events = (run / "events.jsonl").open("x", encoding="utf-8", newline="\n")
        except Exception:
            super().server_close()
            raise
        self.origin = "http://" + HOST + ":" + str(self.server_port)
        self.host_header = HOST + ":" + str(self.server_port)

    def get_request(self):
        request, address = super().get_request()
        request.settimeout(3)
        return request, address

    def record(self, status: int, route: str, account: str | None, object_id: str | None):
        with self.event_lock:
            self.events.write(json.dumps({
                "time_utc": datetime.now(timezone.utc).isoformat(),
                "mode": self.mode, "scenario": self.scenario,
                "route": route, "account": account, "object_id": object_id,
                "status": status,
            }) + "\n")
            self.events.flush()

    def server_close(self):
        super().server_close()
        if self.events:
            self.events.close()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "FictionalOrderLab/1"
    sys_version = ""

    def log_message(self, *_args):
        pass

    def send_error(self, code, message=None, explain=None):
        # Do not reflect parser input, filesystem paths or Python exceptions.
        self.respond(code, {"error": "Unsupported or malformed HTTP request"})

    def respond(self, status, body, content_type="application/json; charset=utf-8", extra=None):
        data = (json.dumps(body, indent=2) if isinstance(body, dict) else body).encode("utf-8")
        self.send_response(status)
        for key, value in {
            "Content-Type": content_type, "Content-Length": str(len(data)),
            "Cache-Control": "no-store", "Connection": "close",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
            "X-Lab-Mode": self.server.mode, "X-Lab-Scenario": self.server.scenario,
            **(extra or {}),
        }.items():
            self.send_header(key, value)
        self.end_headers()
        self.close_connection = True
        if self.command != "HEAD":
            self.wfile.write(data)
        self.server.record(status, getattr(self, "route", "rejected"),
                           getattr(self, "account", None), getattr(self, "object_id", None))

    def boundary(self) -> bool:
        self.route, self.account, self.object_id = "rejected", None, None
        hosts = self.headers.get_all("Host", [])
        origins = self.headers.get_all("Origin", [])
        if hosts != [self.server.host_header]:
            self.respond(421, {"error": "Use only the exact printed loopback Host"})
            return False
        if origins and origins != [self.server.origin]:
            self.respond(403, {"error": "Unexpected Origin"})
            return False
        if self.headers.get_all("Transfer-Encoding"):
            self.respond(400, {"error": "Transfer-Encoding is unsupported"})
            return False
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) > 1 or (lengths and not re.fullmatch(r"[0-9]{1,4}", lengths[0])):
            self.respond(400, {"error": "Invalid Content-Length"})
            return False
        if len(self.headers.get_all("Cookie", [])) > 1:
            self.respond(400, {"error": "Duplicate Cookie header"})
            return False
        if not self.path.startswith("/") or self.path.startswith("//") or "#" in self.path:
            self.respond(400, {"error": "Use an origin-form request path"})
            return False
        if self.command == "GET" and lengths and int(lengths[0]) != 0:
            self.respond(400, {"error": "GET bodies are unsupported"})
            return False
        return True

    def identify(self) -> str | None:
        raw = self.headers.get("Cookie", "")
        if len(raw) > 512:
            return None
        values = [part.strip().split("=", 1)[1] for part in raw.split(";")
                  if part.strip().startswith("lab_session=")]
        return self.server.sessions.get(values[0]) if len(values) == 1 else None

    def do_GET(self):
        if not self.boundary():
            return
        self.account = self.identify()
        if self.path == "/":
            self.route = "home"
            selected = ACCOUNTS.get(self.account, "None selected")
            links = "".join('<li><a href="/api/orders/' + oid + '">Order ' + oid + ": "
                            + html.escape(row["title"]) + "</a></li>"
                            for oid, row in self.server.records.items() if row["owner"] == self.account)
            body = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Lantern orders: training</title>
<h1>Lantern orders: fictional training application</h1>
<p>All records and accounts are invented. This is an access-control exercise.</p>
<p><strong>Mode: """ + self.server.mode.upper() + "</strong> | Scenario: " + self.server.scenario + """</p>
<p>Training simplification: select either fictional account without a password.
This is not real authentication or a private account service.</p>
<form action="/session" method="post"><label>Training account
<select name="account"><option value="ada">Ada Finch</option><option value="ben">Ben Reed</option></select>
</label><button type="submit">Select account</button></form>
<p>Selected account: <strong>""" + selected + "</strong></p><h2>Your order links</h2><ul>" + links + """</ul>
<p>Only your links appear here. Does the server enforce the same rule?</p>
<p>Return here with the browser Back button after opening a JSON order.</p>
</html>"""
            self.respond(200, body, "text/html; charset=utf-8")
            return
        if self.path == "/favicon.ico":
            self.route = "favicon"
            self.respond(204, "")
            return
        if self.path.startswith("/api/orders/"):
            self.route = "order"
            if not re.fullmatch(r"/api/orders/[1-9][0-9]{2}", self.path):
                self.respond(400, {"error": "Order ID must be exactly three digits, starting 1..9; no query string"})
                return
            self.object_id = self.path.rsplit("/", 1)[1]
            if self.account is None:
                self.respond(401, {"error": "Select a training account first"})
                return
            row = self.server.records.get(self.object_id)
            if row is None:
                self.respond(404, {"error": "No fictional order with that ID"})
                return
            # The vulnerable mode deliberately omits this server-side ownership check.
            if self.server.mode == "fixed" and row["owner"] != self.account:
                self.respond(403, {"error": "This order belongs to another training account"})
                return
            self.respond(200, {"synthetic": True, "id": self.object_id, **row})
            return
        self.respond(404, {"error": "No such lab route"})

    def do_POST(self):
        if not self.boundary():
            return
        if self.path != "/session":
            self.respond(404, {"error": "No such lab route"})
            return
        self.route = "session"
        if self.headers.get_all("Origin", []) != [self.server.origin]:
            self.respond(403, {"error": "Account selection requires the same Origin"})
            return
        if self.headers.get_all("Content-Type", []) != ["application/x-www-form-urlencoded"]:
            self.respond(415, {"error": "Use the account selection form"})
            return
        length = self.headers.get("Content-Length")
        if length is None:
            self.respond(411, {"error": "Content-Length required"})
            return
        if int(length) > 128:
            self.respond(413, {"error": "Account form is too large"})
            return
        try:
            raw = self.rfile.read(int(length)).decode("ascii")
            form = parse_qs(raw, keep_blank_values=True, strict_parsing=True, max_num_fields=2)
        except (ValueError, UnicodeDecodeError):
            self.respond(400, {"error": "Invalid account form"})
            return
        if set(form) != {"account"} or len(form["account"]) != 1 or form["account"][0] not in ACCOUNTS:
            self.respond(400, {"error": "Choose exactly one fictional account"})
            return
        self.account = form["account"][0]
        token = next(key for key, value in self.server.sessions.items() if value == self.account)
        self.respond(303, {"selected": self.account}, extra={
            "Location": "/", "Set-Cookie": "lab_session=" + token + "; Path=/; HttpOnly; SameSite=Strict"})

    def unsupported(self):
        if self.boundary():
            self.respond(405, {"error": "Only GET and POST are supported"}, extra={"Allow": "GET, POST"})

    do_HEAD = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_CONNECT = do_TRACE = unsupported


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Run the fictional app on 127.0.0.1 only; Ctrl+C stops it")
    serve.add_argument("--mode", choices=("vulnerable", "fixed"), required=True)
    serve.add_argument("--scenario", choices=tuple(SCENARIOS), default="guided")
    serve.add_argument("--port", type=int, default=8765, help="Loopback port 1024..65535; default 8765")
    serve.add_argument("--out", required=True, help="Fresh direct child of this lab's run/, e.g. run/attempt-01")
    sub.add_parser("cases", help="Print the fictional owner roster for each scenario; no writes")
    args = parser.parse_args(argv)
    if args.command == "cases":
        print(json.dumps(SCENARIOS, indent=2))
        return 0
    try:
        if not 1024 <= args.port <= 65535:
            raise ValueError("--port must be 1024..65535")
        run = create_run(args.out)
        write_new(run / "worksheet.md", WORKSHEET)
        write_new(run / "roster.json", json.dumps(SCENARIOS[args.scenario], indent=2) + "\n")
        with LabServer(args.mode, args.scenario, args.port, run) as server:
            info = {"lab": "burp-access-control", "synthetic": True, "mode": args.mode,
                    "scenario": args.scenario, "url": server.origin + "/", "pid": os.getpid(),
                    "manual_burp_completion": "pending", "authentication": "fictional account selector only"}
            write_new(run / "run.json", json.dumps(info, indent=2) + "\n")
            print(json.dumps({**info, "output": str(run), "stop": "Ctrl+C in this terminal"}), flush=True)
            try:
                server.serve_forever(poll_interval=0.2)
            except KeyboardInterrupt:
                print("Stopped. Notes and synthetic request events remain in " + str(run), flush=True)
        return 0
    except (OSError, ValueError) as exc:
        print("Lab error: " + str(exc) + ". Use a fresh run name after correcting the problem.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
