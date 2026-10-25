"""Read-only SQL comparison over three fictional records."""
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlencode, urlsplit
from practice import exact, main, reply, running, send
ROOT = Path(__file__).resolve().parent
LAB_ID = "local-sql-injection"
NAMES = {"Mira", "O'Reed", "Missing", "Mira' OR '1'='1"}

def lookup(name, mode):
    if name not in NAMES or mode not in {"joined", "bound"}:
        raise ValueError("use only the supplied read-only inputs")
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE readers (id INTEGER, name TEXT, book TEXT)")
        connection.executemany("INSERT INTO readers VALUES (?, ?, ?)",
                               [(1,"Mira","Clouds"),(2,"O'Reed","Rivers"),(3,"Tao","Trees")])
        connection.commit()
        connection.execute("PRAGMA query_only=ON")
        # after setup, permit only reading this tiny table; no functions or writes
        connection.set_authorizer(lambda action, a, b, db, source:
            sqlite3.SQLITE_OK if action == sqlite3.SQLITE_SELECT or
            (action == sqlite3.SQLITE_READ and a == "readers") else sqlite3.SQLITE_DENY)
        if mode == "joined":
            query = "SELECT id, name, book FROM readers WHERE name = '" + name + "' ORDER BY id"
            return connection.execute(query).fetchall()
        return connection.execute("SELECT id, name, book FROM readers WHERE name = ? ORDER BY id", (name,)).fetchall()
    finally:
        connection.close()

class App:
    def __call__(self, request):
        path = urlsplit(request.path)
        if request.method != "GET" or path.path not in {"/joined", "/bound"}:
            return reply(404, {"error":"route"})
        values = parse_qs(path.query, strict_parsing=True, max_num_fields=1)
        if set(values) != {"name"} or len(values["name"]) != 1:
            raise ValueError("one name required")
        try:
            rows = lookup(values["name"][0], path.path[1:])
            return reply(200, {"rows":rows})
        except sqlite3.Error:
            return reply(400, {"error":"query-not-valid"})

def exercise(data):
    exact(data, "name")
    if not isinstance(data["name"], str) or data["name"] not in NAMES:
        raise ValueError("choose a supplied name")
    checks = []
    with running(App()) as port:
        for mode in ("joined", "bound"):
            target = "/" + mode + "?" + urlencode(data)
            status, value, _ = send(port, "GET", target)
            checks.append({"mode":mode,"status":status,"response":value})
    return {"checks":checks,"evidence":{"input":data,"responses":checks}}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, App, exercise))
