# Test session expiry and logout

A library website remembers that a reader has signed in. After the reader
logs out, can the old pass still open the profile? Send that old pass again
and check the server's answer. Then let a new pass expire.

Start with http-header-review and burp-access-control. Allow 25-35 minutes.
Use Python 3.10+ already on Windows, macOS or Linux. This lab uses only the
standard library that comes with Python. You need no new install or real account.

## Words used here

A **session** is the server's record of a signed-in visit. A **cookie** is a
small value the client can send with later requests. Here it carries a random
session ID. **Expiry** is the time that ID stops working. **Replay** means
sending an earlier value again. A **status** is the response number: this
app uses 200 for success and 401 when no valid session is present.

## Start a first attempt

Open a terminal in this lab folder. Replace `python` with your existing Python
3 command if needed. `prepare` makes a copy; it refuses to replace an attempt.

```text
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
```

Read `run/attempt-01/case.json`. Write a prediction for each step in
`run/attempt-01/notes.txt`, then send the requests:

```text
python lab.py run --folder run/attempt-01
```

The script starts a real HTTP server on a free port at `127.0.0.1`. It sends
six requests, saves `evidence.json`, and stops the server. That address means
this computer. The app accepts no outside address. Your saved evidence leaves
out token values. Keep the first notes and evidence before reading WORKED-EXAMPLE.md.

Repeat with `changed` in `run/attempt-02`, then `challenge` in
`run/attempt-03`. Keep the reference folder closed until after predicting.
For a new experiment, prepare another copy and edit only its `steps` list.

## Exact app rules

POST `/login` takes JSON with exactly `account` and `password`. The only dummy
pair is `reader` and `training-only`. Never substitute a real password.
A successful login returns a fresh cookie. It makes the cookie sent on that
request stop working. A wrong password returns 401 but leaves a valid session
in place. The runner keeps its current cookie after a wrong login.

GET `/profile` returns 200 only if the server holds the ID and it is less
than two seconds old. The clock starts at login. Using the session does not
reset that clock. At exactly two seconds it has expired. POST `/logout`
deletes the server record for the ID sent. It also sends a header that tells
the client to delete the cookie. Sending that old ID again must fail, even
if the client kept the cookie.

`login`, `wrong-login`, `profile`, `logout`, `wait` and `old-profile` are the
only plan steps. A plan has 1-8 steps and at most one wait. Wait lasts 2.15
seconds. After login, `old-profile` uses the cookie from before that login;
after logout, it uses the logged-out cookie. It never exposes the value.
Two quick valid logins test replacement; this is separate from expiry.

The JSON evidence has stable `checks` and timed request `evidence`. It leaves
out or hides passwords and cookies. Compare the status and body with your
notes. If a run is very slow, a session may expire before your next request.
Keep that evidence and try again in a fresh folder.

## Manual request and checks

You may inspect the app in a second terminal. This is optional; the automatic
run already sends real requests.

```text
python lab.py serve --port 8765
```

In another PowerShell terminal, `curl.exe -i http://127.0.0.1:8765/profile`
shows the response without a signed-in session. On macOS/Linux use `curl`
if it is already available. Press Ctrl+C in the server terminal to stop it. All sessions are
then lost. Do not expose this service or add real data.

After preserving your predictions, maintainer checks are:

```text
python test_lab.py
python lab.py verify
```

Exit 0 means the command worked. Exit 2 means the input was not valid or
there was a file problem. A failed unit test exits with a nonzero code.
Matching the reference does not score your reasons or prove skill.

## Evidence and cleanup

Keep your first prediction and a table of requests and statuses. Save the
evidence with secret values hidden. Explain why deleting only the browser
cookie is not enough. State which steps you ran, including any manual request.
For handover, explain what happened before logout, on replay, after expiry
and after a new login. What would you test next?

The run stops and closes its server, even if an error occurs. The separate
`serve` command needs Ctrl+C. No state is stored outside the named attempt.
After review, remove only that attempt folder with your file manager. Keep
source files, fixtures and earlier attempts you still need.

This HTTP service is for a short lesson. It has no TLS encryption or password
hashing. It does not keep state after restart or lock out accounts. It is not
built for many users at once. Its cookie is HttpOnly and SameSite=Strict.
It leaves out Secure because this is local HTTP. Do not use these choices
as a design for a real service. Script checks do not show what a browser did
or prove that you finished the lab.

Primary documentation opened during preparation:

- [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): enforce logout and expiry on the server.
- [Python HTTP server](https://docs.python.org/3/library/http.server.html): the small server API; unsuitable for production.

`practice.py` is copied here so the package runs on its own. It sends requests
to this computer and makes fresh evidence folders. `lab.py` holds the session
rules. This app changes HTTP state, so it does not use the offline foundation helper.
