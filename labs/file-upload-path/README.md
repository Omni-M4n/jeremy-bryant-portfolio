# Review upload validation and path containment

A noticeboard accepts a small text note. Its name should not choose a
folder elsewhere on the computer. Send a note, a path-looking name and a
normal follow-up; inspect what was actually saved.

Prerequisites: http-request-construction and file-integrity. Allow 25-40 minutes.

## Words used here

An **upload** sends file content to a service. An **extension** is the end
of a name, such as `.txt`. A **content type** is a claimed format; it is not
proof of that format. **Containment** means a saved path remains inside the
intended folder. A **hash** is a content fingerprint. **PPM** is a simple image
format; this lab accepts only a one-pixel plain-text form of it.

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

## Exact upload rules

POST `/upload` takes JSON with exactly `filename`, `content_type` and `text`.
This small JSON envelope stands in for an upload; it is not multipart/form-data.
All fields are text. File content is UTF-8 with 1-128 bytes. The plan itself
permits up to 512 bytes per field, enough to test a modest rejected boundary.

A name begins with an ASCII letter, then has up to 31 letters, digits,
underscores or hyphens, followed by `.txt` or `.ppm` in lowercase. It has no
path separators, drive names, extra extensions or trailing dot. Windows
reserved stems such as CON and COM1 are refused regardless of letter case.

For `.txt`, the claimed type must be `text/plain`. Text may contain tabs and
newlines but not other control characters. For `.ppm`, the type must be
`image/x-portable-pixmap`. The content must be ASCII `P3`, width 1, height 1,
maximum 255, and exactly three integer colour values from 0 to 255.
Separate each value with spaces, tabs or line breaks. The exact allowed
characters are space, tab, carriage return, line feed, vertical tab and form
feed. Put at least one of these after the last value too. Other control
characters are refused. This is a tiny PPM subset: no comments, larger images
or extra pixels. No archive or executable content is used or executed.

Accepted uploads get 201. The app creates its own random basename in a fresh
temporary folder and checks the resolved parent before writing a new file.
It does not use the supplied name as a disk path. Repeating a name creates a
different file. Rule failures get 422, wrong envelope type gets 415. Eight
accepted files is the lifetime cap of one server; the next gets 429.

The unsafe pattern would be `storage / supplied_name`: `../note.txt` could
then select a parent folder. This expression is explained only; the lab never
uses it for a write. The supplied implementation combines a name rule,
content rule, generated storage name and a containment check. Changing only
the file extension would not establish that the content has the right type.

## Inspect the operation

The automatic run reads each accepted file back, compares its bytes, records
its generated basename and SHA-256 hash, then deletes its own temporary
upload folder. `contained` and `content_matches` are actual file checks.
The evidence remains in your attempt; the uploaded samples do not.

To make one request manually, start `python lab.py serve --port 8765`. The
server prints its disposable upload directory. In another PowerShell terminal:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8765/upload -Method Post -ContentType application/json -Body '{"filename":"note.txt","content_type":"text/plain","text":"Hello"}'
```

Use the printed directory and returned `saved_name` to inspect that text file
with your file manager. Save the location relative to that directory and its
content. Do not put other files there. Ctrl+C stops the server and removes
its own temporary directory. The portable fixture runner needs no browser.

Save an allowed/rejected matrix, generated file names, readback evidence and
a normal-upload retest after rejection. Handover: what was claimed, what was
checked, where was content saved, and why could the supplied name not escape?

This is not a complete file-security service. It has no malware scanner,
image library, durable storage, authentication or concurrent attacker model.
It never serves uploaded files back as a page. A matching hash confirms the
saved bytes; it does not establish that a file is safe for every other use.

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

- [OWASP file upload guidance](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html): allowlisted formats, names, storage and size limits.
- [Python pathlib](https://docs.python.org/3/library/pathlib.html): resolved filesystem paths.
- [Netpbm PPM format](https://netpbm.sourceforge.net/doc/ppm.html): plain P3 image structure.
