"""Original fictional evidence exercise. No network or host changes."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "cloud-storage-review"


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

LIMITS = [
    "This is a fictional Boolean read-access model, not an AWS policy or ACL evaluator.",
    "No object contents, write access, conditions, cross-account roles, access points, signed URLs or real cloud state are examined.",
]


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "account_block_public buckets", "data")
    boolean(data["account_block_public"], "account_block_public")
    decisions, observations = {}, []
    for row in records(data["buckets"], "buckets"):
        fields(row, "id purpose data_class bucket_block_public policy_public_read acl_public_read explicit_deny_public_read approval", "bucket")
        require(row["purpose"] in ("internal", "public-site"), "unsupported purpose")
        require(row["data_class"] in ("public", "internal", "restricted"), "unsupported data class")
        require(row["approval"] in ("approved", "none"), "unsupported approval")
        for key in ("bucket_block_public", "policy_public_read", "acl_public_read", "explicit_deny_public_read"):
            boolean(row[key], key)
        grants = [name for name, key in (("policy", "policy_public_read"), ("acl", "acl_public_read")) if row[key]]
        blockers = [name for name, enabled in (("account", data["account_block_public"]), ("bucket", row["bucket_block_public"]), ("deny", row["explicit_deny_public_read"])) if enabled]
        if not grants:
            result = "no-public-grant"
        elif blockers:
            result = "blocked-public-grant"
        elif row["purpose"] == "public-site" and row["data_class"] == "public" and row["approval"] == "approved":
            result = "public-read-approved"
        else:
            result = "public-read-unapproved"
        decisions[row["id"]] = result
        observations.append(f"{row['id']}: grants={joined(grants)}; blockers={joined(blockers)}; purpose={row['purpose']}; class={row['data_class']}; approval={row['approval']}.")
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
