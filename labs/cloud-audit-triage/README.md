# Build a cloud audit evidence timeline

Correlate identity, session, action and result while preserving uncertainty. Separate a denied attempt from a successful change, recognise missing logging and avoid attributing a session to a person from a label alone.

**Time:** 30-45 minutes for a first pass; use the later recall task on another day.
**Prerequisites:** Basic file navigation, editing a small JSON worksheet, and introductory networking/security vocabulary. No professional security experience, cloud account, coding background or programming changes are required.

> **Vocabulary:** **Audit event**: a record of an attempted action and its result. **Correlation**: a supported link between records. **Attribution**: identifying who actually acted. **Management event**: a change or identity operation. **Data event**: an object operation. **Coverage gap**: activity types not reliably recorded.

## Evidence and exact semantics

This is a **fictional schema**, not provider log JSON. `data` has UTC
`window_start`, `window_end`, `logging` (Boolean `management` and `data`),
`approved_changes`, and nonempty `events`. Logging is the coverage configuration
at the start of the window. Event fragments can still exist for a disabled
category; a fragment never proves full coverage.

Every event has unique `id`, `at`, `identity`, `session`, `action`, `result`, and
`resource`. All IDs are lowercase labels, not real account identifiers. Action
is `sign-in`, `read-object`, `change-policy`, or `disable-logging`; result is
`success` or `denied`. Sign-in resource must be `identity-service`. Read-object
is a data action; the others are management actions. `logging` is reserved for
the extra coverage decision. Timestamps use exactly `YYYY-MM-DDTHH:MM:SSZ` and
must lie inside the inclusive window. The window must increase.

An approval has exactly `identity`, `action`, `resource`, `from`, `to`; only
change-policy/disable-logging actions can be approved. Both approval boundaries
are inclusive. Correlation requires a successful sign-in with equal identity
**and** session at or before the action, at most 15 minutes earlier, inclusive.
Input order is not trusted; output observations are sorted by time then ID.

Use these exact labels for event IDs, with the first applicable rule winning:

| Label | Rule |
| --- | --- |
| `denied-no-success-evidence` | Result denied; this record does not establish a successful change. |
| `authentication-only` | Successful sign-in; no downstream action established by this record alone. |
| `successful-action-unattributed` | Successful non-sign-in without the required correlation. |
| `successful-read-correlated` | Successful object read with correlation. |
| `approved-change-correlated` | Successful correlated change matching identity/action/resource and approval window. |
| `unapproved-change-correlated` | Successful correlated change without that approval match. |

For the extra `logging` decision use `coverage-configured` when both categories
are enabled, otherwise `coverage-gap:ITEMS` where ITEMS is `data`, `management`,
or `data,management` in that order. Append `;interruption-observed` whenever any
successful disable-logging event appears, regardless of approval or correlation.
A denied disable event never adds that suffix. Configured coverage is not proof
that every event was delivered.

## Run the exercise

From the repository root, enter this folder with `cd labs/cloud-audit-triage`.
Use Python 3.10 or newer. On Windows, `py` may replace `python` if that is your
installed launcher. No package install, account, cloud subscription or billing
setup is needed. Commands run entirely offline and change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any extracted `.txt` evidence. Edit the blank
`run/attempt-01/answers.json`: fill every decision with the exact vocabulary
below, write your own explanation, and cite record IDs or line references in
`evidence`. Keep `notes.txt` for prediction, uncertainty and help used.
Only after saving your prediction:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has exactly `decisions` (object), `explanation` (text), and
`evidence` (list of text references). For example, an evidence entry can be a
record ID plus its field name. Use your own case IDs, not invented references.
`check` compares decision strings and requires nonempty written fields; a person
must assess their accuracy. `verify` checks shipped fixtures, not learner skill.
Exit codes are 0 for success/match, 1 for differences or incomplete written
fields, and 2 for invalid input. Default `--case` is the guided fixture beside
the script. Explicit input paths are relative to the working directory; `--out`
is relative to this lab and must be a new folder below `run/`.

For the next cases, prepare fresh folders:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with the chosen folder.
Edit practice copies only. Do not overwrite fixture or reference files.

## Deliverable and handover

Save one completed worksheet and a short evidence note for each case. Include
your prediction, changed judgment, uncertainty, and one next check you cannot
perform from this evidence. Record whether you used the worked example or help.
Ask a reviewer: "Can you reproduce my decision from these record IDs, and which
claim goes beyond the evidence?" Your independent status remains **unassessed**;
matching output is not a qualification, professional experience or proof of
mastery. These are original fictional practice cases, not assessment submissions.

## Limits

The model does not parse a real cloud log, validate cryptographic provenance, infer intent, account for every authentication route, restore logging or query a service. The arbitrary 15-minute correlation window is a teaching boundary. Unattributed means insufficient supplied linkage, not proof of malicious activity.

## Primary references

The official record reference demonstrates time, identity, action and result-related evidence in real audit records. This lab uses smaller fictional names and deliberately avoids claiming provider parsing or complete event coverage.

- [AWS CloudTrail: event record contents](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html)

Links are optional further reading, checked 2026-10-23. Running this lab does
not fetch them. See [the worked example](WORKED-EXAMPLE.md) after your prediction
and [the drills](DRILLS.md) for varied practice.
