"""Offline fictional practice: Email identity and message triage."""

from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = 'email-triage'


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


LIMITATIONS = ['Receiver trust is supplied out of band for this exercise; an Authentication-Results header or matching relay name alone is not proof.', 'SPF authorises a sending domain context; DMARC relates authenticated domains to From. Neither authenticates a person or guarantees harmless content.', 'Only decoded strict domain alignment is checked; no DNS, signature, ARC, relaxed alignment, attachment or URL-content analysis occurs.']


def rendered(messages):
    lines = []
    for m in messages:
        lines += [f"[{m['id']}]", f"From: curator@{m['from_domain']}",
                  f"Reply-To: desk@{m['reply_to_domain']}"]
        for a in m["authentication_results"]:
            signing = "" if a["dkim_domain"] is None else f" header.d={a['dkim_domain']}"
            lines.append(f"Authentication-Results: {a['authserv_id']}; spf={a['spf']} smtp.mailfrom={a['mailfrom_domain']}; dkim={a['dkim']}{signing}; dmarc={a['dmarc']} header.from={m['from_domain']} (record {a['id']})")
        lines.append("Link domains: " + ", ".join(m["link_domains"]))
        lines.append("")
    return "\n".join(lines)


def analyse(case):
    question(case, "trusted_receiving_relay")
    trust = case["context"]["trusted_receiving_relay"]
    fields(trust, "authserv_id trusted_record_ids alignment provenance", "receiver context")
    relay = domain(trust["authserv_id"])
    require(trust["alignment"] == "strict" and trust["provenance"] == "fictional-receiver-export", "unsupported trust context")
    trusted_ids = [identifier(k) for k in items(trust["trusted_record_ids"], "trusted record IDs", 0)]
    unique(trusted_ids, "trusted record ID")
    fields(case["data"], "messages", "data")
    messages = items(case["data"]["messages"], "messages")
    decisions, observations, all_ids = {}, [], set()
    for m in messages:
        fields(m, "id expected_sender_domain from_domain reply_to_domain link_domains authentication_results", "message")
        key = identifier(m["id"])
        require(key not in decisions, "duplicate message ID")
        expected, sender, reply = [domain(m[field]) for field in ("expected_sender_domain", "from_domain", "reply_to_domain")]
        links = [domain(d) for d in items(m["link_domains"], "link domains", 0, 20)]
        unique(links, "link domain")
        accepted = []
        for a in items(m["authentication_results"], "authentication records", 0, 10):
            fields(a, "id authserv_id spf mailfrom_domain dkim dkim_domain dmarc", "authentication record")
            record = identifier(a["id"])
            require(record not in all_ids, "duplicate authentication record ID")
            all_ids.add(record)
            authority = domain(a["authserv_id"])
            for name in ("spf", "dkim", "dmarc"):
                enumeration(a[name], {"pass", "fail", "none", "temperror"}, name + " result")
            mailfrom = domain(a["mailfrom_domain"])
            if a["dkim"] == "none":
                require(a["dkim_domain"] is None, "no DKIM signature uses null signing domain")
                signing = None
            else:
                signing = domain(a["dkim_domain"])
            if record in trusted_ids:
                require(authority == relay, "trusted record names a different receiving relay")
                aligned_pass = (a["spf"] == "pass" and mailfrom == sender) or (a["dkim"] == "pass" and signing == sender)
                require(a["dmarc"] != "pass" or aligned_pass, "trusted DMARC pass lacks an aligned passing mechanism")
                require(a["dmarc"] != "fail" or not aligned_pass, "trusted DMARC fail contradicts aligned passing mechanism")
                accepted.append(a)
        require(len(accepted) <= 1, "ambiguous multiple trusted results for one message")
        mismatches = []
        if sender != expected:
            mismatches.append("from-not-expected")
        if reply != sender:
            mismatches.append("reply-domain-differs")
        if any(link != sender for link in links):
            mismatches.append("link-domain-differs")
        if not accepted:
            decision, auth = "authentication-unverified", "no trusted receiver result"
        else:
            a = accepted[0]
            auth = f"trusted {a['id']}: SPF={a['spf']}, DKIM={a['dkim']}, DMARC={a['dmarc']}"
            if a["dmarc"] == "fail":
                decision = "domain-authentication-failed"
            elif a["dmarc"] != "pass":
                decision = "domain-authentication-unresolved"
            elif mismatches:
                decision = "authenticated-domain-with-mismatch"
            else:
                decision = "authenticated-domain-review-content"
        decisions[key] = decision
        observations.append(f"{key}: {auth}; mismatches={','.join(mismatches) if mismatches else 'none'}.")
    require(set(trusted_ids) <= all_ids, "receiver context names an absent authentication record")
    require(case["artifacts"] == {"headers.txt": rendered(messages)}, "headers.txt must mirror authoritative decoded JSON")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITATIONS.copy()}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
