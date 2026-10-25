"""Stateful local dummy account service. No network listener or real account."""
import argparse
import base64
import copy
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import stat
import struct
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from foundation_runtime import encoded, read_json, require, safe_path

PASSWORD = "training-pass"


def totp(secret, at, digits=6):
    require(type(at) is int and 0 <= at <= 10000000000, "time must be a bounded nonnegative integer")
    require(digits in (6, 8), "use six or eight digits")
    key = base64.b32decode(secret, casefold=False)
    digest = hmac.new(key, struct.pack(">Q", at // 30), hashlib.sha1).digest()
    offset = digest[-1] & 15
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7fffffff
    return str(value % (10 ** digits)).zfill(digits)


def fresh():
    return {"dummy_only": True, "secret": base64.b32encode(secrets.token_bytes(20)).decode(), "recovery": secrets.token_hex(16), "recovery_used": False, "enrolled": False, "used_steps": [], "sessions": 0, "last_at": 0, "events": []}


def validate(state):
    expected = {"dummy_only", "secret", "recovery", "recovery_used", "enrolled", "used_steps", "sessions", "last_at", "events"}
    require(isinstance(state, dict) and set(state) == expected and state["dummy_only"] is True, "unsupported state format")
    require(isinstance(state["secret"], str) and len(state["secret"]) == 32, "invalid dummy seed")
    try:
        require(len(base64.b32decode(state["secret"])) == 20, "invalid dummy seed")
    except (ValueError, TypeError) as error:
        raise ValueError("invalid dummy seed") from error
    require(isinstance(state["recovery"], str) and len(state["recovery"]) == 32 and all(c in "0123456789abcdef" for c in state["recovery"]), "invalid dummy recovery code")
    require(type(state["recovery_used"]) is bool and type(state["enrolled"]) is bool, "invalid enrolment flags")
    require(type(state["sessions"]) is int and 0 <= state["sessions"] <= 1000 and type(state["last_at"]) is int and 0 <= state["last_at"] <= 10000000000, "invalid session count or time")
    require(isinstance(state["used_steps"], list) and len(state["used_steps"]) <= 1000 and all(type(v) is int and 0 <= v <= state["last_at"] // 30 for v in state["used_steps"]) and len(set(state["used_steps"])) == len(state["used_steps"]), "invalid consumed time steps")
    require(state["enrolled"] or (state["sessions"] == 0 and not state["used_steps"]), "an unenrolled account cannot retain accepted codes or sessions")
    require(not state["enrolled"] or bool(state["used_steps"]), "enrolment needs an accepted confirmation step")
    require(isinstance(state["events"], list) and len(state["events"]) <= 1000, "invalid event log")
    for event in state["events"]:
        require(isinstance(event, dict) and set(event) == {"operation", "at", "result", "sessions"} and event["operation"] in ("confirm", "challenge", "recover") and event["result"] in ("accept", "reject") and type(event["at"]) is int and 0 <= event["at"] <= state["last_at"] and type(event["sessions"]) is int and 0 <= event["sessions"] <= 1000, "invalid event record")


def transition(original, operation, at, password, proof):
    validate(original)
    require(operation in ("confirm", "challenge", "recover"), "unsupported operation")
    require(type(at) is int and original["last_at"] <= at <= 10000000000, "actions need a nondecreasing training clock")
    require(isinstance(password, str) and isinstance(proof, str), "password and proof must be text")
    require(len(original["events"]) < 1000, "start a new bounded exercise")
    state = copy.deepcopy(original)
    password_ok = hmac.compare_digest(password.encode("utf-8"), PASSWORD.encode("utf-8"))
    if operation == "recover":
        accepted = state["enrolled"] and password_ok and not state["recovery_used"] and hmac.compare_digest(proof.encode("utf-8"), state["recovery"].encode("utf-8"))
        if accepted:
            state.update(secret=base64.b32encode(secrets.token_bytes(20)).decode(), recovery_used=True, enrolled=False, used_steps=[], sessions=0)
    else:
        stage_ok = not state["enrolled"] if operation == "confirm" else state["enrolled"]
        accepted = stage_ok and password_ok and at // 30 not in state["used_steps"] and hmac.compare_digest(proof.encode("utf-8"), totp(state["secret"], at).encode("utf-8"))
        if accepted:
            state["used_steps"].append(at // 30)
            if operation == "confirm":
                state["enrolled"] = True
            else:
                state["sessions"] += 1
    state["last_at"] = at
    event = {"operation": operation, "at": at, "result": "accept" if accepted else "reject", "sessions": state["sessions"]}
    state["events"].append(event)
    validate(state)
    return state, event


def checked_state_path(path):
    path = safe_path(path)
    info = path.stat()
    require(stat.S_ISREG(info.st_mode), "state must be a regular file")
    require(info.st_nlink == 1, "hard-linked state is outside this practice model")
    return path


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["new", "device", "confirm", "challenge", "recover", "evidence", "clean"])
    parser.add_argument("--folder", default="run/account-01")
    parser.add_argument("--at", type=int, default=60)
    parser.add_argument("--password", default="")
    parser.add_argument("--proof", default="")
    args = parser.parse_args()
    try:
        relative = Path(args.folder)
        require(not relative.is_absolute() and ".." not in relative.parts, "use a relative folder below run/")
        folder = safe_path(ROOT / relative)
        require(safe_path(ROOT / "run") in folder.parents, "folder must be below run/")
        path = safe_path(folder / "state.json")
        if args.command == "new":
            require(not folder.exists(), "use a new folder")
            state = fresh()
            folder.mkdir(parents=True)
            path.write_bytes(encoded(state))
            print(json.dumps({"dummy_password": PASSWORD, "dummy_recovery_code": state["recovery"], "note": "Keep this outside the evidence handover. Both factors live on this machine."}, indent=2))
            return 0
        state = read_json(checked_state_path(path))
        validate(state)
        if args.command == "device":
            print(totp(state["secret"], args.at))
            return 0
        if args.command == "evidence":
            print(json.dumps({"dummy_only": True, "events": state["events"], "enrolled": state["enrolled"], "recovery_used": state["recovery_used"], "active_sessions": state["sessions"]}, indent=2))
            return 0
        if args.command == "clean":
            require({p.name for p in folder.iterdir()} == {"state.json"}, "unexpected files; cleanup refused")
            path.unlink()
            folder.rmdir()
            print('{"exercise_removed": true}')
            return 0
        state, event = transition(state, args.command, args.at, args.password, args.proof)
        checked_state_path(path).write_bytes(encoded(state))
        print(json.dumps(event, indent=2))
        return 0 if event["result"] == "accept" else 1
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
