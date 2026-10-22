"""Original fictional evidence exercise. No network or host changes."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "mfa-review"


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()),
            f"{label}: missing or unsupported fields")


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 240,
            f"{label}: expected nonempty text up to 240 characters")


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}", value),
            "record IDs must be lowercase letters, digits and hyphens")


def records(value, label):
    require(isinstance(value, list) and 0 < len(value) <= 60,
            f"{label}: expected 1-60 records")
    seen = set()
    for row in value:
        require(isinstance(row, dict) and "id" in row, f"{label}: invalid record")
        identifier(row["id"])
        require(row["id"] not in seen, f"{label}: duplicate ID")
        seen.add(row["id"])
    return value


def boolean(value, label):
    require(type(value) is bool, f"{label}: expected boolean")


def joined(values):
    return ",".join(sorted(values)) or "none"

from datetime import date

LIMITS = [
    "Method names describe supplied enrolment records, not proof of a successful multi-factor ceremony or any NIST assurance level.",
    "The 90-day emergency test interval and exception rules are fictional local policy; real provider recovery and emergency-access designs differ.",
]


def day(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value), "expected YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("invalid calendar date") from error


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "as_of accounts", "data")
    today = day(data["as_of"])
    decisions, observations = {}, []
    for row in records(data["accounts"], "accounts"):
        fields(row, "id type interactive privileged methods enforced recovery owner credential_lifetime monitored controlled_storage test_age_days exception_until", "account")
        kind = row["type"]
        require(kind in ("human", "service", "breakglass"), "unsupported account type")
        for key in ("interactive", "privileged", "enforced", "monitored", "controlled_storage"):
            boolean(row[key], key)
        methods = row["methods"]
        require(isinstance(methods, list) and all(isinstance(m, str) for m in methods), "methods must be strings")
        require(len(methods) == len(set(methods)), "duplicate authentication method")
        allowed = {"password", "federated-workload"} if kind == "service" else {"password", "totp", "security-key"}
        require(set(methods) <= allowed, "method unsupported for this account type")
        require(row["recovery"] in ("none", "helpdesk-verified", "backup-codes-secured", "shared-mailbox"), "unsupported recovery")
        require(row["owner"] is None or isinstance(row["owner"], str), "owner must be text or null")
        if row["owner"] is not None:
            identifier(row["owner"])
        require(row["credential_lifetime"] in ("none", "short-lived", "long-lived"), "unsupported credential lifetime")
        age = row["test_age_days"]
        require(age is None or (type(age) is int and 0 <= age <= 10000), "invalid test age")
        until = None if row["exception_until"] is None else day(row["exception_until"])
        if kind != "breakglass":
            require(age is None and until is None and not row["controlled_storage"], "emergency controls apply only to breakglass accounts")
        if kind != "service":
            require(row["interactive"] and row["credential_lifetime"] == "none", "human and breakglass records require interactive login and no workload lifetime")
        else:
            require(row["recovery"] == "none" and not row["enforced"], "service records use workload controls, not human MFA or recovery")
        missing = []
        active_exception = kind == "breakglass" and until is not None and until >= today
        if kind == "service":
            if row["interactive"]:
                missing.append("disable-interactive-login")
            if row["owner"] is None:
                missing.append("assign-owner")
            if row["credential_lifetime"] != "short-lived" or "federated-workload" not in methods or "password" in methods:
                missing.append("replace-static-workload-credential")
            if not row["monitored"]:
                missing.append("monitor-workload-use")
        else:
            enrolled = bool(set(methods) & {"totp", "security-key"})
            if not active_exception:
                if not enrolled:
                    missing.append("enrol-mfa")
                elif not row["enforced"]:
                    missing.append("enforce-mfa")
                if (row["privileged"] or kind == "breakglass") and "security-key" not in methods:
                    missing.append("use-phishing-resistant-mfa")
            if kind == "human" and row["recovery"] not in ("helpdesk-verified", "backup-codes-secured"):
                missing.append("repair-recovery")
            if kind == "breakglass":
                if row["owner"] is None:
                    missing.append("assign-owner")
                if not row["monitored"]:
                    missing.append("monitor-emergency-use")
                if not row["controlled_storage"]:
                    missing.append("secure-emergency-material")
                if age is None or age > 90:
                    missing.append("test-emergency-access")
                if row["recovery"] not in ("none", "backup-codes-secured"):
                    missing.append("repair-emergency-recovery")
        decisions[row["id"]] = ";".join(missing) if missing else ("exception-current" if active_exception else "meets-lab-controls")
        exception_state = "current" if active_exception else ("expired" if until is not None else "none")
        observations.append(f"{row['id']}: type={kind}; methods={joined(methods)}; enforced={str(row['enforced']).lower()}; recovery={row['recovery']}; exception={exception_state}; missing={joined(missing)}.")
        observations.append(f"{row['id']}: interactive={str(row['interactive']).lower()}; privileged={str(row['privileged']).lower()}; owner={row['owner'] or 'none'}; credential-lifetime={row['credential_lifetime']}; monitored={str(row['monitored']).lower()}; controlled-storage={str(row['controlled_storage']).lower()}; test-age-days={age if age is not None else 'none'}; exception-until={row['exception_until'] or 'none'}.")
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
