"""Offline fictional practice: HTTP headers and cookies."""

from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = 'http-header-review'


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()),
            f"{label}: missing or unsupported fields")


def items(value, label, minimum=1, maximum=100):
    require(isinstance(value, list) and minimum <= len(value) <= maximum,
            f"{label}: expected {minimum}-{maximum} records")
    return value


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value),
            "record IDs must be short lowercase names")
    return value


def domain(value, wildcard=False):
    require(isinstance(value, str), "domain must be text")
    candidate = value.lower()
    if wildcard and candidate.startswith("*."):
        candidate = candidate[2:]
    require(len(candidate) <= 253 and candidate.endswith(".test") and
            all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part)
                for part in candidate.split(".")), "use ASCII .test domains only")
    return value.lower()


def integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, f"invalid {label}")
    return value


def boolean(value, label):
    require(type(value) is bool, f"{label} must be a boolean")


def enumeration(value, choices, label):
    require(isinstance(value, str) and value in choices, f"unsupported {label}")


def unique(values, label):
    require(len(values) == len(set(values)), f"duplicate {label}")


def question(case, extra=""):
    validate_case(case, LAB_ID)
    fields(case["context"], "question " + extra, "context")
    require(isinstance(case["context"]["question"], str) and
            case["context"]["question"].strip(), "question is required")


LIMITATIONS = ['Results compare supplied response excerpts with a fictional application policy, not with every browser rule or security requirement.', 'The narrow parser rejects folding, duplicate singleton fields and unsupported cookie/CSP/HSTS forms; no browser, server or network is used.']
TOKEN = re.compile(r"[A-Za-z0-9!#$%&'*+.^_`|~-]+\Z")


def headers(raw):
    require(isinstance(raw, str) and 0 < len(raw) <= 20000 and "\r" not in raw,
            "headers must be bounded LF text")
    result = {}
    for line in raw.rstrip("\n").split("\n"):
        require(line and not line[0].isspace() and ":" in line, "empty, folded or malformed header")
        name, value = line.split(":", 1)
        require(TOKEN.fullmatch(name) is not None, "invalid header name")
        value = value.strip(" ")
        require(value and all(32 <= ord(c) <= 126 for c in value), "header value must be printable ASCII")
        name = name.lower()
        require(name == "set-cookie" or name not in result, "duplicate singleton header")
        result.setdefault(name, []).append(value)
    return result


def semicolons(value):
    parts = [p.strip() for p in value.split(";")]
    require(all(parts), "empty directive is unsupported")
    return parts


def parse_hsts(value):
    found = {}
    for part in semicolons(value):
        if part.lower() == "includesubdomains":
            name, amount = "includesubdomains", True
        else:
            match = re.fullmatch(r"max-age=([0-9]+)", part, re.IGNORECASE)
            require(match is not None, "unsupported HSTS directive")
            name, amount = "max-age", integer(int(match[1]), 0, 2147483647, "HSTS duration")
        require(name not in found, "duplicate HSTS directive")
        found[name] = amount
    require("max-age" in found, "HSTS requires max-age")
    return found["max-age"]


def parse_csp(value):
    found = {}
    for part in semicolons(value):
        pieces = part.split()
        require(len(pieces) == 2 and pieces[0].lower() in {"default-src", "frame-ancestors"}
                and pieces[1] in {"'self'", "'none'"}, "CSP subset supports one self/none source per known directive")
        name = pieces[0].lower()
        require(name not in found, "duplicate CSP directive")
        found[name] = pieces[1]
    return found


def parse_cookie(value):
    parts = semicolons(value)
    require("=" in parts[0], "cookie needs a name/value pair")
    name, cookie_value = parts[0].split("=", 1)
    require(TOKEN.fullmatch(name) is not None and re.fullmatch(r"[A-Za-z0-9_-]*", cookie_value),
            "cookie subset uses token names and simple values")
    attrs = {}
    for part in parts[1:]:
        key, separator, val = part.partition("=")
        key = key.lower()
        require(key in {"secure", "httponly", "samesite", "path"} and key not in attrs, "unsupported or duplicate cookie attribute")
        if key in {"secure", "httponly"}:
            require(not separator, "cookie flag must not have a value")
            attrs[key] = True
        elif key == "path":
            require(separator and val == "/", "cookie subset supports Path=/ only")
            attrs[key] = val
        else:
            require(separator and val.lower() in {"lax", "strict", "none"}, "invalid SameSite value")
            attrs[key] = val.lower()
    return name, attrs


def parse_cache(value):
    found = set()
    for part in value.split(","):
        part = part.strip().lower()
        require(part in {"no-store", "private", "public", "no-cache"} or
                re.fullmatch(r"max-age=[0-9]+", part), "unsupported Cache-Control directive")
        name = part.split("=", 1)[0]
        require(name not in found, "duplicate cache directive")
        found.add(name)
    return found


def rendered(responses):
    return "\n".join(f"[{r['id']}] scheme={r['scheme']}\n{r['headers']}" for r in responses)


def analyse(case):
    question(case)
    fields(case["data"], "requirements responses", "data")
    policy = case["data"]["requirements"]
    fields(policy, "hsts_min_seconds frame_ancestors session_cookie cookie_samesite", "requirements")
    minimum = integer(policy["hsts_min_seconds"], 1, 2147483647, "minimum HSTS duration")
    enumeration(policy["frame_ancestors"], {"'none'", "'self'"}, "frame policy")
    require(isinstance(policy["session_cookie"], str) and TOKEN.fullmatch(policy["session_cookie"]), "invalid session cookie name")
    enumeration(policy["cookie_samesite"], {"Lax", "Strict"}, "required SameSite value")
    responses = items(case["data"]["responses"], "responses")
    decisions, observations = {}, []
    for response in responses:
        fields(response, "id scheme is_html requires_session private_data headers", "response")
        key = identifier(response["id"])
        require(key not in decisions, "duplicate response ID")
        enumeration(response["scheme"], {"http", "https"}, "scheme")
        for flag in ("is_html", "requires_session", "private_data"):
            boolean(response[flag], flag)
        parsed = headers(response["headers"])
        hsts = parse_hsts(parsed["strict-transport-security"][0]) if "strict-transport-security" in parsed else None
        csp = parse_csp(parsed["content-security-policy"][0]) if "content-security-policy" in parsed else {}
        cache = parse_cache(parsed["cache-control"][0]) if "cache-control" in parsed else set()
        cookies = {}
        for value in parsed.get("set-cookie", []):
            name, attrs = parse_cookie(value)
            require(name not in cookies, "duplicate cookie name")
            cookies[name] = attrs
        gaps = []
        if response["scheme"] != "https":
            gaps.append("https-required")
        elif hsts is None or hsts < minimum:
            gaps.append("hsts-duration")
        if parsed.get("x-content-type-options", [""])[0].lower() != "nosniff":
            gaps.append("nosniff")
        if response["is_html"] and csp.get("frame-ancestors") != policy["frame_ancestors"]:
            gaps.append("frame-ancestors")
        if response["private_data"] and "no-store" not in cache:
            gaps.append("cache-no-store")
        if response["requires_session"]:
            cookie = cookies.get(policy["session_cookie"])
            if cookie is None:
                gaps.append("session-cookie")
            else:
                for flag in ("secure", "httponly"):
                    if not cookie.get(flag):
                        gaps.append("cookie-" + flag)
                if cookie.get("samesite") != policy["cookie_samesite"].lower():
                    gaps.append("cookie-samesite")
        decisions[key] = "requirement-gaps:" + ",".join(gaps) if gaps else "meets-supplied-requirements"
        observations.append(f"{key}: scheme={response['scheme']}; HSTS-max-age={hsts if hsts is not None else 'absent'}; gaps={','.join(gaps) if gaps else 'none'}.")
    require(case["artifacts"] == {"headers.txt": rendered(responses)}, "headers.txt must mirror authoritative JSON responses")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITATIONS.copy()}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
