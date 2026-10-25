# Test a state-changing request's CSRF protection

A reader chooses a colour on one desk's website. Another page sends a
form to that desk. The browser may bring the reader's cookie along. Does
the colour change even though the reader did not use the intended form?

Prerequisites: session-lifecycle and http-request-construction. Allow
30-45 minutes. The browser observation needs an existing modern browser.

## Words used here

A **preference** is a harmless setting: grey, blue or gold here. An
**origin** is the scheme, host and port of a web address. **CSRF** means
cross-site request forgery: another page causes an unwanted request to use
a person's session. **Ambient** means the browser adds the cookie without
the page supplying it. An **anti-CSRF token** is a server value that the
intended form must return. **Same-site** and **same-origin** are different
browser concepts; changing a port changes origin, not the cookie's site.

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

## Exact service rules

The preference desk runs at one loopback port. The other desk runs at the
next port. Both use `127.0.0.1` and HTTP. They are different origins because
their ports differ, but are same-site. Keep this exact address form; do not
mix `localhost` and `127.0.0.1` or open either page as a local file.

POST `/login` creates a fictional visit with preference grey, a random
session cookie and a separate token. It replaces any supplied earlier visit.
The visit lasts ten minutes or until restart. This is a training sign-in
button with no real identity check. GET `/form` serves three local forms.
GET `/state` shows the preference. GET `/token` supports the bounded runner;
it requires the session, and no CORS permission is returned.

POST `/open` accepts the preference with a valid session alone. POST
`/protected` requires the valid session, the current visit's token and an
Origin header exactly matching the preference desk. Missing, wrong or old
tokens and missing/wrong origins get 403 before state changes. A missing
session gets 401. Accepted changes get 200. Only blue and gold may be sent.
Repeated or unsupported fields are refused. GET cannot change the preference.

Forms use `application/x-www-form-urlencoded`. The cookie is HttpOnly and
SameSite=Strict. Strict does not block this same-site, different-port form
demonstration. Cookies are not scoped by port. This pair is not a test of
cross-site cookie rules for unrelated public domains. The response read rule
and the ability to send a simple form are also different things.

Fixtures contain `rotate` (true/false) and 1-5 request descriptions: route,
preference, origin (same/other/absent), token (valid/wrong/missing/previous),
and whether to send the cookie. `previous` requires `rotate: true`. The
runner makes real HTTP requests but supplies Origin and Cookie itself; it
cannot prove what a browser would attach. It records a state read after every
attempt, with both secret values redacted.

## Required two-page browser observation

Start both servers with:

```text
python lab.py serve --port 8765
```

1. Open `http://127.0.0.1:8765/`. Click **Start a training visit**, then open
   the form. Use **Current form** to choose gold. Check `/state` in another
   tab and save the result.
2. Open `http://127.0.0.1:8766/` in a separate tab. Predict what each button
   will do. Submit its **open route** form. Return to the state tab and refresh.
   Save the response and the preference you observed.
3. Return to the current form on port 8765 and choose gold again. Return to
   the other desk and submit its **protected route** form. Inspect the status,
   refresh state, and save both results.
4. On port 8765, try **Alternate form** and **Short form**. Then verify the
   current form still works. Save the missing/wrong-token and normal-use rows.
5. In browser developer tools, inspect the form request's Origin and whether
   a Cookie header was sent. Redact cookie and token values from screenshots.
   Record browser/version and the two ports. Close the tabs and press Ctrl+C
   in the terminal to stop both servers.

If a browser omits the session, record the resulting 401 and inspect why.
Do not call that proof of the token defence: no authenticated state change
was attempted. Do not disable browser security or alter cookie policy to
force a result. These manual observations are separate from script results.

Handover: compare cross-origin and intended-form requests, missing/wrong-token
checks, the observed preference after each, and successful normal use.

This uses one local host and harmless state. It does not establish every
SameSite/browser policy, token design, login defence, CORS configuration or
production deployment. The origin rule is an extra check, not a replacement
for understanding the token. No external page, callback or account is used.

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

- [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html): session-bound tokens and origin checking.
- [MDN same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy): origin includes scheme, host and port.
- [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): cookie/session controls and their limits.
