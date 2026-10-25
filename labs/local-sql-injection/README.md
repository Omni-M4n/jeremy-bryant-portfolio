# Explain and retest a simple SQL injection

A book desk looks up a reader by name. The clerk should treat the name as
data. What happens if the program joins that name into database instructions?
Compare two supplied routes using three fictional records.

Prerequisites: http-request-construction and burp-access-control. Allow
25-35 minutes. Your Python installation must include its usual sqlite3 module.

## Words used here

A **database** stores records. **SQL** is a language used to ask it questions.
A **query** is one such instruction. **Injection** happens when supplied data
changes the instruction. A **parameter** passes a value separately from the
query's structure. **Read-only** means the exercise can look at records but
cannot change them after setup.

## Make a first attempt

Open a terminal in this lab folder. Use your existing Python 3 command in
place of `python` if its name differs. No packages need installing.

```text
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
```

Read `run/attempt-01/case.json` in a text editor. JSON is a format that stores
named values and lists. Write your prediction and reason in `notes.txt` in
the same folder. Then run the small request plan:

```text
python lab.py run --folder run/attempt-01
```

This starts a real HTTP server at `127.0.0.1` on a free port, sends the listed
requests, saves `evidence.json`, then closes the server. That address means
this computer. No external host is used. Record what you observed before
opening WORKED-EXAMPLE.md or the reference folder.

Prepare `changed` in `run/attempt-02` and `challenge` in `run/attempt-03`.
The command refuses to replace an attempt or its evidence. To try your own
change, make a new copy and edit only its `data` fields. Keep the first
attempt, even if your guess was wrong. A plan outside the rules stops with
an error. The tool does not treat it as a successful run.

## Exact app rules

The in-memory `readers` table contains only these dummy rows:

| ID | Name | Book |
| --- | --- | --- |
| 1 | Mira | Clouds |
| 2 | O'Reed | Rivers |
| 3 | Tao | Trees |

GET `/joined?name=...` places the supplied name inside SQL quotes by joining
strings. GET `/bound?name=...` uses `WHERE name = ?` and passes the value
separately to SQLite. Both sort rows by ID. The exercise runs both routes for
one name. These are comparisons of supplied implementations, not a repair
you are asked to code.

Only four inputs are accepted: `Mira`, `O'Reed`, `Missing`, and the supplied
read-only comparison `Mira' OR '1'='1`. Arbitrary SQL, stacked statements,
writes and other targets are outside the exercise. Every request builds a
fresh tiny database, then enables read-only mode and an authorizer that
permits only SELECT and reading this table. There are no files or real data.

The fixture contains exactly one `name` field. A successful query returns
200 with its rows, including an empty list if no name matches. A query syntax
error returns 400 with `query-not-valid`; no SQL error details are exposed.
Unsupported supplied inputs get 400 at the server or stop a plan before it
runs. Compare the rows as well as the status.

## Retest ordinary use

After the three cases, prepare another copy and set its `data.name` to `Mira`.
Predict the exact one-row result, then run it. You can also start
`python lab.py serve --port 8765` and open these local URLs in a browser:

```text
http://127.0.0.1:8765/joined?name=Mira
http://127.0.0.1:8765/bound?name=Mira
```

Press Ctrl+C to stop the server. Save the normal-input retest with the
before/after comparison. Handover: what instruction changed, what rows became
visible, how did the parameter change that, and did ordinary names still work?

No authentication is being bypassed here. The example only changes a read
filter over fictional records. Parameter binding does not choose table names
or replace access control. An empty result on one probe is not proof that an
unknown application is safe.

## Checks, evidence and cleanup

After saving your first prediction, these maintainer commands compare the
supplied cases and check boundaries:

```text
python test_lab.py
python lab.py verify
```

`verify` sends fresh local requests. It compares `checks` with the saved
reference files. Exit 0 means the command worked. Exit 2 means the input
was not valid, the reference did not match, or there was a file problem.
A failed unit test exits with a nonzero code. A completed `run` saves what
happened. It does not score your skills. Someone must still review your
reasons and evidence.

Keep the case copy, first notes, evidence, any manual screenshots, and one
question you still have. State which steps you ran. Checks sent by the script
do not show what a browser did or prove that you finished the lab.

The run closes its server, even if an error occurs. A separate `serve`
command needs Ctrl+C in its terminal. After review, use your file manager to
remove only the named attempt folder you made. Keep the supplied files and
any attempts you still need. Do not change host security settings or use real
accounts. Do not point tools at other sites or expose this server.

Use Python 3.10+ on Windows, macOS or Linux. The package uses only the
standard library that comes with Python. The server uses local HTTP, without
TLS encryption. Do not deploy it as a real service.
`practice.py` is a small helper copied into this package. It sends requests
and makes fresh evidence folders. `lab.py` holds the topic rules. These labs
send requests or change short-term state, so they do not use the offline
foundation helper.

Primary documentation opened during preparation:

- [OWASP SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html): separating query structure from values.
- [Python SQLite documentation](https://docs.python.org/3/library/sqlite3.html): parameter placeholders and the database API.
