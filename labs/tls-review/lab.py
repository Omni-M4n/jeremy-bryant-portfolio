"""Offline fictional practice: TLS certificate review."""

from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = 'tls-review'


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


from datetime import datetime, timezone

LIMITATIONS = ['Certificate fields and a supplied chain report are synthetic; no signature, chain, revocation, protocol or cipher verification is performed.', 'Only ASCII DNS SAN names and a single leftmost wildcard are modelled; a matching name does not establish application safety.']


def instant(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value),
            "timestamps must be UTC YYYY-MM-DDTHH:MM:SSZ")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise ValueError("invalid calendar time") from error


def matches(host, name):
    host, name = host.lower(), name.lower()
    if name.startswith("*."):
        return len(host.split(".")) == len(name.split(".")) and host.split(".")[1:] == name.split(".")[1:]
    return host == name


def analyse(case):
    question(case)
    require(case["artifacts"] == {}, "this lab reads decoded JSON fields only")
    data = case["data"]
    fields(data, "evaluation_time renew_within_days certificates", "data")
    now = instant(data["evaluation_time"])
    window = integer(data["renew_within_days"], 0, 365, "renewal window") * 86400
    decisions, observations = {}, []
    for cert in items(data["certificates"], "certificates"):
        fields(cert, "id requested_host dns_names not_before not_after chain_report", "certificate")
        key = identifier(cert["id"])
        require(key not in decisions, "duplicate certificate ID")
        host = domain(cert["requested_host"])
        names = [domain(n, wildcard=True) for n in items(cert["dns_names"], "DNS SAN names", 0, 20)]
        unique(names, "DNS SAN name")
        start, end = instant(cert["not_before"]), instant(cert["not_after"])
        require(start <= end, "certificate validity interval is reversed")
        enumeration(cert["chain_report"], {"verified", "failed", "unverified"}, "supplied chain report")
        remaining = int((end - now).total_seconds())
        name_match = any(matches(host, name) for name in names)
        issues = []
        if now < start:
            issues.append("not-yet-valid")
        elif now > end:
            issues.append("expired")
        if not name_match:
            issues.append("hostname-mismatch")
        if cert["chain_report"] != "verified":
            issues.append("chain-" + cert["chain_report"])
        if start <= now <= end and remaining <= window:
            issues.append("renewal-due")
        decisions[key] = "|".join(issues) if issues else "fields-and-reported-chain-pass"
        observations.append(f"{key}: seconds-until-notAfter={remaining}; SAN-match={str(name_match).lower()}; supplied-chain={cert['chain_report']}.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITATIONS.copy()}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
