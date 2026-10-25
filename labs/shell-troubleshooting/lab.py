"""Interpret a small supplied command notebook; never execute its commands."""
from pathlib import Path
import ntpath
import posixpath
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "shell-troubleshooting"
LIMITATIONS = [
    "Commands and fields are supplied fictional evidence, not commands executed or operating-system output parsed by this helper.",
    "Path resolution is lexical and excludes links, mounts, case-sensitive Windows folders, wildcards, expansion and permission checks. Actual argument tokens are supplied explicitly.",
    "GNU grep uses only ordinary -F searches here, without -q. PowerShell cmdlet success uses the immediately captured $?; a retained $LASTEXITCODE belongs to a native program.",
    "Service state, a PID, free bytes and a socket binding do not prove malicious intent or external reachability. Filesystem quotas, changing processes and permissions need separate evidence."
]


def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": missing or unsupported fields")


def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 500 and value.strip() == value, label + ": bounded nonempty text required")


def integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, label + ": integer outside allowed range")


def boolean(value, label):
    require(type(value) is bool, label + ": boolean required")


def windows_fully_qualified(value):
    """Accept drive-rooted or ordinary UNC paths without omitted drive state."""
    path = value.replace("/", "\\")
    if re.match(r"^[A-Za-z]:\\", path):
        return True
    if not path.startswith("\\\\"):
        return False
    parts = path[2:].split("\\")
    # A UNC path needs both a server and a share; device namespaces are excluded.
    if len(parts) < 2:
        return False
    return all(part not in {"", ".", ".."} and not part.endswith((".", " "))
               and not re.search(r'[<>:"|?*\x00-\x1f]', part)
               for part in parts[:2])


def validate_windows_argument(value):
    """Only plain relative arguments or the supported fully qualified forms."""
    if windows_fully_qualified(value):
        return
    path = value.replace("/", "\\")
    require(not path.startswith("\\") and ":" not in path,
            "Windows argument must be plain relative or fully qualified; root-relative and drive-relative forms are unsupported")


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["shell", "records"], "data")
    require(isinstance(data["shell"], str) and data["shell"] in {"bash", "powershell"}, "unsupported shell")
    require(isinstance(data["records"], list) and 1 <= len(data["records"]) <= 20, "provide 1-20 records")
    decisions, observations = {}, []
    for record in data["records"]:
        require(isinstance(record, dict), "record must be an object")
        for key in ("id", "kind", "command"):
            text(record.get(key), key)
        record_id, kind = record["id"], record["kind"]
        require(record_id not in decisions, "duplicate record ID")
        base = ["id", "kind", "command"]
        if kind == "path":
            exact(record, base + ["cwd", "wanted", "arguments", "existing_files"], kind)
            paths = posixpath if data["shell"] == "bash" else ntpath
            fully_qualified = posixpath.isabs if data["shell"] == "bash" else windows_fully_qualified
            for key in ("cwd", "wanted"):
                text(record[key], key)
                require(fully_qualified(record[key]), "cwd and wanted must be fully qualified")
            require(isinstance(record["arguments"], list) and 1 <= len(record["arguments"]) <= 8, "invalid argument list")
            require(isinstance(record["existing_files"], list) and len(record["existing_files"]) <= 20, "invalid file inventory")
            for value in record["arguments"] + record["existing_files"]:
                text(value, "path evidence")
            require(all(fully_qualified(value) for value in record["existing_files"]), "file inventory must be fully qualified")
            if data["shell"] == "powershell":
                for value in record["arguments"]:
                    validate_windows_argument(value)
            normal = lambda value: paths.normcase(paths.normpath(value))
            resolved = normal(paths.join(record["cwd"], record["arguments"][0]))
            result = ("repair-path-quoting" if len(record["arguments"]) != 1 else
                      "check-working-directory" if resolved != normal(record["wanted"]) else
                      "requested-file-missing" if resolved not in {normal(value) for value in record["existing_files"]} else
                      "requested-file-resolved")
            detail = f'argument count={len(record["arguments"])}; first resolved path={resolved}; wanted={normal(record["wanted"])}.'
        elif kind == "search":
            exact(record, base + ["match_count", "exit_status", "success", "stderr", "last_native_exit"], kind)
            integer(record["match_count"], 0, 1000, "match count")
            require(isinstance(record["stderr"], str) and len(record["stderr"]) <= 1000, "invalid error stream")
            if data["shell"] == "bash":
                require(record["success"] is None and record["last_native_exit"] is None, "Bash record cannot contain PowerShell status fields")
                integer(record["exit_status"], 0, 2, "ordinary GNU grep status")
                status = record["exit_status"]
                require(not (status == 0 and record["match_count"] == 0 or status == 1 and record["match_count"] > 0), "grep status contradicts matches")
                require(status == 2 or not record["stderr"], "successful ordinary grep record contains errors")
                result = "search-command-error" if status == 2 else "no-matching-lines" if status == 1 else "matching-lines-observed"
                detail = f'GNU grep exit={status}; matches={record["match_count"]}; stderr={record["stderr"]!r}.'
            else:
                require(record["exit_status"] is None, "cmdlet has no native exit status")
                boolean(record["success"], "immediate cmdlet success")
                require(record["last_native_exit"] is None or type(record["last_native_exit"]) is int and -2147483648 <= record["last_native_exit"] <= 2147483647, "invalid retained native exit")
                require(not record["success"] or not record["stderr"], "successful cmdlet record contains errors")
                result = "search-command-error" if not record["success"] else "no-matching-lines" if record["match_count"] == 0 else "matching-lines-observed"
                detail = f'Immediate $?={record["success"]}; matches={record["match_count"]}; retained $LASTEXITCODE={record["last_native_exit"]} is not this cmdlet status; error stream={record["stderr"]!r}.'
        elif kind == "pipeline":
            exact(record, base + ["statuses", "pipefail", "reported_status"], kind)
            require(data["shell"] == "bash", "pipeline model supports Bash only")
            require(isinstance(record["statuses"], list) and 2 <= len(record["statuses"]) <= 5, "provide 2-5 stage statuses")
            for status in record["statuses"]:
                integer(status, 0, 255, "stage status")
            boolean(record["pipefail"], "pipefail")
            integer(record["reported_status"], 0, 255, "reported status")
            nonzero = [status for status in record["statuses"] if status]
            expected = (nonzero[-1] if nonzero else 0) if record["pipefail"] else record["statuses"][-1]
            require(record["reported_status"] == expected, "reported pipeline status contradicts stage statuses and pipefail")
            result = "all-stages-zero" if not nonzero else "earlier-nonzero-hidden" if expected == 0 else "pipeline-nonzero-review-stage"
            detail = f'stages={record["statuses"]}; pipefail={record["pipefail"]}; reported={expected}; interpret nonzero using the individual tool contract.'
        elif kind == "capacity":
            exact(record, base + ["available_bytes", "required_bytes"], kind)
            integer(record["available_bytes"], 0, 10**15, "available bytes")
            integer(record["required_bytes"], 1, 10**15, "required bytes")
            margin = record["available_bytes"] - record["required_bytes"]
            result = "stated-space-budget-met" if margin >= 0 else "stated-space-budget-short"
            detail = f'available={record["available_bytes"]} bytes; required={record["required_bytes"]} bytes; margin={margin} bytes.'
        elif kind == "service":
            exact(record, base + ["query_succeeded", "state"], kind)
            boolean(record["query_succeeded"], "service query success")
            require(record["state"] is None or isinstance(record["state"], str) and record["state"] in {"running", "stopped", "not-found"}, "unsupported service state")
            require(record["query_succeeded"] == (record["state"] is not None), "service result contradicts query success")
            result = "service-query-inconclusive" if record["state"] is None else "service-" + record["state"]
            detail = f'query succeeded={record["query_succeeded"]}; state={record["state"]}; compare with the expected service before changing anything.'
        elif kind == "process":
            exact(record, base + ["pid", "expected_pid", "name"], kind)
            integer(record["pid"], 1, 2**31 - 1, "PID")
            integer(record["expected_pid"], 1, 2**31 - 1, "expected PID")
            text(record["name"], "process name")
            result = "process-pid-correlated" if record["pid"] == record["expected_pid"] else "process-pid-mismatch"
            detail = f'PID={record["pid"]}; expected PID={record["expected_pid"]}; name={record["name"]}; name alone does not establish identity or intent.'
        elif kind == "listener":
            exact(record, base + ["bind", "port", "owner_pid", "expected_pid"], kind)
            require(isinstance(record["bind"], str) and record["bind"] in {"127.0.0.1", "::1", "0.0.0.0", "::"}, "unsupported binding")
            integer(record["port"], 1, 65535, "port")
            integer(record["expected_pid"], 1, 2**31 - 1, "expected PID")
            if record["owner_pid"] is not None:
                integer(record["owner_pid"], 1, 2**31 - 1, "owner PID")
            result = ("wildcard-listener-review" if record["bind"] in {"0.0.0.0", "::"} else
                      "listener-owner-unresolved" if record["owner_pid"] is None else
                      "listener-pid-mismatch" if record["owner_pid"] != record["expected_pid"] else
                      "loopback-listener-correlated")
            detail = f'bind={record["bind"]}; port={record["port"]}; owner PID={record["owner_pid"]}; expected PID={record["expected_pid"]}; a bind is not a remote reachability test.'
        else:
            raise ValueError("unsupported record kind")
        decisions[record_id] = result
        observations.append(f'{record_id}: {detail} Command recorded: {record["command"]}')
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITATIONS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
