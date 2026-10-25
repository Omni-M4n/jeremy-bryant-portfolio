# Burp practice: whose order is this?

Use Burp Suite Community Edition to intercept a request, replay it manually,
change an order ID, and compare vulnerable and fixed server behaviour. The
original Lantern Orders application contains two fictional users and three
invented craft orders. The question is whether a user can read another user's
order even though the page only shows their own links.

Allow 45–75 minutes for the guided attempt and 20 minutes for a later repeat.
You use a terminal, a browser and Burp's manual tools. No programming is needed.

## Prerequisites and scope

- Python 3.10+ and Burp Suite Community Edition already available on the **same
  machine**. Use the bundled Burp browser. This exercise does not install tools,
  change a VM, configure your everyday browser, or require an account online.
- A terminal opened in this lab folder. On Windows, use PowerShell. Commands
  below use `python`; substitute your existing Python command if necessary.
- The only test target is this process at `http://127.0.0.1:8765/`. No external
  target, other local service, scanner, extension, Intruder job or paid feature
  is needed. The server has no host or target argument and always binds to
  `127.0.0.1`. Do not expose it through a tunnel or port forward.

Training simplification: selecting Ada Finch or Ben Reed creates a disposable
session cookie without a password. Anyone using this app can select either
account. This is **not real authentication**, a privacy service or an example
of production session design. Keep the same account cookie when comparing two
order IDs; changing the account as well would test a different question.

## Maintained command contract

`lab.py` is the single entry point. It uses only Python's standard library.

```text
python -B lab.py --help
python -B lab.py serve --help
python -B lab.py cases
python -B lab.py serve --mode vulnerable --scenario guided --out run/guided-vulnerable-01
```

`serve` runs until Ctrl+C. `--mode` must be explicit. `--scenario` is `guided`
or `changed`; the default is `guided`. `--port` defaults to 8765 and accepts
1024–65535. If that port is busy, stop this attempt and use a fresh output name
with `--port 8766`; use the newly printed URL and port throughout Burp.

`--out` is relative to this lab folder, regardless of the terminal's directory.
It must be a fresh direct child such as `run/attempt-01`. Absolute, nested,
traversing, existing, symbolic-link and Windows reparse/junction paths are
refused. An unsuccessful start may leave its new folder; use a new name rather
than overwriting it. Generated files stay under the ignored `run/` folder.
These checks are for accidental path mistakes, not hostile concurrent filesystem
changes by another local process. Exit codes: 0 normal stop or read-only command;
2 invalid arguments, output-path problem or unavailable port.

Each successful run creates:

| File | Purpose |
| --- | --- |
| `run.json` | Mode, scenario, exact URL and process ID; manual completion remains pending |
| `roster.json` | Synthetic owner roster used by this run |
| `worksheet.md` | Blank manual evidence table and explanation prompts |
| `events.jsonl` | Server outcomes with account labels and IDs, without session tokens |

The server serves only the home page, account selector and in-memory order
routes. It cannot browse or serve your folders. It does not read credentials,
fetch remote URLs, modify orders or send data elsewhere. Its loopback and
Host/Origin checks narrow this exercise's boundaries; they are not a security
claim about Python's development HTTP server.

## Guided attempt

1. Run the vulnerable command above. Leave that terminal open. Confirm its
   printed URL is `http://127.0.0.1:8765/`, mode is `vulnerable`, and scenario is
   `guided`. Open the generated `worksheet.md` in your usual text editor.
2. Start your existing Burp Community installation with a temporary project
   and default configuration. In **Proxy > Intercept**, leave interception off
   initially and use **Open Browser**. Burp's browser is already configured to
   proxy its traffic. In **Settings > Tools > Proxy > Proxy listeners**, confirm
   the listener used by that browser binds to loopback (normally
   `127.0.0.1:8080`), not all interfaces. The primary
   [Proxy settings reference](https://portswigger.net/burp/documentation/desktop/settings/tools/proxy)
   describes these listeners. The proxy port 8080 and application
   port 8765 have different jobs. Do not alter an unrelated listener.
3. In that browser, enter `http://127.0.0.1:8765/` exactly. Use HTTP, not HTTPS,
   and `127.0.0.1`, not `localhost`. No certificate installation is needed.
   Choose **Ada Finch**, then **Select account**. The home page should show Ada,
   **VULNERABLE**, `guided`, and links to orders 101 and 103.
4. In **Target > Site map**, right-click the `http://127.0.0.1:8765` node and
   choose **Add to scope**. If asked, exclude out-of-scope traffic from logging.
   Inspect the resulting scope entry in Settings and keep only this HTTP host
   and port for this temporary project. In **Proxy > HTTP history**, open the
   display filter and select **Show only in-scope items**. Scope filters help
   you focus; they do not block every possible out-of-scope request. Browse
   only this app in this browser. These controls follow the primary
   [scope guide](https://portswigger.net/burp/documentation/desktop/getting-started/setting-target-scope).
5. In **Proxy > Intercept**, turn interception on. In the browser, click Ada's
   order 101. The browser waits while Burp holds the request. Inspect
   `GET /api/orders/101`, the exact Host, and `Cookie: lab_session=...`. Leave
   this baseline unchanged. Click **Forward**, then turn interception off.
   Record the matching entry number from HTTP history. The JSON should show
   order 101 owned by `ada`. If unrelated traffic is held, drop it; do not send
   it to this lab. See the primary
   [interception guide](https://portswigger.net/burp/documentation/desktop/getting-started/intercepting-http-traffic).
6. In HTTP history, right-click that **GET order request** and choose **Send to
   Repeater**. In Repeater, confirm the destination is HTTP, `127.0.0.1`, port
   8765. Click **Send** for an unchanged baseline. Read the status, response
   body, `X-Lab-Mode` and `X-Lab-Scenario`. Write your prediction for order 102.
7. Change only `/api/orders/101` to `/api/orders/102` in that request. Keep its
   Host, method and Ada cookie. Click **Send** once. Record the response status
   and the returned owner and note. Compare with `roster.json`: guided order
   102 belongs to Ben. Explain what this proves about this endpoint. The
   [Repeater guide](https://portswigger.net/burp/documentation/desktop/getting-started/reissuing-http-requests)
   describes manual send, edit and response-history controls.
8. In the browser, go back to `/`, select Ben, and open order 102. Send this
   fresh GET to a **separate Repeater tab** labelled Ben. Verify his own 102,
   then change only its ID to 101. Record both results. Keep the Ada and Ben
   tabs separate; browser account changes do not rewrite an old captured
   request. Do not guess tokens or use real accounts.
9. Save screenshots or copied request/response evidence alongside the worksheet
   before closing this temporary Burp project. Label tokens by account in your
   notes. Do not treat the generated event log alone as proof that you used Burp.

## Apply the prepared fix and retest

No code edit is needed: fixed mode contains the server-side ownership check.
Stop the vulnerable process with **Ctrl+C in its terminal**, then start:

```text
python -B lab.py serve --mode fixed --scenario guided --out run/guided-fixed-01
```

Refresh `/` in Burp's browser. Confirm **FIXED** and `guided`. Select Ada again:
old session cookies become invalid after a server restart. Capture a fresh order
101 request and send it to a new Repeater tab. An old cookie returning 401 is
not evidence that the ownership fix works.

Predict each outcome, then manually perform the following checks with fresh
Ada and Ben sessions. Save the results in the fixed run's worksheet.

| Selected account | Request | Expected outcome in fixed mode |
| --- | --- | --- |
| Ada | `/api/orders/101` and `/api/orders/103` | 200; Ada's correct record is present |
| Ada | `/api/orders/102` | 403; no order note or record body |
| Ben | `/api/orders/102` | 200; Ben's correct record is present |
| Ben | `/api/orders/101` and `/api/orders/103` | 403; no order note or record body |
| Either valid account | `/api/orders/999` | 404; no such seeded order |
| Either valid account | `/api/orders/abc` | 400; invalid ID format |
| Cookie header removed | `/api/orders/101` | 401; select an account first |

The narrow rule is: **a selected training account may read an existing order
only when the server's owner field matches that account**. The browser link list
is the same in both modes. The fix matters at the requested object, not just at
the page that contains its link. A 200 must contain the correct record; a denied
response must exclude it. A status code alone is insufficient evidence.

## Stop, troubleshoot and hand over

Set interception off, save your evidence, and press Ctrl+C in the server
terminal. Wait for its stopped message, then reload the app URL: it should fail
to connect. Close the lab browser and temporary Burp project. No everyday
browser proxy settings or certificates were changed by these instructions.
The `run/` notes remain for later review. Preserve them; there is no automatic
deletion command. A fresh attempt uses a different run name.

If the browser waits, check for a held Proxy request and use Forward or turn
interception off. If history is empty, confirm you used **Open Browser** and
the exact printed URL, then check the scope filter. A 421 means the Host was not
the exact printed host and port. A 403 on `/session` means the browser's Origin
was missing or different; reload the form from the printed URL. A 401 after
restart means you need a new selected session. A bind error usually means the
port is already in use; do not kill an unknown service. Use the alternate port
and a new run folder. If Burp is unavailable, stop here: direct HTTP tests do
not replace the requested Burp practice.

Deliver a short finding, the before/after evidence table, proof of retained
own-record access, and a limitation. Use the worksheet's handover sentence.
Continue with [the drills](DRILLS.md). Open [the worked example](WORKED-EXAMPLE.md)
after writing your initial predictions.

## Software validation and limits

```text
python -B test_lab.py
```

The suite opens temporary **loopback** listeners and sends real HTTP requests.
It checks both modes, both accounts, both owner rosters, valid and invalid
requests, session restart behaviour, Host/Origin restrictions, and output-path
refusals. It also starts the actual CLI, checks its files and home page, stops
that test process, and confirms its socket closes. Scratch artifacts stay in
fresh `run/software-tests-*` and `run/cli-smoke-*` children.
An unsupported symlink-creation facility is reported as a skip, not a pass.
Passing tests establish behaviour of the exercise software. They do not establish
that a learner intercepted anything, understood the result, or completed a
manual Burp retest. **Hands-on completion remains pending until that evidence
and explanation are reviewed.**

This app models one read endpoint and an owner-only rule. It has no real
authentication, password handling, persistence, write operations, sharing,
roles, account recovery or production session protection. Its different 403
and 404 responses reveal whether an ID exists; this is deliberate for teaching
and does not demonstrate privacy protection. Success here is not a claim that
an entire application is secure.

Primary documentation checked 23 October 2026: the linked interception, scope
and Repeater guides, and PortSwigger's
[horizontal access-control workflow](https://portswigger.net/burp/documentation/desktop/testing-workflow/vulnerabilities/access-controls/horizontal-access-controls).
The external guides describe their own exercises; this lab uses only the local
Lantern Orders target. UI labels may vary with the installed Burp version.

Vocabulary: **proxy** observes traffic between a browser and server;
**intercept** pauses a request before forwarding; **Repeater** resends an edited
request manually; **object ID** selects a record; **session** identifies the
selected account in this toy app; **authorization** decides whether that account
may access that record; **horizontal access** crosses between accounts with the
same kind of privileges; **regression check** confirms necessary behaviour
continues after a change.
