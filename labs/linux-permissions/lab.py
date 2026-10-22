"""Original fictional evidence analysis; no host inspection or network activity."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "linux-permissions"

def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": unsupported or missing fields")

def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 300 and value.strip() == value, label + ": bounded nonempty text required")


from pathlib import PurePosixPath
import re

def path_text(value):
    require(isinstance(value, str) and value.startswith("/") and len(value) <= 200, "absolute fictional path required")
    require(value == "/" or (not value.endswith("/") and "//" not in value and all(part not in (".", "..", "") for part in value[1:].split("/"))), "path must be canonical with no dot components")

def selected(node, actor):
    if node["owner"] == actor["name"]:
        return "owner", int(node["mode"][0])
    if node["group"] in actor["groups"]:
        return "group", int(node["mode"][1])
    return "other", int(node["mode"][2])

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["actor", "nodes", "requests"], "data")
    actor = data["actor"]
    exact(actor, ["name", "groups"], "actor")
    text(actor["name"], "actor name")
    require(actor["name"] not in ("root", "0"), "privileged actors are not modelled")
    require(isinstance(actor["groups"], list) and all(isinstance(g, str) and g.strip() for g in actor["groups"]) and len(actor["groups"]) == len(set(actor["groups"])), "groups must be unique names")
    require(isinstance(data["nodes"], list) and 1 <= len(data["nodes"]) <= 40, "provide 1-40 nodes")
    nodes = {}
    for node in data["nodes"]:
        exact(node, ["path", "type", "owner", "group", "mode"], "node")
        path_text(node["path"])
        require(node["path"] not in nodes, "duplicate path")
        require(node["type"] in ("file", "directory"), "only files and directories are modelled")
        for field in ("owner", "group"):
            text(node[field], field)
        require(isinstance(node["mode"], str) and re.fullmatch(r"[0-7]{3}", node["mode"]), "mode requires three octal digits; special bits are unsupported")
        nodes[node["path"]] = node
    require("/" in nodes and nodes["/"]["type"] == "directory", "root directory evidence required")
    for path in nodes:
        for ancestor in PurePosixPath(path).parents:
            require(str(ancestor) in nodes and nodes[str(ancestor)]["type"] == "directory", "all ancestor directories must be supplied")
    operations = {"read-file": ("file", 4), "write-file": ("file", 2), "execute-file": ("file", 1), "list-dir": ("directory", 4), "search-dir": ("directory", 1), "create-entry": ("directory", 3)}
    require(isinstance(data["requests"], list) and 1 <= len(data["requests"]) <= 40, "provide 1-40 requests")
    decisions, observations = {}, []
    for request in data["requests"]:
        exact(request, ["id", "path", "operation"], "request")
        text(request["id"], "request ID")
        require(request["id"] not in decisions, "duplicate request ID")
        path_text(request["path"])
        require(request["path"] in nodes and isinstance(request["operation"], str) and request["operation"] in operations, "unknown path or operation")
        node = nodes[request["path"]]
        kind, needed = operations[request["operation"]]
        require(node["type"] == kind, "operation does not apply to this node type")
        blocked = []
        for ancestor in reversed(PurePosixPath(request["path"]).parents):
            if not selected(nodes[str(ancestor)], actor)[1] & 1:
                blocked.append(str(ancestor))
        category, bits = selected(node, actor)
        target_ok = bits & needed == needed
        decisions[request["id"]] = "allowed-by-mode" if not blocked and target_ok else "denied-by-mode"
        observations.append(f'{request["id"]}: {request["operation"]} {request["path"]}; class={category}; selected={bits}; required={needed}; target-bits={"yes" if target_ok else "no"}; blocked-ancestor-search={",".join(blocked) or "none"}.')
    return {"decisions": decisions, "observations": observations, "limitations": [
        "Owner bits take precedence over group, then other; there is no fallback to a more permissive class. Ancestor directories need search (execute) permission.",
        "Directory read lists names; search resolves names; creating an entry needs write and search on the target directory. File mode alone does not determine deletion permission.",
        "This evaluates ordinary mode bits for an unprivileged synthetic actor only. ACLs, SELinux, capabilities, special bits, symlinks and mount restrictions are not modelled. No host permissions were inspected or changed."]}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
