# Test a small request limit without load testing

A ticket desk lets visitors collect three tickets during a short visit.
What happens on the next request, and when can a normal request work again?
Measure a few requests and one short wait.

Prerequisites: http-request-construction and login-triage. Allow 20-30 minutes.

## Words used here

A **limit** is an allowed count. A **window** is the time span used to count
requests. A **threshold** is the count at which the next request is rejected.
HTTP **429** means too many requests in a period. **Retry-After** is a response
header that can tell a client how long to wait. A **monotonic clock** measures
elapsed time without moving backwards when the wall clock is adjusted.

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

## Exact counting rules

GET `/ticket` allows three requests in a two-second window. The first valid
request starts the window. Successful responses are 200 with remaining counts
2, 1 and 0. A later request in that window gets 429 and a Retry-After header.
The header is the remaining wait rounded up to a whole second, at least 1.

At `now >= window start + 2`, the next valid request starts a fresh window
and uses one place in it. Rejected 429 requests do not extend the window.
GET `/other` returns 404 and POST `/ticket` returns 405; neither uses a place.
One server shares one bucket for all its callers. No account or client-ID
header creates a separate allowance. A restart resets state.

A plan has 1-8 steps chosen from `ticket`, `other`, `post` and `wait`. It may
contain one wait of 2.15 seconds. No parallel requests, loop, large payload or
load generator is needed. This is a handful of requests, not a capacity test.
The evidence includes elapsed times, response bodies and the actual header.

Very slow execution can cross a two-second boundary between requests. If
that happens, keep the timed evidence and explain it before using a fresh
attempt. Deterministic unit tests use a chosen clock for exact-edge checks;
the fixture runs use real elapsed time.

## Inspect one response yourself

Start `python lab.py serve --port 8765`. In another PowerShell terminal,
`curl.exe -i http://127.0.0.1:8765/ticket` shows one response. On macOS/Linux
use `curl` if available. Do not start a loop. Use the fixture runner for the
short sequence so the timing is recorded. Stop the server with Ctrl+C.

Save a timed table including the first rejected request, Retry-After value,
and permitted request after reset. Handover: what was counted, where was the
boundary, did rejection move it, and did legitimate use recover?

This single-process fixed-window example does not establish production
capacity, account fairness, abuse resistance, distributed consistency or
protection from a denial-of-service attack.

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

- [RFC 6585 section 4](https://www.rfc-editor.org/rfc/rfc6585.html): 429 and optional Retry-After response semantics.
- [Python monotonic clock](https://docs.python.org/3/library/time.html#time.monotonic): elapsed-time clock behaviour.
