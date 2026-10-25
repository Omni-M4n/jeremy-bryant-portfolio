# Compare reflected text and safe output encoding

A noticeboard should display the exact text on a submitted card. A card
contains `<b>LOCAL MARKER</b>`. Will the angle brackets appear, or will the
browser read them as instructions to make text bold?

Prerequisite: http-request-construction. Allow 25-35 minutes. The browser
part needs an existing modern browser as well as Python 3.10+.

## Words used here

**HTML** describes a web page. **Markup** is text the browser reads as page
structure, such as a bold tag. A **text context** is the space between HTML
tags. **Output encoding** represents special characters so they display as
text there. An **entity**, such as `&amp;`, represents a character in HTML.
The response **content type** tells the browser how to read the bytes.

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

GET `/reflect` places a marker directly between `<p id=marker>` and `</p>`.
GET `/encoded` passes the original marker through `html.escape` at that same
point. Both return `text/html`. GET `/text` returns the original marker as
`text/plain`. All use UTF-8 and a no-sniff header.

Only `hello`, `<b>LOCAL MARKER</b>` and `A &amp; B` are accepted. No scripts,
event handlers, external resources or callbacks are allowed. The pages also
set a policy that blocks scripts and other resource loads. This deliberately
shows harmless markup interpretation, not a script-execution exploit.

Each fixture has `marker` and a 1-3 item `modes` list. Modes are `reflect`,
`encoded` and `text`. Unknown markers, repeated query fields and missing
values are rejected. The automatic run records UTF-8 response text and content
type. Its result explicitly says that browser rendering was not observed.

## Required browser observation

Start the page server:

```text
python lab.py serve --port 8765
```

Open `http://127.0.0.1:8765/` in your browser. First predict the result of each
link for your case. Open the links one at a time. Compare the visible marker,
then use the browser's View Source or Network response view to inspect the
returned markup and content type. Save a screenshot of the visible marker
and a response excerpt for each mode. Record your browser/version and result.
Use the back button to return to the link list. Press Ctrl+C to stop.

For the ampersand case, track both the original value and the final display;
do not decode the value before the server encodes it. For the display-desk
case, compare the same marker under different response types.

Handover: which text became markup, which stayed visible text, what changed
in the encoded response, and which observations came from a real browser?

This rule applies to an HTML text context. JavaScript, CSS, URLs and attributes
need context-specific handling. This is not an HTML sanitizer. A parser test
and saved response text does not replace the required visual browser check.

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

- [OWASP output encoding guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html): encoding depends on the output context.
- [Python html.escape](https://docs.python.org/3/library/html.html): escaping the special HTML characters.
