# Offline scanner observation reporter

A small Python command line utility that turns normalized JSON findings into a readable, printable HTML report. It uses the standard library, runs offline and makes no network requests. Resources and evidence appear as text, including anything that looks like a URL.

The included [sample](sample.json) is entirely fictional. Its service names, scanner messages and findings are invented. This is a utility project, separate from the guided [finding report](../../labs/finding-report/) and [prioritisation](../../labs/vulnerability-prioritisation/) cases. It produces a report from a defined input format; it does not decide whether a vulnerability exists or calculate a risk priority.

## Run

Use Python 3.10 or newer. From this directory:

```sh
python report.py sample.json my-report.html
python -m unittest -v
```

Open `my-report.html` in a browser. No server or internet connection is needed. The inline stylesheet includes a print layout. A checked [example report](example.html) is supplied for the fictional sample.

Choose a new output name each time. Existing files are never overwritten. The output folder must already exist. The CLI exits with `0` for success, `1` for input/output failure and `2` for incorrect command usage. Operational error messages omit supplied paths and content.

## Input contract

Supply a UTF-8 JSON object. A UTF-8 byte order mark is accepted. Field names are exact; missing, extra or duplicate fields are errors. No automatic type conversions happen.

| Field | Accepted value |
| --- | --- |
| `schema_version` | Integer `1`; boolean `true` and numeric `1.0` are rejected |
| `report_title` | Nonempty text, up to 200 characters |
| `findings` | Array of 0–500 observation objects |

Each observation has exactly these fields:

| Field | Accepted value |
| --- | --- |
| `id` | Unique, case-sensitive identifier; 1–64 ASCII letters, digits, `.`, `_` or `-`; starts with a letter or digit |
| `resource` | Nonempty text, up to 500 characters; a resource identifier, not a clickable link |
| `title` | Nonempty text, up to 200 characters |
| `severity` | `critical`, `high`, `medium`, `low` or `informational` |
| `confidence` | `high`, `medium` or `low` |
| `evidence` | Array of 1–10 nonempty text strings, each up to 2,000 characters |

Severity and confidence are the source's supplied labels. High confidence is not a claim of successful exploitation. Evidence is preserved as supplied text, escaped for HTML. The renderer adds no validation verdict to an observation.

The complete input file may be at most 1,000,000 bytes. JSON container nesting is limited to eight levels before decoding. Non-finite numbers, invisible control characters other than tab/line endings, and unpaired Unicode surrogates are rejected. Whitespace-only text is empty. Surrounding whitespace in accepted text is preserved. A file with `"findings": []` is valid and explicitly says that an empty report does not establish security. An empty file, missing file or missing `findings` field fails without creating output.

## Data flow and safeguards

1. Read at most the byte limit plus one; reject an oversized input.
2. Decode text, bound JSON nesting and reject duplicate keys or non-finite numbers.
3. Validate the entire document, including the final observation, before creating output.
4. Sort by the severity order above, then by case-sensitive ID. Count supplied severity labels.
5. Escape all supplied text into a self-contained HTML page. No supplied value becomes markup, a URL, a stylesheet or a script.
6. Write and flush a temporary file in the output folder. Publish the completed file using a hard link that fails if the destination already exists. Remove the temporary name.

The same accepted input produces the same bytes: there is no timestamp or random content in the report. Reordering observations also leaves the result unchanged; reordering evidence changes the displayed evidence order. Tests cover invalid input, HTML injection, limits, ordering, collisions, a destination creation race and write failure cleanup.

## Limits and current evidence

This accepts normalized JSON, not native scanner exports. It has no scanner integration, live checks, CVSS calculation, remediation advice or vulnerability database. It does not verify evidence or decide urgency. Review evidence and intended resource access with an authorised owner before acting on a finding. Reports may contain sensitive supplied information; HTML escaping does not redact it.

Atomic publication requires a local filesystem that supports hard links. There is no overwrite fallback. A process or machine crash can leave a `.scan-report-*.tmp` file; the report content has already been written there, so keep the output folder appropriate for the supplied data. This is not a power-loss durability guarantee.

Programmatic checks cover the supplied fixture and synthetic edge cases. They do not demonstrate that a learner can explain the implementation, adapt a new scanner export or independently judge a real finding. Learner mastery is pending. Use [PRACTICE.md](PRACTICE.md) and [INTERVIEW.md](INTERVIEW.md) to gather that separate evidence.
