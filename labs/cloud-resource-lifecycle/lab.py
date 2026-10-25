"""Inventory and proposed teardown review, with fictional cost units."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAB_ID = "cloud-resource-lifecycle"
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import main, require

LIMITS = ["Costs are invented whole practice units per day, not provider prices or a bill. Budget alerts do not stop this model's charges.", "A teardown plan is reviewed but never executed. Dependencies and retention approval must be checked again on a real inventory."]


def keys(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")


def integer(value):
    require(type(value) is int and 0 <= value <= 100000, "expected a whole nonnegative practice number")


def analyse(case):
    data = case["data"]
    keys(data, ["today", "budget_units", "spent_units", "resources", "delete_order"])
    for key in ("today", "budget_units", "spent_units"):
        integer(data[key])
    require(isinstance(data["resources"], list) and 0 < len(data["resources"]) <= 30, "supply 1-30 resources")
    resources = {}
    for row in data["resources"]:
        keys(row, ["id", "owner", "expires_day", "daily_units", "depends_on", "retain"])
        require(isinstance(row["id"], str) and re.fullmatch(r"r[0-9]+", row["id"]) and row["id"] not in resources, "unique neutral IDs required")
        require(row["owner"] is None or (isinstance(row["owner"], str) and re.fullmatch(r"team-[a-z]+", row["owner"])), "owner is a fictional team or null")
        if row["expires_day"] is not None:
            integer(row["expires_day"])
        integer(row["daily_units"])
        require(type(row["retain"]) is bool, "retain must be boolean")
        require(isinstance(row["depends_on"], list) and all(isinstance(v, str) for v in row["depends_on"]) and len(set(row["depends_on"])) == len(row["depends_on"]), "invalid dependencies")
        resources[row["id"]] = row
    for row in resources.values():
        require(all(dep in resources and dep != row["id"] for dep in row["depends_on"]), "unknown or self dependency")
    def visit(ident, active, done):
        require(ident not in active, "dependency cycle")
        if ident not in done:
            for dep in resources[ident]["depends_on"]:
                visit(dep, active | {ident}, done)
            done.add(ident)
    done = set()
    for ident in resources:
        visit(ident, set(), done)
    order = data["delete_order"]
    require(isinstance(order, list) and all(isinstance(v, str) and v in resources for v in order) and len(set(order)) == len(order), "unknown or repeated deletion target")
    decisions, observations = {}, []
    for ident, row in resources.items():
        flags = []
        if row["owner"] is None:
            flags.append("owner-missing")
        if row["expires_day"] is None:
            flags.append("expiry-missing")
        elif row["expires_day"] <= data["today"]:
            flags.append("review-due")
        decisions[ident] = "+".join(flags) or "tags-current"
        observations.append(f"{ident}: owner={row['owner'] or 'none'}; expiry={row['expires_day']}; daily_units={row['daily_units']}; retain={str(row['retain']).lower()}.")
    remaining = set(resources)
    issues = []
    for ident in order:
        blockers = sorted(other for other in remaining if ident in resources[other]["depends_on"])
        if resources[ident]["retain"]:
            issues.append(f"{ident}:retention-hold")
        elif blockers:
            issues.append(f"{ident}:used-by-{','.join(blockers)}")
        else:
            remaining.remove(ident)
    decisions["plan"] = "blocked" if issues else "order-valid-in-model"
    residual = sum(resources[ident]["daily_units"] for ident in remaining)
    decisions["cost"] = "residual-cost" if residual else "zero-model-cost"
    decisions["budget"] = "alert-threshold-reached" if data["spent_units"] >= data["budget_units"] else "below-alert-threshold"
    observations.append(f"Plan issues={';'.join(issues) or 'none'}; remaining={','.join(sorted(remaining)) or 'none'}; daily_units={residual}.")
    observations.append(f"Spent={data['spent_units']}; budget={data['budget_units']}; charges are not capped by an alert.")
    return {"decisions": decisions, "observations": observations, "limitations": LIMITS}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
