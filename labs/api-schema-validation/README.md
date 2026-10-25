# Validate API input and error handling

A small lunch-order service needs a food name and a number of portions.
Someone sends the number as text, leaves it out, or sends too much text.
Which requests should be accepted, and can you understand the error without
seeing the server's private details?

Prerequisite: http-request-construction. Allow 20-30 minutes.

## Words used here

An **API** lets one program ask another to do something. **JSON** stores
named values, such as text, numbers and true/false values. A **schema** is a
set of rules for those values. A **type** says what kind of value it is.
**Validation** checks the rules before using the value. An **internal error**
is a server failure, which is different from rejecting an invalid order.

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

## Exact order rules

POST `/order` accepts `application/json` and a body of at most 256 UTF-8
bytes. The only fields are `name` and `count`. Name must have 1-20 characters,
include a non-space character, and contain no control characters. Count must
be a JSON integer from 1 to 5. Strings, decimals, booleans and null are not
counts. Unicode names are allowed. Spaces are retained, not trimmed away.

The processing order is byte-size check, content type, JSON parsing, then
schema validation. Size above 256 gets 413; a different content type gets
415. Malformed JSON, repeated keys and non-standard number constants get
400. Valid JSON that breaks field rules gets 422. Accepted orders get 201
and an `accepted` copy. The app does not save or charge for an order.

The schema error contains a brief public rule. Responses do not include a
traceback, SQL, local path or secret. This app's choice of 422 is a teaching
policy; another API may document a different validation status.

A fixture has 1-6 requests, each with `body` text and `content_type`. The plan
caps a body at 512 bytes, so it can test just beyond the API's 256-byte edge
without sending a large request. Supported plan types are `application/json`
and `text/plain`. Other transport methods/routes return route errors.

## Send a normal order yourself

Start `python lab.py serve --port 8765`. In another PowerShell terminal:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8765/order -Method Post -ContentType application/json -Body '{"name":"Pear","count":2}'
```

Inspect status and content, then stop the server with Ctrl+C. The fixture
runner is the portable option on macOS/Linux. It preserves expected negative
responses rather than treating them as a terminal failure.

Save an input/output boundary table with status, public error and your reason.
Handover: did parsing or field validation fail, did a normal order still work,
and what evidence would make you investigate a server fault?

These narrow rules do not prove business correctness, authorization, database
safety or the behaviour of every JSON parser. The code is a small supplied
validator, not a full JSON Schema implementation.

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

- [OWASP input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): define accepted values and validate structured inputs.
- [Python JSON documentation](https://docs.python.org/3/library/json.html): parser hooks and input-size caution.
