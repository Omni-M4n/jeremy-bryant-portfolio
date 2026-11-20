"""Assess supplied synthetic indicator metadata; never query or block anything."""

from __future__ import annotations

from datetime import datetime, timedelta
import ipaddress
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case


ROOT = Path(__file__).resolve().parent
LAB_ID = "indicator-quality"
ID = re.compile(r"[a-z][a-z0-9-]{0,39}\Z", re.ASCII)
TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z",
    re.ASCII,
)
DOMAIN_LABEL = re.compile(
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z",
    re.ASCII,
)
IPV4_TEXT = re.compile(r"[0-9.]{7,15}\Z", re.ASCII)
DOCUMENTATION_NETWORKS = tuple(
    ipaddress.IPv4Network(value)
    for value in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)
LIMITATIONS = (
    "All indicator values, records, metadata and conflict flags are synthetic and supplied. No lookup, reputation check, blocking action, external submission or attribution is performed.",
    "Source, confidence, scope, timestamps, expiry and conflict are supplied metadata; the helper does not verify provenance, source reliability, truth, independence or corroboration.",
    "Each row is assessed independently; the helper does not link records across sources or decide that two records describe the same activity.",
    "The seven-day review interval and 70 confidence threshold are local teaching choices, not STIX requirements or operational policy.",
)


def exact(value, fields, message="missing or unsupported fields"):
    require(isinstance(value, dict) and set(value) == set(fields), message)


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value) is not None,
            "use a lowercase fictional ID of at most 40 characters")


def question(value):
    require(isinstance(value, str) and 1 <= len(value) <= 200 and
            value == value.strip() and all(" " <= character <= "~" for character in value),
            "question must be 1-200 trimmed printable ASCII characters")


def moment(value):
    require(isinstance(value, str) and TIMESTAMP.fullmatch(value) is not None,
            "use a UTC timestamp with seconds and Z")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("use a real UTC calendar timestamp") from error


def domain(value):
    require(isinstance(value, str), "domain must be text")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("use a lowercase ASCII .test domain") from error
    labels = value.split(".")
    require(len(encoded) <= 253 and len(labels) >= 2 and labels[-1] == "test" and
            all(1 <= len(label) <= 63 and DOMAIN_LABEL.fullmatch(label) is not None
                for label in labels),
            "use a lowercase ASCII .test domain with valid 1-63 character labels")


def indicator(value, kind):
    require(kind in ("domain", "ipv4"), "indicator type must be domain or ipv4")
    if kind == "domain":
        domain(value)
        return
    require(isinstance(value, str) and IPV4_TEXT.fullmatch(value) is not None,
            "use an RFC 5737 documentation IPv4 address")
    try:
        address = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        raise ValueError("use an RFC 5737 documentation IPv4 address") from None
    require(any(address in network for network in DOCUMENTATION_NETWORKS),
            "use an RFC 5737 documentation IPv4 address")


def analyse(case):
    validate_case(case, LAB_ID)
    exact(case["context"], ["question"], "context must contain only question")
    question(case["context"]["question"])
    require(case["artifacts"] == {},
            "case.json is authoritative and this package has no extracted artifacts")

    data = case["data"]
    exact(data, ["as_of", "records"], "data must contain only as_of and records")
    as_of = moment(data["as_of"])
    rows = data["records"]
    require(isinstance(rows, list) and 1 <= len(rows) <= 30,
            "provide 1-30 indicator records")

    record_ids = set()
    evidence_ids = set()
    decisions = {}
    observations = []
    for row in rows:
        exact(row, [
            "id", "value", "type", "source", "confidence", "observed_at",
            "reported_at", "valid_until", "scope", "contradicted", "evidence_id",
        ], "indicator record has missing or unsupported fields")
        record_id = row["id"]
        evidence_id = row["evidence_id"]
        identifier(record_id)
        identifier(evidence_id)
        require(record_id not in record_ids, "duplicate indicator record ID")
        require(evidence_id not in evidence_ids, "duplicate evidence ID")
        record_ids.add(record_id)
        evidence_ids.add(evidence_id)

        indicator(row["value"], row["type"])
        require(row["source"] in ("direct", "copied"),
                "source must be direct or copied")
        confidence = row["confidence"]
        require(confidence is None or
                (type(confidence) is int and 0 <= confidence <= 100),
                "confidence must be null or an integer from 0 to 100")
        require(row["scope"] in ("single-host", "shared-service"),
                "scope must be single-host or shared-service")
        require(type(row["contradicted"]) is bool,
                "contradicted must be true or false")

        observed_at = moment(row["observed_at"])
        reported_at = moment(row["reported_at"])
        valid_until = moment(row["valid_until"])
        require(observed_at <= reported_at <= as_of,
                "dates must satisfy observed_at <= reported_at <= as_of")
        require(observed_at < valid_until and reported_at <= valid_until,
                "valid_until must follow observation and not precede reporting")

        if as_of >= valid_until:
            decision = "review-expiry"
        elif row["contradicted"]:
            decision = "review-conflict"
        elif row["source"] == "copied" or confidence is None or confidence < 70:
            decision = "seek-support"
        elif row["scope"] == "shared-service":
            decision = "narrow-scope"
        else:
            decision = "retain-as-context"

        review_date = as_of
        if decision == "retain-as-context":
            # This ordering avoids overflowing datetime at the end of year 9999.
            review_date = (valid_until if valid_until - as_of <= timedelta(days=7)
                           else as_of + timedelta(days=7))
        review_text = review_date.isoformat(timespec="seconds").replace("+00:00", "Z")
        stated_confidence = "unstated" if confidence is None else str(confidence)
        supplied_conflict = "true" if row["contradicted"] else "false"

        decisions[record_id] = decision
        observations.append(
            f"{record_id}: value={row['value']}; type={row['type']}; "
            f"evidence_id={evidence_id}; observed_at={row['observed_at']}; "
            f"reported_at={row['reported_at']}; valid_until={row['valid_until']}; "
            f"as_of={data['as_of']}; supplied conflict={supplied_conflict}; "
            f"source={row['source']}; stated confidence={stated_confidence}; "
            f"scope={row['scope']}; decision={decision}; review_date={review_text}."
        )

    return {
        "decisions": decisions,
        "observations": observations,
        "limitations": list(LIMITATIONS),
    }


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
