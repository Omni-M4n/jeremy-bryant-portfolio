"""Small fictional evidence model; no network or host inspection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case
ROOT = Path(__file__).resolve().parent
LAB_ID = 'soc-query-workbook'

def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), "missing or unsupported fields")

def name(value):
    import re
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", value), "use a short fictional ID")

def number(value, low=0, high=10000):
    require(type(value) is int and low <= value <= high, "integer outside the lesson range")

def flag(value):
    require(type(value) is bool, "true or false required")

def moment(value):
    from datetime import datetime
    import re
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value), "use a UTC timestamp with seconds and Z")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def host(value):
    import re
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9-]+\.test", value), "use a fictional .test host")

import sqlite3
LIMITS = ['Joins link equal host and account fields in this small dataset; they do not prove cause or compromise.', 'One row is one distinct event ID in its own table. Repeated deliveries are removed before querying.', 'Time, sensor coverage and account ownership need separate checks before an incident claim.']
QUERIES = {
    "failures": "SELECT COUNT(*) AS failures FROM login WHERE outcome='failure';",
    "joined": "SELECT COUNT(*) AS joined_rows FROM login l JOIN endpoint e ON l.host=e.host AND l.account=e.account WHERE l.outcome='failure' AND e.kind='process';",
    "linked": "SELECT COUNT(DISTINCT l.id) AS linked_logins FROM login l JOIN endpoint e ON l.host=e.host AND l.account=e.account WHERE l.outcome='failure' AND e.kind='process';",
    "web": "SELECT COUNT(*) AS web_errors FROM web WHERE status>=400;"
}

def tables(case):
    validate_case(case, LAB_ID)
    exact(case["data"], ["login","endpoint","web"])
    require(not case["artifacts"], "case data is the single table source")
    output = {}
    for table, field in [("login","outcome"),("endpoint","kind"),("web","status")]:
        rows=case["data"][table]
        require(isinstance(rows,list) and len(rows)<=100, "each table allows 0-100 deliveries")
        seen={}
        for row in rows:
            exact(row,["id","host","account",field])
            name(row["id"]); host(row["host"]); name(row["account"])
            if table=="login": require(row[field] in ("failure","success"), "unsupported login outcome")
            elif table=="endpoint": require(row[field] in ("process","inventory"), "unsupported endpoint kind")
            else: number(row[field],100,599)
            require(row["id"] not in seen or seen[row["id"]]==row, "conflicting duplicate event ID")
            seen[row["id"]]=row
        output[table]=list(seen.values())
    return output

def populate(db, source):
    db.execute("CREATE TABLE login (id TEXT PRIMARY KEY,host TEXT,account TEXT,outcome TEXT)")
    db.execute("CREATE TABLE endpoint (id TEXT PRIMARY KEY,host TEXT,account TEXT,kind TEXT)")
    db.execute("CREATE TABLE web (id TEXT PRIMARY KEY,host TEXT,account TEXT,status INTEGER)")
    for table, field in [("login","outcome"),("endpoint","kind"),("web","status")]:
        db.executemany(f"INSERT INTO {table} VALUES (:id,:host,:account,:{field})",source[table])
    db.commit()

def analyse(case):
    source=tables(case)
    db=sqlite3.connect(":memory:")
    try:
        populate(db,source)
        counts={key:db.execute(sql).fetchone()[0] for key,sql in QUERIES.items()}
    finally: db.close()
    return dict(decisions={key:str(value) for key,value in counts.items()},
        observations=[f"Unique rows: login={len(source['login'])}; endpoint={len(source['endpoint'])}; web={len(source['web'])}.",
        f"Failed login rows={counts['failures']}; joined rows={counts['joined']}; distinct linked login IDs={counts['linked']}; HTTP status 400-599 rows={counts['web']}."],limitations=LIMITS)

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
