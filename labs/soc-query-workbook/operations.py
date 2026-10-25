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

def build(case_path, output):
    source=lab.tables(read_json(run_input(case_path)))
    target=fresh_folder(output)
    db=sqlite3.connect(target / "events.sqlite")
    try: lab.populate(db,source)
    finally: db.close()
    for key,sql in lab.QUERIES.items():
        (target / (key+".sql")).write_text(sql+"\n",encoding="utf-8",newline="\n")
    return {"database":"events.sqlite","queries":list(lab.QUERIES),"table_rows":{k:len(v) for k,v in source.items()}}

def query(db_path, sql_path):
    path=run_input(db_path); sql=run_input(sql_path).read_text(encoding="utf-8")
    require(len(sql)<=10000,"query exceeds the lesson limit")
    db=sqlite3.connect(path.as_uri()+"?mode=ro",uri=True)
    allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ}
    def authorise(action,first,second,*rest):
        if action==sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if second=="count" else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
    db.set_authorizer(authorise)
    # A bad join must not run forever even though this database is tiny.
    budget=[0]
    def progress():
        budget[0]+=1
        return int(budget[0]>1000)
    db.set_progress_handler(progress,1000)
    try:
        cursor=db.execute(sql)
        require(cursor.description is not None,"use a SELECT query that returns columns")
        rows=cursor.fetchmany(101)
        require(len(rows)<=100,"result exceeds 100 rows; narrow the query")
        return {"columns":[item[0] for item in cursor.description],"rows":rows}
    finally: db.close()

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Build a fictional SQLite workspace or run one read-only query.")
    sub=p.add_subparsers(dest="command",required=True)
    b=sub.add_parser("build"); b.add_argument("--case",required=True); b.add_argument("--out",required=True)
    q=sub.add_parser("query"); q.add_argument("--db",required=True); q.add_argument("--sql",required=True)
    args=p.parse_args()
    try:
        result=build(args.case,args.out) if args.command=="build" else query(args.db,args.sql)
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,sqlite3.Error) as error:
        print(f"Input error: {error}",file=sys.stderr); raise SystemExit(2)
