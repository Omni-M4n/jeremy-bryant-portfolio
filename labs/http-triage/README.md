# HTTP access-log triage: original guided practice

Read a small web-server access-log export, reconstruct a request sequence and
explain which evidence deserves a closer look. The busiest source is not
necessarily the most concerning. A response status alone cannot tell you what
information a visitor received or whether an account was accessed.

These are original guided materials for someone with introductory networking or
Wireshark experience. Everything in the cases is fictional: the site, addresses,
events, notes and future dates. This is separate practice, not a university
submission or evidence of professional experience. Jeremy's independent
completion has not been assessed. The supplied utility is a tool for the exercise;
the learner is not expected to develop Python or claim independent authorship of it.

## Start here

Use Python 3.10 or newer. Only its standard library is needed. Open a terminal in
this folder; on Windows, `py` can replace `python` if that is the installed command.
No command makes network requests, starts a server or contacts a target.

```sh
python lab.py --help
python lab.py check
python lab.py timeline
python lab.py triage
python lab.py check --report runs/report.json
```

Read [`fixture/context.json`](fixture/context.json) alongside the sorted timeline.
The table itself is [`fixture/access.csv`](fixture/access.csv). Open the generated
`runs/report.json` in a text editor. Write a short interpretation before opening
the [worked example](WORKED-EXAMPLE.md), then try the [drills](PRACTICE.md).

## Compact command contract

`lab.py` is the only maintained command entry point. Input paths are relative to
the terminal's current folder; output paths are relative to this lab folder.
Generated cases and reports must be inside this lab's ignored `runs/` folder.
Every output must be new, including a case directory that would otherwise be
empty. Repeating an output path is refused to protect fixtures and your notes.
Use a fresh name to repeat an exercise.

| Command | Input | Result |
| --- | --- | --- |
| `generate --seed 72 --scenario mixed` | A numeric seed and scenario | New `runs/seed-72-mixed/` containing access CSV, context and manifest |
| `timeline [--case DIRECTORY] [--source-ip ADDRESS]` | Checked-in fixture by default | Requests sorted by UTC time, optionally filtered to one exact source; no file written |
| `triage [--case DIRECTORY] [--volume-threshold 8] [--path-threshold 3] [--output runs/report.json]` | CSV and context from one case | Source summaries, evidence IDs, input hashes and review prompts in one JSON file |
| `check [--case DIRECTORY] [--report FILE]` | Manifest and case files; optional report | Recreate expected bytes from the seed, compare all three files, and optionally recalculate the report |
| `test` | Supplied fixture and temporary cases | Standard-library unit checks; temporary folders removed only from the test's own locations |

`generate --output runs/my-case` sets a fresh case directory. Exit status `0`
means completion, `1` means software tests failed, and `2` means invalid input or
a file problem. These numbers are not learner grades. `check` tests reproducible
file content and calculations; it does not judge an explanation or prove security.

## Reading an HTTP request

**HTTP** is the application protocol used for web requests and responses. An
access log records what the logging component observed. This lab uses a deliberately
small **CSV** export, a text table with comma-separated fields. It is not a raw
packet capture or a parser for every web-server log format.

| Field | Meaning in this export |
| --- | --- |
| `event_id` | Unique fictional record label, such as `HTTP-0017` |
| `timestamp` | Request time in UTC, written `YYYY-MM-DDTHH:MM:SSZ` |
| `source_ip` | Recorded source address; not proof of one device or person |
| `host` | Fictional destination site ending `.test` |
| `method` | `GET`, `HEAD` or `POST` |
| `target` | Requested path, optionally followed by a query starting `?` |
| `status` | HTTP response status recorded by the fictional server |
| `body_bytes` | Number of response body bytes sent in this invented export; excludes headers |
| `user_agent` | A client-supplied label beginning `Practice`; not verified identity |
| `synthetic` | Literal `true`, marking every record fictional |

`GET` requests a representation of a resource. `HEAD` requests similar response
metadata without a response body. `POST` asks a resource to process submitted
content; this export omits that content. These meanings follow
[HTTP method definitions](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3).

| Status used here | Basic meaning |
| --- | --- |
| `200` | The HTTP request succeeded; interpretation depends on the method and resource |
| `303` | The client is directed to another resource; the destination header is absent here |
| `403` | The server understood the request and refuses it |
| `404` | No current representation was found, or the server is unwilling to disclose one |

See the [HTTP status definitions](https://www.rfc-editor.org/rfc/rfc9110.html#section-15).
For this exercise, `HEAD` with `body_bytes=0` is expected. A `POST /login` response
with status `200` is not an authentication-result field. Body size does not tell
you whether a response was a form, a fallback page or sensitive information.

## What the three review rules count

The program groups requests by the exact `(host, source_ip)` pair over the
**whole collection interval**, including both endpoints. It reports:

1. **Request volume:** at least eight requests by default. This is a count, not
   requests per second. Compare collection durations before comparing counts.
2. **Watched-path variety:** at least three distinct paths from `/.env`, `/admin`,
   `/backup.zip` and `/debug`. These are exercise choices, not a universal list
   of malicious paths. An authorised tester or normal site feature could use them.
3. **Watched-path 200:** any request for a watched path with status exactly `200`.
   This asks what the server returned; it does not establish disclosure.

For rules 2 and 3, only text after `?` is removed before comparison. Matching is
case-sensitive and exact. `/admin?view=1` matches `/admin`; `/Admin` and `/admin/`
do not. Repeated requests and query variations do not increase path variety.
The parser accepts simple paths and queries only. It rejects percent encoding,
network-path references, traversal forms, unsupported methods and live addresses.
It does not decode or normalise paths, classify payloads or detect every attack.

Rules do not trust user-agent labels or automatically excuse a source described
in a context note. They do not combine different addresses. Shared addresses,
proxies, changing addresses and missing logs can change the interpretation.
Several prompts can refer to the same sequence. Neither prompt counts nor
request counts are counts of incidents, attackers or affected people.

## Write an evidence-led handover

Keep three things separate in a short note saved under `runs/`:

- **Observed:** collection interval and coverage, source, methods, targets,
  statuses, counts and evidence IDs. Record the rule settings.
- **Interpretation:** one plausible explanation, one alternative, and what the
  export cannot establish. A context note supports an explanation but needs
  corroboration before being treated as confirmed operational history.
- **Next check:** the smallest additional evidence that would change the
  decision, such as scheduled-job records, route configuration, a corresponding
  application event or the preserved response content. Describe the request;
  do not contact these invented addresses or replay the requests.

There are no authentication results, request or response bodies, cookies, proxy
chains, process activity or file changes in this export. `compromise_assessed`
is `false` because that assessment is not made. It does not mean the site has
been declared uncompromised.

## Variants and reproducibility

A **seed** reproduces the same fictional case. Changing it varies addresses,
site label, date and file order. The **scenario** changes the evidence:

| Scenario | Reasoning change |
| --- | --- |
| `mixed` | A busy crawler and a smaller sequence requesting watched paths |
| `soft-200` | One watched-path response is `200`; a fallback route is a competing explanation |
| `logging-gap` | A known missing interval hides some requests, so a rule can stop matching |
| `crawler-only` | Ordinary crawling still matches the volume rule |

`complete-for-fixture` means all planned events were exported by this generator.
It is not a claim that real access logs could establish completeness. `known-gap`
means the listed inclusive interval has no retained rows. The number and content
of missing events are not inferred by triage. Counts are lower bounds for that
collection period. A lack of prompts is especially weak evidence when records
are missing.

The checked-in fixture uses seed **53**, scenario **mixed**, generator **1.0.0**.
[`fixture/manifest.json`](fixture/manifest.json) records its fictional provenance
and SHA-256 fingerprints of the CSV and context. The program regenerates expected
bytes instead of trusting rewritten hashes. Files are UTF-8 with LF endings;
local `.gitattributes` preserves LF in Git. A hash verifies file identity, not
authorship, global novelty or learner competence.

The addresses use the [IPv4 documentation ranges](https://www.rfc-editor.org/rfc/rfc5737.html#section-3),
and the site uses the [reserved `.test` name](https://www.rfc-editor.org/rfc/rfc2606.html#section-2).
Do not substitute real logs or personal data. Run `python lab.py test` after
changing the utility. Independent learning evidence requires an explanation and
an unfamiliar variant; running the utility or reading the answer is practice.
