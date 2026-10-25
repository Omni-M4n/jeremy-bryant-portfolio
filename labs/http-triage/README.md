# HTTP access-log triage: original guided practice

Which web requests need a closer look? Read this small access-log export and put its requests in order. An access log records requests seen by a server. The busiest source may not be the most concerning. A response status alone cannot show what a visitor received. It also cannot show whether they accessed an account.

These new guided materials suit someone with basic networking or Wireshark experience. The site, addresses, events, notes and future dates are made up. This is separate practice. It is not a university submission or proof of professional experience. Jeremy's independent completion has not been assessed. Use the supplied tool for this exercise. You do not need to write Python. Do not claim you wrote the tool without help.

## Start here

Use Python 3.10 or newer. Only its standard library is needed. Open a terminal in this folder. On Windows, `py` can replace `python` if that is the installed command. No command makes network requests, starts a server or contacts a target.

```sh
python lab.py --help
python lab.py check
python lab.py timeline
python lab.py triage
python lab.py check --report runs/report.json
```

Read [`fixture/context.json`](fixture/context.json) beside the sorted timeline. The data table is [`fixture/access.csv`](fixture/access.csv). Open the generated `runs/report.json` in a text editor. Write a short note about what the data shows. Then open the [worked example](WORKED-EXAMPLE.md) and try the [drills](PRACTICE.md).

## Compact command contract

`lab.py` is the only maintained command entry point. Input paths start from the terminal's current folder. Output paths start from this lab folder. New cases and reports must go in this lab's `runs/` folder. Git ignores it. Every output must be new. Even an empty case folder cannot be reused. The tool refuses repeated paths to protect fixtures and notes. Use a fresh name to repeat an exercise.

| Command | Input | Result |
| --- | --- | --- |
| `generate --seed 72 --scenario mixed` | A numeric seed and scenario | New `runs/seed-72-mixed/` containing access CSV, context and manifest |
| `timeline [--case DIRECTORY] [--source-ip ADDRESS]` | Checked-in fixture by default | Requests sorted by UTC time, optionally filtered to one exact source; no file written |
| `triage [--case DIRECTORY] [--volume-threshold 8] [--path-threshold 3] [--output runs/report.json]` | CSV and context from one case | Source summaries, evidence IDs, input hashes and review prompts in one JSON file |
| `check [--case DIRECTORY] [--report FILE]` | Manifest and case files; optional report | Recreate expected bytes from the seed, compare all three files, and optionally recalculate the report |
| `test` | Supplied fixture and temporary cases | Standard-library unit checks; temporary folders removed only from the test's own locations |

`generate --output runs/my-case` sets a fresh case folder. An exit status is the number returned by a command:

| Status | Meaning |
| --- | --- |
| `0` | Completed |
| `1` | Software tests failed |
| `2` | Invalid input or a file problem |

These numbers are not learner grades. `check` rebuilds file content and repeats the calculations. It does not judge an explanation or prove security.

## Reading an HTTP request

**HTTP** sets the rules for web requests and responses. An access log records what the logging component saw. This lab uses a small **CSV** export. CSV is a text table with fields split by commas. This is not a raw packet capture. Its parser does not support every web-server log format.

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

| Method | Meaning |
| --- | --- |
| `GET` | Requests a representation of a resource, such as a page |
| `HEAD` | Requests similar response metadata, without a response body |
| `POST` | Asks a resource to process submitted content; that content is absent from this export |

These meanings follow the [HTTP method definitions](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3). Metadata describes a response, such as its type or length. The body holds the returned content.

| Status used here | Basic meaning |
| --- | --- |
| `200` | The HTTP request succeeded; interpretation depends on the method and resource |
| `303` | The client is directed to another resource; the destination header is absent here |
| `403` | The server understood the request and refuses it |
| `404` | No current representation was found, or the server is unwilling to disclose one |

See the [HTTP status definitions](https://www.rfc-editor.org/rfc/rfc9110.html#section-15). In this exercise, `HEAD` with `body_bytes=0` is expected. A `POST /login` response with status `200` is not a sign-in result. Body size alone cannot show what came back. It might be a form, a fallback page or sensitive information. A fallback page is returned when a requested route is not found.

## What the three review rules count

The program groups requests by the exact `(host, source_ip)` pair. It uses the **whole collection interval**, including both endpoints. These three rules produce prompts for review:

1. **Request volume:** at least eight requests by default. This counts requests, not requests per second. Compare the time spans before comparing counts.
2. **Watched-path variety:** at least three distinct paths from `/.env`, `/admin`, `/backup.zip` and `/debug`. We chose these paths for the exercise. They are not a universal list of harmful paths. An authorised tester or normal site feature could use them.
3. **Watched-path 200:** any request for a watched path with status exactly `200`. This asks what the server returned. It does not prove that data was disclosed.

For rules 2 and 3, matching is exact and case-sensitive. Letter case matters. The query, from `?` onward, is removed before comparison. No other path changes are made.

| Path or input | Treatment |
| --- | --- |
| `/admin?view=1` | Matches `/admin` |
| `/Admin` and `/admin/` | Do not match `/admin` |
| Repeats and query variations | Do not increase path variety |
| Accepted paths and queries | Simple forms only |
| Rejected forms | Percent encoding, network-path references, traversal forms, unsupported methods and live addresses |

The parser does not decode or normalise paths. It does not classify payloads or detect every attack.

Rules do not trust user-agent labels. A context note does not automatically excuse a source. The rules do not combine different addresses. Shared addresses, proxies, changing addresses and missing logs can affect your view. Several prompts can refer to the same sequence. Prompt and request counts do not count incidents, attackers or affected people.

## Write an evidence-led handover

Keep three things separate in a short note saved under `runs/`:

- **Observed:** record the collection interval and coverage. Add the source, methods, targets, statuses, counts and evidence IDs. Record the rule settings.
- **Interpretation:** give one possible explanation and one alternative. State what the export cannot prove. A context note can support your view. Check it against other evidence before treating it as confirmed history.
- **Next check:** name the smallest extra evidence that could change the decision. Examples include scheduled-job records, route settings, a matching app event or the saved response content. Describe the request only. Do not contact these made-up addresses or replay the requests.

| Missing from this export | Why it matters |
| --- | --- |
| Authentication results, request and response bodies, cookies, proxy chains, process activity and file changes | The log alone cannot show these facts |
| A compromise assessment | `compromise_assessed` is `false` because no such assessment was made |

That `false` value does not mean the site has been declared free of compromise.

## Variants and reproducibility

A **seed** makes the same fictional case again. A new seed changes addresses, site label, date and file order. The **scenario** changes the evidence:

| Scenario | Reasoning change |
| --- | --- |
| `mixed` | A busy crawler and a smaller sequence requesting watched paths |
| `soft-200` | One watched-path response is `200`; a fallback route is a competing explanation |
| `logging-gap` | A known missing interval hides some requests, so a rule can stop matching |
| `crawler-only` | Ordinary crawling still matches the volume rule |

`complete-for-fixture` means the generator exported all planned events. It does not mean real access logs could prove their own completeness. `known-gap` means no rows remain for the listed interval, including both endpoints. Triage does not infer how many events are missing or what they contained. Counts give only a lower bound for that period. Missing records make a lack of prompts especially weak evidence.

The checked-in fixture uses seed **53**, scenario **mixed**, generator **1.0.0**. [`fixture/manifest.json`](fixture/manifest.json) records its made-up origin. It also holds SHA-256 fingerprints of the CSV and context. A fingerprint is a value made from the file's bytes. The program rebuilds expected bytes rather than trusting rewritten hashes. Files are UTF-8 with LF endings. Local `.gitattributes` preserves LF in Git. A hash checks file identity. It does not prove who wrote it, global novelty or learner skill.

Addresses use the [IPv4 documentation ranges](https://www.rfc-editor.org/rfc/rfc5737.html#section-3). The site uses the [reserved `.test` name](https://www.rfc-editor.org/rfc/rfc2606.html#section-2). Do not substitute real logs or personal data. Run `python lab.py test` after changing the tool. Evidence of independent learning needs an explanation and an unfamiliar variant. Running the tool or reading the answer is practice.
