# HTTP headers and cookies

Compare saved response headers and session-cookie attributes with the stated requirements of a fictional museum application. These are original fictional practice cases, not copied coursework or completed professional work.

## Before starting

Prerequisites: HTTP requests/responses and the HTTP log triage lab are helpful. No web server, browser automation or prior application-security experience is required. Use Python 3.10+ with the standard library. Run the commands from this lab folder. The learner reads evidence, makes decisions and edits a worksheet; programming is not required.

Allow **30-45 minutes** for the first guided pass: 5 minutes for vocabulary and scope, 15 for prediction, 10 for checking and correction, and 5-15 for explanation. Changed and later recall exercises are separate practice. Personal completion and independent competence have not been assessed.

## Vocabulary

**HSTS:** a browser policy delivered over HTTPS. **CSP:** Content-Security-Policy. **frame-ancestors:** the CSP control used here for permitted framing. **Secure:** a cookie transport restriction. **HttpOnly:** restricts script access to a cookie. **SameSite:** a cookie sending constraint. **no-store:** a cache storage directive.

## Evidence and exact input model

Readable synthetic response-header blocks plus application requirements and per-response HTML, session and private-data context.

Each case has exactly `schema_version: 1`, `lab_id: "http-header-review"`, `case_id` (`guided`, `changed`, `challenge`), `title`, `synthetic: true`, `context`, `data`, `artifacts`. `context.question` is nonempty text. Objects reject unknown/missing fields; record IDs are unique lowercase names. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). Files are small UTF-8 JSON; readable artifacts are supplied through prepare where relevant.

`data.requirements` contains `hsts_min_seconds` (positive integer), `frame_ancestors` (`'none'` or `'self'`), `session_cookie` (case-sensitive token name), and `cookie_samesite` (`Strict` or `Lax`). `data.responses` records have `id`, `scheme` (`http`/`https`), boolean `is_html`, `requires_session`, `private_data`, and `headers` (LF-separated fields without a status line). JSON is authoritative; `artifacts.headers.txt` is a required exact mirror. Header names are case-insensitive; repeated Set-Cookie is allowed but repeated cookie names are rejected. Other duplicate headers, folded fields, controls and empty values are rejected. Unknown header names are ignored. HSTS supports max-age and optional includeSubDomains. CSP supports only default-src and frame-ancestors, each with one quoted self/none source. Cookies support simple alphanumeric/underscore/hyphen values and Path=/, Secure, HttpOnly, SameSite. Cache-Control supports no-store, private, public, no-cache, max-age=N. Duplicate or unsupported directives/attributes are errors, not safe results.

## Decision vocabulary

Use `meets-supplied-requirements` if there are no gaps. Otherwise use `requirement-gaps:` followed by applicable comma-separated tokens in this order: `https-required` (HTTP response), **or** `hsts-duration` (HTTPS with absent/short HSTS); `nosniff`; `frame-ancestors` (HTML only); `cache-no-store` (private data only); `session-cookie` (required cookie missing), **or** `cookie-secure`, `cookie-httponly`, `cookie-samesite` for its missing/wrong attributes.

Every response requires HTTPS and nosniff. HTML requires the exact supplied frame-ancestors value; default-src is not its substitute. Private data requires no-store, not merely private. Required sessions need the named cookie and both flags plus the exact supplied SameSite value. The parser is deliberately narrower than browser syntax.

## Run the practice

Use a new attempt number if the destination already exists. Prepare writes only beneath this lab's ignored `run/` folder and refuses existing or linked paths.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and its readable evidence. Before viewing the analysis, edit `run/attempt-01/answers.json`: replace every blank decision with an exact label above, write `explanation` as a paragraph, and put record/field/line references in the `evidence` list. Keep predictions, uncertainty, next check and help used in `notes.txt`. JSON strings use double quotes; do not add comments or trailing commas. An evidence entry can be a record ID plus the relevant field name.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Repeat show/check/analyse with the new attempt path. Default case is `fixtures/guided.json` beside the script. Explicit input paths are relative to your current directory; prepare output is relative to this lab. Exit 0 means command success or matching decision fields, 1 means differences/incomplete worksheet, and 2 means invalid input or a filesystem error. Analyse shows the reference reasoning and should stay closed until a prediction is saved. Verify compares three shipped fixtures with fixed reference outputs; it does not assess a learner. Check requires prose and references but cannot judge their accuracy.

## Deliverable and handover

A configuration review stating each requirement gap, the exact field that supports it, a proposed correction and a parser limitation. Keep your first prediction and correction in the notes. Include an honest help-used statement. Use [the worked example](WORKED-EXAMPLE.md) for the guided case and [the drills](DRILLS.md) to reduce prompts over time.

Handover prompt: "What did you observe, which exact evidence supports it, what remains uncertain, and what narrow check should happen next?" A person should review your reasoning and an unfamiliar case before treating the practice as independently demonstrated.

## Limits and primary references

- Results compare supplied response excerpts with a fictional application policy, not with every browser rule or security requirement.
- The narrow parser rejects folding, duplicate singleton fields and unsupported cookie/CSP/HSTS forms; no browser, server or network is used.

Runtime is offline: no external target, packet transmission, email action or host configuration change occurs. All addresses and names are reserved fictional examples. The local decision rules are teaching choices; the references explain underlying concepts, not a claim of tool certification.

- [OWASP Secure Headers Project](https://owasp.org/projects/secure-headers-project)
- [IETF RFC 6265, sections 4.1.2.5-6: Secure and HttpOnly](https://www.rfc-editor.org/rfc/rfc6265.html#section-4.1.2.5)
- [IETF RFC 6797: HTTP Strict Transport Security](https://www.rfc-editor.org/rfc/rfc6797.html)
- [W3C CSP3 working draft: frame-ancestors](https://www.w3.org/TR/CSP3/#directive-frame-ancestors)
