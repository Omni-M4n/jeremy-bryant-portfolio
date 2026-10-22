"""Original fictional evidence analysis; no host inspection or network activity."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "endpoint-triage"

def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": unsupported or missing fields")

def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 300 and value.strip() == value, label + ": bounded nonempty text required")


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["processes"], "data")
    rows = data["processes"]
    require(isinstance(rows, list) and 1 <= len(rows) <= 50, "provide 1-50 processes")
    by_id = {}
    for row in rows:
        exact(row, ["id", "parent", "image", "role", "location", "signature", "approved_change", "command"], "process")
        for field in ("id", "image", "command"):
            text(row[field], field)
        require(row["id"] not in by_id, "duplicate process ID")
        require(row["parent"] is None or isinstance(row["parent"], str), "parent must be an ID or null")
        require(row["role"] in ("desktop", "document", "shell", "service", "utility"), "unsupported role")
        require(row["location"] in ("system", "program", "user-temp"), "unsupported location")
        require(row["signature"] in ("verified", "unsigned", "unknown"), "unsupported signature evidence")
        require(type(row["approved_change"]) is bool, "approval must be boolean")
        by_id[row["id"]] = row
    for row in rows:
        seen = set()
        current = row
        while current is not None:
            require(current["id"] not in seen, "cyclic process tree")
            seen.add(current["id"])
            parent = current["parent"]
            require(parent is None or parent in by_id, "parent missing from this bounded snapshot")
            current = by_id.get(parent)
    decisions, observations = {}, []
    for row in rows:
        parent = by_id.get(row["parent"])
        signals = []
        if row["role"] == "shell" and parent and parent["role"] == "document":
            signals.append("document-spawned-shell")
        if row["location"] == "user-temp":
            signals.append("user-temp-execution")
        if signals and not row["approved_change"]:
            result = "prioritise-context-review"
        elif row["approved_change"]:
            result = "documented-change-context"
        elif row["signature"] != "verified":
            result = "signature-context-incomplete"
        else:
            result = "no-modelled-triage-trigger"
        decisions[row["id"]] = result
        observations.append(f'{row["id"]}: parent={row["parent"] or "root"}; image={row["image"]}; location={row["location"]}; signature={row["signature"]}; approval={"yes" if row["approved_change"] else "no"}; signals={",".join(signals) or "none"}.')
    return {"decisions": decisions, "observations": observations, "limitations": [
        "A suspicious relationship is a review priority, not proof of malware; a verified signature is not proof of safety.",
        "Roles, locations, signatures and approval notes are supplied synthetic evidence. The model cannot verify them or establish execution intent.",
        "This bounded tree omits memory, file contents, network activity and missing telemetry; no host was inspected."]}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
