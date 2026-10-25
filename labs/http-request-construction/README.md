# Construct and trace an HTTP request

A picnic order says “red apple”. How does that phrase travel from a form
to a server? Send it in a URL, then in a form body. Compare the received
values with the exact bytes you sent.

This extends [http-triage](../http-triage/README.md) and
[traffic-capture](../traffic-capture/README.md). The first reads saved access
logs. The second creates local traffic and captures it with Wireshark. Here,
you choose the method, query, body and headers, then inspect what arrived.
It is an extension, not a new core lab.

Prerequisites: http-triage and traffic-capture. Allow 20-30 minutes.

## Words used here

A **URL** identifies a resource. The **path** is the part such as `/inspect`.
The **query** follows `?`. A **method**, such as GET or POST, tells the server
the requested operation. **Headers** carry named details. The **body** carries
content after the headers. **Encoding** represents a value in a format that
can travel safely; it is not encryption.

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

## Exact request rules

GET `/inspect` reads query fields and has no body in this toy app. POST
`/inspect` accepts only `application/x-www-form-urlencoded` bodies. The server
returns the raw target, method, `X-Note` header, raw body, decoded query and
decoded form separately. A query field does not replace a form field.

For this form format, `+` represents a space and `%2B` represents a literal
plus. UTF-8 text is decoded after percent decoding. Repeated names become
lists; empty values remain present. Malformed percent escapes and invalid
UTF-8 are rejected. There may be at most eight fields in either location.

A fixture has 1-5 request objects, each with exactly `method`, `target`,
`body`, `content_type` and `note`. They are strings of at most 300 characters.
The plan allows GET and POST to the inspection route. Wrong content type
gets 415. Invalid input gets 400. Unknown routes get 404. A GET body gets 400
under this teaching policy; that is not a claim that HTTP forbids every GET
body in all systems. Headers are not shown as a full packet capture.

In a plan, write a space in the target as `%20` or `+` in a form query.
Write other non-ASCII text with percent encoding, such as `caf%C3%A9`.
Raw spaces, control characters, other routes and URL fragments are refused
before sending. The command exits with code 2 and keeps your attempt files.

## Send one request yourself

Start `python lab.py serve --port 8765`. In a second PowerShell terminal:

```powershell
curl.exe -i "http://127.0.0.1:8765/inspect?item=red+apple" -H "X-Note: desk-1"
curl.exe -i "http://127.0.0.1:8765/inspect" -H "X-Note: desk-1" --data "item=red+apple"
```

Use `curl` on macOS/Linux if already available. A browser can open the first
URL, but its address bar sends GET. Compare the body and query in the returned
JSON. Press Ctrl+C in the server terminal. No request data survives there.

Save a request/response notebook and one prediction about changing method or
encoding. Handover: where did each value travel, how was it decoded, and
which header told the server how to read the body?

This is an HTTP/1 teaching view. It does not capture packets, measure network
timing, demonstrate TLS or cover all URL and HTTP rules.

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

- [MDN HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages): request line, headers and body.
- [Python URL parsing](https://docs.python.org/3/library/urllib.parse.html): query decoding and repeated values.
