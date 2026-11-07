# Interview walkthrough

Use this as a preparation guide, not a claim of independent authorship or completed learning. Programmatic checks and learner mastery are separate. Explain the code in your own words, then make and test a small change without following a prepared answer.

## Start with the purpose and data flow

“The tool reads normalized scanner observations from a local JSON file and creates an offline HTML report. It preserves the supplied severity and confidence, escapes supplied text and refuses to overwrite files. It does not scan a network or establish successful exploitation.”

Trace a single fictional finding through this flow:

```text
main
  -> load_report
       -> bounded byte read
       -> UTF-8 decode and check_depth
       -> JSON decode using unique_object and reject_constant
       -> validate -> fields and short_text
  -> render_report -> validation, sort, count, escape, HTML
  -> write_report -> temporary write, flush, atomic link, cleanup
```

Be ready to explain why a high-severity observation with low confidence stays high severity in the output: the tool reports source labels rather than inventing a new risk model.

## Walk through each function

| Code | Explain and demonstrate |
| --- | --- |
| Constants and `ReportError` | Show the file/count/depth bounds and the exact ordering vocabulary. Explain why expected failures use short controlled messages. |
| `check_depth` | Trace entering a quoted string, an escaped quote and a nested container. Explain why brackets inside evidence text do not count and why JSON syntax is still the decoder's job. |
| `unique_object` | Show why ordinary JSON object decoding could silently replace a repeated key. Point to the duplicate-key test. |
| `reject_constant` | Explain why JSON-like `NaN` is rejected rather than carried into the schema. |
| `fields` | Show a missing field and an unexpected field. Explain the maintenance tradeoff of a strict schema. |
| `short_text` | Explain nonempty versus whitespace-only text, length limits, control characters and lone Unicode surrogates. |
| `validate` | Trace version, list, per-finding fields, unique IDs, enumerations and evidence. Explain `type(value) is int` for the schema version and why there is no type coercion. |
| `load_report` | Explain the extra byte in the bounded read, UTF-8 BOM support, pre-decode depth bound and error translation. Show where complete validation ends. |
| `render_report` | Show deterministic severity/ID sorting and counts. Trace an evidence string through `escape`. Explain why resource values never become `href` attributes. |
| `write_report` | Explain temporary-file placement, `flush`, `fsync`, the hard link and cleanup. Explain why checking `exists()` alone would not prevent a destination creation race. |
| `main` | Trace the two positional arguments, successful output and controlled errors. Explain the difference between operational failure and incorrect CLI usage. |

The CSS is static presentation. The report contains no scripts or external resources. Explain why escaping text protects the HTML context but does not remove confidential data.

## Show a small change

Choose one and state the affected files before editing:

- Add a required report-level scanner name with a text bound and an injection test.
- Reverse ID order within a severity and update the deterministic ordering test and contract.
- Change the maximum evidence item length and add passing/failing boundary cases.

Demonstrate one failing test before the change, then a passing suite. Avoid adding scanner-specific importers before you can explain the normalized schema.

## Diagnose a broken version

- Evidence appears as an actual HTML element. Find the missing escaping boundary and repair it.
- `schema_version: true` is accepted. Explain the Python type relationship and tighten the check.
- Rerunning the CLI destroys an earlier report. Find the publication operation and restore the no-clobber behavior.
- An invalid final finding creates a partial page. Locate the validation/write ordering error.

Run these only in a disposable copy using fictional test files.

## State the limits accurately

Be explicit: native scanner exports need a separate normalization step; evidence is not independently checked; confidence does not prove exploitation; no business context or urgency calculation is supplied. Hard-link support is required. Abrupt termination can leave a temporary file. The tests exercise file handling, validation and rendering; they do not establish security of a real target or learner mastery.

Evidence a reviewer should request: a fresh fictional fixture, a predicted report order, a report generated from it, one explained rejection, a tested small code change and a walkthrough without reading this guide word for word.
