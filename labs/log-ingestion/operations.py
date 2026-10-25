from pathlib import Path
import argparse
import json
import sys
import lab
from foundation_runtime import safe_path, read_json, encoded, require

def fresh_folder(value):
    relative = Path(value)
    require(not relative.is_absolute() and ".." not in relative.parts, "use a relative path below run/")
    target = safe_path(lab.ROOT / relative)
    require(safe_path(lab.ROOT / "run") in target.parents and not target.exists(), "use a fresh folder below run/")
    target.mkdir(parents=True, exist_ok=False)
    return target

def run_input(value):
    path = safe_path(value)
    require(safe_path(lab.ROOT / "run") in path.parents and path.is_file(), "use a regular input below this lab run/")
    require(path.stat().st_size <= 1000000, "input exceeds 1 MB")
    return path

import sqlite3

def import_file(source, format_name, output):
    source_bytes = run_input(source).read_bytes()
    raw = source_bytes.decode("utf-8")
    records, states, rejected = lab.parse_records(raw, format_name)
    target = fresh_folder(output)
    db = sqlite3.connect(target / "events.sqlite")
    try:
        db.execute("CREATE TABLE events (id TEXT PRIMARY KEY, time TEXT, account TEXT, outcome TEXT)")
        db.executemany("INSERT INTO events VALUES (:id,:time,:account,:outcome)", records)
        db.commit()
        count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        rows = db.execute("SELECT * FROM events ORDER BY time,id").fetchall()
    finally:
        db.close()
    report = dict(source_rows=len(states), imported=count, repeats=list(states.values()).count("repeat"), rejected=len(rejected), rows=rows)
    (target / "import-report.json").write_bytes(encoded(report))
    (target / "rejected.json").write_bytes(encoded(rejected))
    (target / "source.txt").write_bytes(source_bytes)
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Import only the prepared fictional file into a fresh local SQLite database.")
    p.add_argument("--source", required=True)
    p.add_argument("--format", required=True, choices=["csv", "json"])
    p.add_argument("--out", required=True)
    args = p.parse_args()
    try:
        print(json.dumps(import_file(args.source,args.format,args.out), indent=2))
    except (ValueError,OSError,sqlite3.Error) as error:
        print(f"Input error: {error}", file=sys.stderr)
        raise SystemExit(2)
