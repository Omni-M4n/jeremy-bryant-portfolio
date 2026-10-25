"""Trace the request target, form encoding and selected headers."""
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
from practice import exact, main, reply, running, send
ROOT = Path(__file__).resolve().parent
LAB_ID = "http-request-construction"

def fields(text):
    if re.search(r"%(?![0-9A-Fa-f]{2})", text):
        raise ValueError("bad percent escape")
    return parse_qs(text, keep_blank_values=True, strict_parsing=True,
                    encoding="utf-8", errors="strict", max_num_fields=8)

class App:
    def __call__(self, request):
        target = urlsplit(request.path)
        if target.path != "/inspect" or target.fragment:
            return reply(404, {"error":"route"})
        if request.method == "GET" and request.body:
            return reply(400, {"error":"get-body-not-supported"})
        if request.method == "POST" and request.headers.get("content-type") != "application/x-www-form-urlencoded":
            return reply(415, {"error":"form-required"})
        body = request.body.decode("utf-8")
        return reply(200, {"method":request.method, "target":request.path,
                           "query":fields(target.query) if target.query else {},
                           "note":request.headers.get("x-note", ""),
                           "body":body, "form":fields(body) if body else {}})

def exercise(data):
    exact(data, "requests")
    rows = data["requests"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 5:
        raise ValueError("use 1-5 requests")
    for row in rows:
        exact(row, "method target body content_type note")
        if not all(isinstance(v, str) and len(v) <= 300 for v in row.values()):
            raise ValueError("bounded text required")
        if not row["target"].isascii() or any(ord(c) <= 32 or ord(c) == 127 for c in row["target"]):
            raise ValueError("encode spaces and non-ASCII text in the target; control characters are not allowed")
        target = urlsplit(row["target"])
        if (row["method"] not in {"GET", "POST"} or target.path != "/inspect"
                or target.scheme or target.netloc or '#' in row['target']):
            raise ValueError("unsupported plan route/method")
        if any(c in row["content_type"] + row["note"] for c in "\r\n"):
            raise ValueError("header newline")
    checks = []
    with running(App()) as port:
        for row in rows:
            status, body, _ = send(port, row["method"], row["target"], row["body"],
                                   {"Content-Type":row["content_type"], "X-Note":row["note"]})
            checks.append({"status":status, "response":body})
    return {"checks":checks, "evidence":{"sent":rows, "received":checks}}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, App, exercise))
