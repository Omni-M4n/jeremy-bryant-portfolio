"""Small loopback transport and practice-file commands; Python 3.10+."""
import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import re
import threading
import time

@dataclass
class Request:
    method: str
    path: str
    headers: dict
    body: bytes
    origin: str

def reply(status, value, headers=None):
    return status, json.dumps(value, ensure_ascii=True).encode(), {
        "Content-Type": "application/json; charset=utf-8", **(headers or {})}

def html_reply(text):
    return 200, text.encode(), {"Content-Type": "text/html; charset=utf-8"}

def handler_for(app):
    class Handler(BaseHTTPRequestHandler):
        # no request paths or cookies are printed to the terminal
        def log_message(self, *args):
            pass

        def setup(self):
            super().setup()
            self.connection.settimeout(2)

        def dispatch(self):
            origin = f"http://127.0.0.1:{self.server.server_port}"
            try:
                if self.headers.get_all("Host", []) != [origin[7:]]:
                    raise ValueError("host")
                if any(len(self.headers.get_all(name, [])) > 1 for name in ("Content-Type", "Cookie", "Origin")):
                    raise ValueError("duplicate request header")
                if self.headers.get("Transfer-Encoding"):
                    raise ValueError("framing")
                lengths = self.headers.get_all("Content-Length", [])
                if len(lengths) > 1 or (lengths and not re.fullmatch(r"[0-9]{1,5}", lengths[0])):
                    raise ValueError("length")
                size = int(lengths[0]) if lengths else 0
                if size > 4096:
                    status, body, headers = reply(413, {"error": "body-too-large"})
                elif self.command not in {"GET", "POST"}:
                    status, body, headers = reply(405, {"error": "method"}, {"Allow": "GET, POST"})
                elif len(self.path) > 2048 or not self.path.startswith("/") or self.path.startswith("//"):
                    raise ValueError("path")
                else:
                    body_in = self.rfile.read(size)
                    if len(body_in) != size:
                        raise ValueError("short-body")
                    request = Request(self.command, self.path,
                                      {k.lower(): v for k, v in self.headers.items()}, body_in, origin)
                    status, body, headers = app(request)
            except (ValueError, UnicodeError):
                status, body, headers = reply(400, {"error": "invalid-request"})
            except Exception:
                # a learner sees a bounded error, never a traceback or local path
                status, body, headers = reply(500, {"error": "internal-error"})
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Connection", "close")
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_HEAD = dispatch
    return Handler

@contextmanager
def running(app, port=0):
    if type(port) is not int or not (port == 0 or 1024 <= port <= 65535):
        raise ValueError("use port 0 or 1024-65535")
    server = HTTPServer(("127.0.0.1", port), handler_for(app))
    worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .02}, daemon=True)
    worker.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)

def send(port, method, path, body="", headers=None):
    connection = HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        connection.request(method, path, body.encode() if isinstance(body, str) else body, headers or {})
        response = connection.getresponse()
        raw = response.read().decode("utf-8")
        fields = {k.lower(): v for k, v in response.getheaders()}
        value = json.loads(raw) if fields.get("content-type", "").startswith("application/json") else raw
        return response.status, value, fields
    finally:
        connection.close()

def exact(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys.split()):
        raise ValueError("missing or unsupported fields")

def strict_json(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate JSON key")
            value[key] = item
        return value
    def constant(value):
        raise ValueError("non-standard JSON number")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)

def read_case(path, lab_id):
    if path.is_symlink() or getattr(path.stat(), "st_file_attributes", 0) & 1024 or path.stat().st_nlink > 1:
        raise ValueError("linked case files refused")
    if path.stat().st_size > 32768:
        raise ValueError("case is too large")
    value = strict_json(path.read_text(encoding="utf-8"))
    exact(value, "schema_version lab_id case_id title synthetic question data")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1 or value["synthetic"] is not True:
        raise ValueError("case version or synthetic flag")
    if value["lab_id"] != lab_id or value["case_id"] not in {"guided", "changed", "challenge"}:
        raise ValueError("case identity")
    if not all(isinstance(value[k], str) and value[k].strip() for k in ("title", "question")):
        raise ValueError("case text")
    return value

def safe_attempt(root, name, create=False):
    if not re.fullmatch(r"run/[a-z0-9][a-z0-9-]{0,39}", name):
        raise ValueError("use run/a-short-name")
    target = root / name
    for item in (root, root / "run", target):
        if item.exists() and (item.is_symlink() or getattr(item.stat(), "st_file_attributes", 0) & 1024):
            raise ValueError("linked practice paths refused")
    if create:
        target.parent.mkdir(exist_ok=True)
        target.mkdir(exist_ok=False)
    elif not target.is_dir():
        raise ValueError("prepare a fresh attempt first")
    return target

def save_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write("\n")

def main(root, lab_id, app_factory, exercise):
    parser = argparse.ArgumentParser(description="Fictional, loopback-only practice")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("cases")
    prep = sub.add_parser("prepare")
    prep.add_argument("--scenario", choices=["guided", "changed", "challenge"], required=True)
    prep.add_argument("--out", required=True)
    run = sub.add_parser("run")
    run.add_argument("--folder", required=True)
    sub.add_parser("verify")
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        if args.command == "cases":
            for name in ("guided", "changed", "challenge"):
                case = read_case(root / "fixtures" / (name + ".json"), lab_id)
                print(name + ": " + case["title"])
        elif args.command == "prepare":
            case = read_case(root / "fixtures" / (args.scenario + ".json"), lab_id)
            folder = safe_attempt(root, args.out, create=True)
            save_new(folder / "case.json", case)
            (folder / "notes.txt").write_text("Stage: first attempt\nPrediction and reason:\n\nObserved evidence:\n\nNext check:\n", encoding="utf-8")
            print("Prepared " + args.out + "; save a prediction in notes.txt before run.")
        elif args.command == "run":
            folder = safe_attempt(root, args.folder)
            if (folder / "evidence.json").exists():
                raise ValueError("evidence exists; preserve it and prepare a new attempt")
            case = read_case(folder / "case.json", lab_id)
            result = exercise(case["data"])
            save_new(folder / "evidence.json", result)
            print(json.dumps(result, indent=2))
        elif args.command == "verify":
            for name in ("guided", "changed", "challenge"):
                case = read_case(root / "fixtures" / (name + ".json"), lab_id)
                expected = json.loads((root / "reference" / (name + ".json")).read_text())
                actual = exercise(case["data"])
                if actual["checks"] != expected["checks"]:
                    raise ValueError(name + " reference differs: " + repr(actual["checks"]))
                print(name + ": reference checks passed")
        else:
            app = app_factory()
            with running(app, args.port) as port:
                print(f"Training only: http://127.0.0.1:{port} (Ctrl+C stops)", flush=True)
                if hasattr(app, "storage"):
                    print("Disposable upload directory: " + str(app.storage), flush=True)
                try:
                    while True:
                        time.sleep(.2)
                except KeyboardInterrupt:
                    pass
            if hasattr(app, "close"):
                app.close()
        return 0
    except (ValueError, OSError) as error:
        print("Stopped: " + str(error))
        return 2
