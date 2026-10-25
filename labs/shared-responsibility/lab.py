"""Allocate atomic tasks in a fictional service agreement; never inspect cloud state."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require, validate_case

LAB_ID = "shared-responsibility"
MODELS = ("IaaS", "PaaS", "SaaS")
OWNERS = ("customer", "provider", "unspecified")
TASKS = {
    "physical-host-patching", "workload-os-patching", "application-code-patching",
    "tenant-access", "data-sharing", "backup-copy-creation", "restore-acceptance",
}
LIMITS = [
    "This fictional agreement allocates narrow tasks, not all controls or legal liability for a real cloud service.",
    "Evidence states are supplied snapshots, not independently inspected cloud settings or proof of continued security.",
    "Backup scope, retention, recovery time, restore execution and customer extensions need separate service-specific evidence.",
]


def fields(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected.split()),
            f"{label}: missing or unsupported fields")


def text(value, label):
    require(isinstance(value, str) and 0 < len(value.strip()) <= 400,
            f"{label}: expected nonempty text up to 400 characters")


def rows(value, label):
    require(isinstance(value, list) and 1 <= len(value) <= 20,
            f"{label}: expected 1-20 rows")
    seen = set()
    for row in value:
        require(isinstance(row, dict) and isinstance(row.get("id"), str) and
                re.fullmatch(r"[a-z][a-z0-9-]{0,39}", row["id"]), f"{label}: invalid ID")
        require(row["id"] not in seen, f"{label}: duplicate ID")
        seen.add(row["id"])
    return value


def task_owner(task, service):
    # broad labels such as patching are split by the exact component being patched
    if task == "physical-host-patching":
        return "provider"
    if task == "workload-os-patching":
        return "customer" if service["model"] == "IaaS" else "provider"
    if task == "application-code-patching":
        return "provider" if service["model"] == "SaaS" else "customer"
    if task == "backup-copy-creation":
        return service["backup_copy_owner"]
    return "customer"


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    fields(data, "services controls", "data")
    services = {}
    for service in rows(data["services"], "services"):
        fields(service, "id model backup_copy_owner agreement_ref", "service")
        require(service["model"] in MODELS, "unsupported service model")
        require(service["backup_copy_owner"] in OWNERS, "unsupported backup owner")
        text(service["agreement_ref"], "agreement_ref")
        services[service["id"]] = service
    decisions, observations, task_pairs = {}, [], set()
    for row in rows(data["controls"], "controls"):
        fields(row, "id service_id task claimed_owner evidence evidence_ref evidence_note", "control")
        require(isinstance(row["service_id"], str) and row["service_id"] in services,
                "unknown service reference")
        require(isinstance(row["task"], str) and row["task"] in TASKS, "unsupported task")
        require(row["claimed_owner"] in (*OWNERS, "shared"), "unsupported owner claim")
        require(row["evidence"] in ("pass", "fail", "missing"), "unsupported evidence state")
        for key in ("evidence_ref", "evidence_note"):
            text(row[key], key)
        pair = (row["service_id"], row["task"])
        require(pair not in task_pairs, "duplicate task for the same service")
        task_pairs.add(pair)
        service = services[row["service_id"]]
        owner = task_owner(row["task"], service)
        if owner == "unspecified":
            assignment = "clarify-agreement"
        elif row["claimed_owner"] == "unspecified":
            assignment = "assign-owner"
        elif row["claimed_owner"] == owner:
            assignment = "owner-matches"
        else:
            assignment = "correct-owner"
        decisions[row["id"]] = f"{owner}:{assignment}:evidence-{row['evidence']}"
        observations.append(
            f"{row['id']}: service={row['service_id']} ({service['model']}); task={row['task']}; "
            f"agreement={service['agreement_ref']}; owner={owner}; claimed={row['claimed_owner']}; "
            f"evidence={row['evidence']} at {row['evidence_ref']}: {row['evidence_note']}")
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
