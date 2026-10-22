"""Shared offline lab CLI. Read FOUNDATION-CONTRACT.md before extending it."""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys

CASE_FIELDS = {"schema_version", "lab_id", "case_id", "title", "synthetic", "context", "data", "artifacts"}
CASE_IDS = ("guided", "changed", "challenge")
NAME = re.compile(r"[a-z0-9][a-z0-9_-]*\.[a-z0-9]+\Z")
RESERVED = {"case.json", "answers.json", "notes.txt"}
WINDOWS_NAMES = {"con", "prn", "aux", "nul"} | {f"{p}{n}" for p in ("com", "lpt") for n in range(1, 10)}
MAX_BYTES = 1_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def safe_path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.exists() or part.is_symlink():
            info = part.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not
                    (getattr(info, "st_file_attributes", 0) & 0x400),
                    "linked paths are outside this practice model")
    return path


def read_json(path):
    path = safe_path(path)
    require(path.is_file(), "input must be a regular file")
    require(path.stat().st_size <= MAX_BYTES, "input exceeds the 1 MB practice limit")
    def invalid(value):
        raise ValueError(f"nonstandard JSON number: {value}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object, parse_constant=invalid)


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, sort_keys=True) + "\n").encode("utf-8")


def validate_case(case, lab_id):
    require(isinstance(case, dict) and set(case) == CASE_FIELDS, "case has missing or unsupported envelope fields")
    require(type(case["schema_version"]) is int and case["schema_version"] == 1, "unsupported schema version")
    require(case["synthetic"] is True and case["lab_id"] == lab_id, "case must be synthetic and belong to this lab")
    require(case["case_id"] in CASE_IDS, "unknown case ID")
    require(isinstance(case["title"], str) and bool(case["title"].strip()), "title is required")
    for field in ("context", "data", "artifacts"):
        require(isinstance(case[field], dict), f"{field} must be an object")
    require(len(case["artifacts"]) <= 12, "too many artifacts")
    for name, content in case["artifacts"].items():
        require(NAME.fullmatch(name) is not None and name not in RESERVED and
                name.split(".")[0] not in WINDOWS_NAMES, "unsafe or reserved artifact name")
        require(isinstance(content, str) and len(content.encode("utf-8")) <= MAX_BYTES,
                "artifact must be bounded text")
    return case


def validate_result(result):
    require(isinstance(result, dict) and set(result) == {"decisions", "observations", "limitations"}, "invalid analysis result fields")
    decisions = result["decisions"]
    require(isinstance(decisions, dict) and 0 < len(decisions) <= 200, "analysis needs 1-200 decisions")
    require(all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                for k, v in decisions.items()), "decisions must map nonempty strings")
    for field in ("observations", "limitations"):
        require(isinstance(result[field], list) and result[field] and all(
            isinstance(v, str) and v.strip() for v in result[field]), f"{field} needs text entries")
    return result


def analyse_checked(case, lab_id, analyse):
    validate_case(case, lab_id)
    before = encoded(case)
    result = validate_result(analyse(case))
    require(encoded(case) == before, "analyser modified its input")
    return result


def prepare(root, lab_id, analyse, scenario, output):
    case = read_json(root / "fixtures" / f"{scenario}.json")
    result = analyse_checked(case, lab_id, analyse)
    relative = Path(output)
    require(not relative.is_absolute() and ".." not in relative.parts,
            "output must be a relative path below run/")
    target = safe_path(root / relative)
    run_root = safe_path(root / "run")
    require(run_root in target.parents and not target.exists(), "use a new folder below run/")
    target.mkdir(parents=True, exist_ok=False)
    (target / "case.json").write_bytes(encoded(case))
    (target / "answers.json").write_bytes(encoded({"decisions": {key: "" for key in result["decisions"]},
                                                   "explanation": "", "evidence": []}))
    (target / "notes.txt").write_bytes(b"Prediction:\nEvidence:\nInterpretation:\nUncertainty:\nNext check:\nHelp used:\nLater recall:\n")
    for name, content in case["artifacts"].items():
        (target / name).write_bytes(content.encode("utf-8"))
    return {"prepared": relative.as_posix(), "case": scenario,
            "next": "Read the evidence and save your decisions before viewing the reference analysis."}


def check_answers(expected, answers):
    require(isinstance(answers, dict) and set(answers) == {"decisions", "explanation", "evidence"}, "invalid worksheet fields")
    require(isinstance(answers["decisions"], dict) and all(isinstance(k, str) and isinstance(v, str)
            for k, v in answers["decisions"].items()), "worksheet decisions must be strings")
    require(isinstance(answers["explanation"], str) and isinstance(answers["evidence"], list) and
            all(isinstance(v, str) for v in answers["evidence"]), "invalid explanation or evidence references")
    wanted = expected["decisions"]
    differences = [{"id": key, "submitted": answers["decisions"].get(key), "expected": wanted.get(key)}
                   for key in sorted(set(wanted) | set(answers["decisions"]))
                   if answers["decisions"].get(key) != wanted.get(key)]
    complete = bool(answers["explanation"].strip()) and bool(answers["evidence"]) and all(v.strip() for v in answers["evidence"])
    return {"decision_match": not differences, "written_fields_present": complete,
            "differences": differences, "learner_mastery": "not assessed",
            "review": "A person must check the reasoning and evidence references, including an unfamiliar case."}, 0 if not differences and complete else 1


def main(root, lab_id, analyse, argv=None):
    root = Path(root).resolve()
    parser = argparse.ArgumentParser(description="Offline fictional security practice. Read README.md first.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("cases", help="list the three practice scenarios")
    p = sub.add_parser("prepare", help="create a new practice folder, evidence and blank answers")
    p.add_argument("--scenario", choices=CASE_IDS, default="guided")
    p.add_argument("--out", default="run/attempt-01")
    for name in ("show", "analyse", "check"):
        p = sub.add_parser(name)
        p.add_argument("--case", type=Path, default=root / "fixtures" / "guided.json")
        if name == "check":
            p.add_argument("--answers", type=Path, required=True)
    sub.add_parser("verify", help="compare all fixtures with shipped reference outputs")
    args = parser.parse_args(argv)
    try:
        code = 0
        if args.command == "cases":
            result = [{"id": case_id, "title": validate_case(read_json(root / "fixtures" / f"{case_id}.json"), lab_id)["title"]}
                      for case_id in CASE_IDS]
        elif args.command == "prepare":
            result = prepare(root, lab_id, analyse, args.scenario, args.out)
        elif args.command == "verify":
            results = []
            for case_id in CASE_IDS:
                case = read_json(root / "fixtures" / f"{case_id}.json")
                require(case["case_id"] == case_id, "fixture file and case ID differ")
                actual = analyse_checked(case, lab_id, analyse)
                expected = validate_result(read_json(root / "reference" / f"{case_id}.json"))
                results.append({"case": case_id, "matches_reference": actual == expected})
            code = int(not all(r["matches_reference"] for r in results))
            result = {"cases": results, "learner_mastery": "not assessed"}
        else:
            case = read_json(args.case)
            actual = analyse_checked(case, lab_id, analyse)
            if args.command == "show":
                result = case
            elif args.command == "analyse":
                result = actual
            else:
                result, code = check_answers(actual, read_json(args.answers))
        print(encoded(result).decode("utf-8"), end="")
        return code
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2
