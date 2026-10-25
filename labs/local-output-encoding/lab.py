"""Harmless markers in an HTML text context, or as plain text."""
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from practice import exact, html_reply, main, reply, running, send
ROOT = Path(__file__).resolve().parent
LAB_ID = "local-output-encoding"
MARKERS = {"hello", "<b>LOCAL MARKER</b>", "A &amp; B"}

class App:
    def __call__(self, request):
        target = urlsplit(request.path)
        if request.method != "GET":
            return reply(405, {"error":"method"})
        if target.path == "/":
            links = []
            for marker in sorted(MARKERS):
                for mode in ("reflect", "encoded", "text"):
                    url = "/" + mode + "?" + urlencode({"marker":marker})
                    links.append(f'<li><a href="{escape(url, quote=True)}">{mode}: {escape(marker)}</a></li>')
            return html_reply("<!doctype html><title>Marker desk</title><h1>Marker desk</h1><ul>" + "".join(links) + "</ul>")
        if target.path not in {"/reflect", "/encoded", "/text"}:
            return reply(404, {"error":"route"})
        fields = parse_qs(target.query, strict_parsing=True, max_num_fields=1)
        if set(fields) != {"marker"} or len(fields["marker"]) != 1 or fields["marker"][0] not in MARKERS:
            raise ValueError("only supplied harmless markers are allowed")
        marker = fields["marker"][0]
        headers = {"Content-Security-Policy":"default-src 'none'; base-uri 'none'; form-action 'none'"}
        if target.path == "/text":
            return 200, marker.encode(), {**headers,"Content-Type":"text/plain; charset=utf-8"}
        shown = escape(marker, quote=True) if target.path == "/encoded" else marker
        page = "<!doctype html><title>Marker desk</title><p id=marker>" + shown + "</p>"
        return 200, page.encode(), {**headers,"Content-Type":"text/html; charset=utf-8"}

def exercise(data):
    exact(data, "marker modes")
    if not isinstance(data["marker"], str) or data["marker"] not in MARKERS:
        raise ValueError("unsupported marker")
    if not isinstance(data["modes"], list) or not 1 <= len(data["modes"]) <= 3 or any(m not in ("reflect","encoded","text") for m in data["modes"]):
        raise ValueError("unsupported mode list")
    checks = []
    with running(App()) as port:
        for mode in data["modes"]:
            status, value, headers = send(port, "GET", "/" + mode + "?" + urlencode({"marker":data["marker"]}))
            checks.append({"mode":mode,"status":status,"content_type":headers["content-type"],"response":value})
    return {"checks":checks,"evidence":{"raw_http_responses":checks,"browser_rendering":"not-observed-by-this-script"}}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, App, exercise))
