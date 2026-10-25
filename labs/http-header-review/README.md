# Check HTTP headers and cookies

A browser gets more than a page's text. It also gets headers with rules about
how to handle that page. Does a saved response meet the needs of a made-up
museum site? Check the page rules and the sign-in cookie separately.

These cases are made up and separate from coursework. They do not claim that
you have reviewed a real site or proved a skill.

## Start here

It helps to know HTTP requests and responses and to try http-triage first.
You need Python 3.10 or newer, a terminal and a text editor. You do not need
to write code, run a web server or have prior web security work.

Allow 30–45 minutes. Read for 5 minutes, predict for 15, then check for 10.
Use the time left to explain your result. Leave later cases for fresh sessions.
Run commands from this lab folder.

| Term | Meaning here |
| --- | --- |
| Header | A named field sent with a response |
| HSTS | A rule received over HTTPS that tells a browser to use HTTPS |
| CSP | Content-Security-Policy, a set of rules for page content |
| frame-ancestors | A CSP rule for which pages may frame this page |
| Cookie | A value the browser can keep and send on later requests |
| Secure | Cookie flag that restricts transport |
| HttpOnly | Cookie flag that stops script access to that cookie |
| SameSite | A rule that limits when a cookie is sent |
| no-store | A rule that tells caches not to store the response |

## Read the case

The case holds the site's rules and saved response fields. It also says which
responses contain HTML, private data or a session. A session links requests
to a sign-in. No browser or network is used here.

Read the [shared file rules](../FOUNDATION-CONTRACT.md) for the format.
The parser rejects missing or extra fields. IDs are unique lowercase names.

| Case field | Required value |
| --- | --- |
| schema_version | 1 |
| lab_id | http-header-review |
| case_id | guided, changed or challenge |
| title | Case title |
| synthetic | true |
| context.question | Nonempty question |
| data | Requirements and responses below |
| artifacts.headers.txt | Exact readable copy of the header data |

The JSON file is the source used for decisions. Its text copy must agree.
JSON is a text format with named fields and values. Each header starts on a
new line, using LF line breaks. Do not include an HTTP status line.

| Requirements field | Allowed value |
| --- | --- |
| hsts_min_seconds | Positive whole number |
| frame_ancestors | 'none' or 'self', including the single quotes |
| session_cookie | HTTP token name; letter case matters |
| cookie_samesite | Strict or Lax |

Each response has an ID, a scheme of `http` or `https`, and header text.
Its `is_html`, `requires_session` and `private_data` fields are true or false.
An HTTP token is a name made from letters, digits and allowed symbols.
It cannot contain spaces or colons. Other unsupported characters are refused.

## Small parser rules

Header names ignore letter case. More than one `Set-Cookie` field is allowed,
but each must name a different cookie. Other repeated headers are refused.
Folded fields, control characters and empty values are also refused.
Unknown header names are ignored. This small reader accepts only these forms:

| Field | Supported parts |
| --- | --- |
| HSTS | max-age, plus optional includeSubDomains |
| CSP | default-src and frame-ancestors; one quoted 'self' or 'none' source each |
| Cookie value | Letters, digits, underscore or hyphen; may be empty |
| Cookie attributes | Path=/, Secure, HttpOnly, SameSite |
| Cache-Control | no-store, private, public, no-cache, max-age=N |

A repeated or unsupported rule or attribute is an input error. It is not a
safe result. These rules are narrower than a browser's full syntax.

## Choose a result

Every response needs HTTPS and `nosniff`. For HTTPS, the HSTS time must meet
the stated minimum. HTML also needs the exact frame-ancestors value given.
A default-src rule does not replace it. Private data needs no-store;
private alone is not enough.

If a session is needed, find the exact cookie named in the requirements.
It needs both Secure and HttpOnly, plus the stated SameSite value.

Use `meets-supplied-requirements` if all the needed checks pass.
Otherwise start with `requirement-gaps:`. Add the matching tokens below in
order, joined by commas without spaces.

| Order | Missing or wrong requirement | Exact token |
| --- | --- | --- |
| 1 | Response uses HTTP | https-required |
| 1 | HTTPS has absent or short HSTS | hsts-duration |
| 2 | Required nosniff value | nosniff |
| 3 | HTML framing rule | frame-ancestors |
| 4 | Storage rule for private data | cache-no-store |
| 5 | Required session cookie is absent | session-cookie |
| 5 | Present cookie lacks Secure | cookie-secure |
| 6 | Present cookie lacks HttpOnly | cookie-httponly |
| 7 | Present cookie has wrong or absent SameSite | cookie-samesite |

Use only one token at order 1. If the cookie is absent, report session-cookie.
Do not also report missing flags for a cookie that is not there.

## Run the practice

Prepare writes under this lab's `run/` folder. It refuses old or linked paths.
Use a new attempt number if your folder already exists.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case before opening the answer. Fill each blank decision in
`run/attempt-01/answers.json` with the exact labels above. Add a short reason.
In the evidence list, give record IDs and field names. Keep your prediction,
unknowns, next check and help used in `notes.txt`. Use double quotes in JSON.
Do not add comments or commas after the last item.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Use the matching attempt path for later cases. The default is the guided
fixture. Input paths are relative to your current folder. Prepare output is
relative to this lab. Analyse shows the answer; save a prediction first.

| Exit code | Meaning |
| --- | --- |
| 0 | Command ran, or decision fields match |
| 1 | Decisions differ, or the worksheet is incomplete |
| 2 | Invalid input or a file error |

Verify compares the three supplied cases with fixed answers. It does not
assess your skill. Check needs reasons and references, but cannot judge them.

## Save and explain

List each gap, its exact evidence and a proposed fix. State one limit of this
small parser. Keep your first prediction and correction. Note any help used.
Read [the worked example](WORKED-EXAMPLE.md) after your first attempt.
Use [the drills](DRILLS.md) to practise with less help.

For a handover, state what you saw, which fields support it, what is unknown
and the next check. Ask a person to review your reasons and a fresh case.
A label match alone does not prove that you can review a real site.

## Limits and sources

The check uses saved excerpts and one made-up site's rules. It does not cover
every browser rule or security need. Unsupported syntax is refused.
No browser, server or network is used. No host settings change.

These sources explain the real concepts. The small schema and local policy
are teaching choices. This lab does not grant a tool qualification.

- [OWASP Secure Headers Project](https://owasp.org/projects/secure-headers-project)
- [IETF RFC 6265: Secure and HttpOnly](https://www.rfc-editor.org/rfc/rfc6265.html#section-4.1.2.5)
- [IETF RFC 6797: HSTS](https://www.rfc-editor.org/rfc/rfc6797.html)
- [W3C CSP3 working draft: frame-ancestors](https://www.w3.org/TR/CSP3/#directive-frame-ancestors)
