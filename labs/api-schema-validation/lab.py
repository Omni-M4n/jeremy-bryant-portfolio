"""A small JSON order API with explicit validation errors."""
from pathlib import Path
import json
from practice import exact, main, reply, running, send
ROOT = Path(__file__).resolve().parent
LAB_ID = "api-schema-validation"

def unique_pairs(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("duplicate JSON key")
        output[key] = value
    return output

def invalid_constant(value):
    raise ValueError("non-standard number")

def validate(value):
    exact(value, "name count")
    name, count = value["name"], value["count"]
    if not isinstance(name, str) or not 1 <= len(name) <= 20 or not name.strip() or any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in name):
        raise ValueError("name")
    if type(count) is not int or not 1 <= count <= 5:
        raise ValueError("count")
    return {"name":name,"count":count}

class App:
    def __call__(self, request):
        if request.path != "/order" or request.method != "POST":
            return reply(404, {"error":"route"})
        if len(request.body) > 256:
            return reply(413, {"error":"body-too-large"})
        if request.headers.get("content-type") != "application/json":
            return reply(415, {"error":"json-required"})
        try:
            value = json.loads(request.body.decode("utf-8"), object_pairs_hook=unique_pairs, parse_constant=invalid_constant)
        except (ValueError, UnicodeError):
            return reply(400, {"error":"invalid-json"})
        try:
            order = validate(value)
        except ValueError:
            return reply(422, {"error":"schema","rule":"name 1-20 characters; count integer 1-5; only these fields"})
        return reply(201, {"accepted":order})

def exercise(data):
    exact(data, "requests")
    if not isinstance(data["requests"], list) or not 1 <= len(data["requests"]) <= 6:
        raise ValueError("use 1-6 requests")
    for row in data["requests"]:
        exact(row, "body content_type")
        if not isinstance(row["body"], str) or len(row["body"].encode()) > 512 or row["content_type"] not in ("application/json", "text/plain"):
            raise ValueError("bounded body and supported content type required")
    checks = []
    with running(App()) as port:
        for row in data["requests"]:
            status, value, _ = send(port,"POST","/order",row["body"],{"Content-Type":row["content_type"]})
            checks.append({"status":status,"response":value})
    return {"checks":checks,"evidence":{"requests":data["requests"],"responses":checks}}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, App, exercise))
