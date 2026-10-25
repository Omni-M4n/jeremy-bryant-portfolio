# Write a finding another reader can check

A toy record page once showed the wrong person's record. A developer says it is fixed. Explain what the evidence shows. Check that the record owner can still use the page.

This extends `vulnerability-retest` and `burp-access-control`. You turn saved test evidence into a report. Another authorised reader should be able to trace its claims and repeat its narrow checks.

## Before you begin

Complete `burp-access-control`, `vulnerability-retest` and `rules-of-engagement`.
This lab has two required stages. Allow 30 minutes for fictional practice and
30-45 minutes to write from a completed owned local attempt. If you have no
completed local attempt, do the linked Burp lab first. It allows 45-75 minutes
for a guided attempt. The local stage stays **unrun** until you do it.


Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

A finding is a problem statement backed by evidence. Preconditions are facts that must hold before a test. Reproduction steps let an authorised person repeat it. A retest checks a change. A regression means a change broke a valid use.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

### Stage 1: fictional preparation

1. Read `transcript.txt`. Fill `report-template.md` in your attempt folder.
2. Keep its origin as **supplied authored transcript**. It is fictional training evidence.
3. State the scope, expected result, observed result, limited harm and exact line references.
4. Record dates, environment and account setup only if supplied. Otherwise write **not supplied**. Do not invent preconditions from a response line.
5. Separate **steps shown in the evidence** from **proposed repeat steps — not run**. Add a correction suggestion, its owner and both retest results or gaps.
6. Save this draft and the worksheet before the reveal. The labels below apply only to this supplied case.

### Stage 2: required report from your own local attempt

The fictional stage alone does not complete this lab. Use evidence from your
completed owned local Burp/access-control attempt or a completed comparable
local retest. The offline `vulnerability-retest` worksheet alone is not that
evidence. Do not relabel its invented records as your test.

Start at [Burp prerequisites and scope](../burp-access-control/README.md#prerequisites-and-scope).
Use Python and Burp Community already available on the same machine.
The only target is the lab process at `http://127.0.0.1:8765/`.
Use Burp's bundled browser and manual tools. Do not use a scanner, other
service, tunnel, port forward, real account or new installation.

Follow [Guided attempt, steps 1-9](../burp-access-control/README.md#guided-attempt).
Run its vulnerable command from the **burp-access-control** folder:

```text
python -B lab.py serve --mode vulnerable --scenario guided --out run/guided-vulnerable-01
```

Use a fresh run name if it exists. If port 8765 is busy, follow that guide's
fresh-run rule for port 8766. Use its printed URL and port throughout.
Keep the account cookie when changing only an order ID. Save the actual
Burp request and response evidence before closing its temporary project.

Then follow [Apply the prepared fix and retest](../burp-access-control/README.md#apply-the-prepared-fix-and-retest).
Stop the vulnerable process with Ctrl+C in its own terminal. From the same
Burp lab folder, start its fixed mode with a fresh run name:

```text
python -B lab.py serve --mode fixed --scenario guided --out run/guided-fixed-01
```

Select fresh sessions after restart. An old cookie's 401 does not prove a fix.
Complete the guide's retest table, including the correct owner's access.
Check the response body as well as its status. Follow
[Stop, troubleshoot and hand over](../burp-access-control/README.md#stop-troubleshoot-and-hand-over)
to save evidence, stop the process and confirm that its URL no longer connects.
If Burp is unavailable, leave this required stage unrun. Direct helper tests
do not replace manual Burp evidence.

If you already have a completed owned local retest, trace it to its actual
run and approved scope. It must retain the same before/after evidence and
valid-use check. Missing evidence means a gap, not permission to invent it.

Write `local-report.md` in this finding-report attempt folder. Copy the report
headings, then change **Evidence origin** to name your actual local run.
Keep it separate from the fictional draft. Work through these steps:

1. Record the actual date and time zone, target URL, run mode, case, tool and version if known. State the permitted scope. Mark missing facts **not supplied**.
2. List real preconditions: running mode, chosen account, fresh session and record ownership. For the Burp route, link both runs' `run.json`, `roster.json`, `worksheet.md` and `events.jsonl`.
3. Number only the steps you actually ran. Cite exact saved request/response files, HTTP history entries or screenshots. A server log alone does not prove use of Burp.
4. Compare the original request, the same route after the fix, and the valid owner's request. Record the actual account, method, order ID, status and relevant body. State any changed conditions.
5. Write the authentic result, even if blocked or incomplete. Do not call an unrun or changed-route test a fix. Give any next steps their own **proposed — not run** heading.
6. State a narrow impact, suggested correction, open questions and untested routes. Do not claim the whole app is secure.
7. Keep raw requests, tokens, screenshots and local paths private. Use redacted copies for a reviewer who may receive them. Do not publish the report or upload raw evidence.

Have a reviewer check each claim against the saved local evidence. Record the
review date and outcome only when it occurs. This guide has not performed
your local attempt or its review. Leave both statuses unrun or unassessed
until the evidence exists.

## Decision labels and model rules

Use one exact label per item. The helper checks these rules in order.

| Exact label | First condition that applies |
|---|---|
| `original-claim-not-supported` | No original response with the other record is shown |
| `retest-not-comparable` | The retest used another route |
| `retest-missing` | No non-owner retest status is supplied |
| `correction-not-demonstrated` | Non-owner retest is not 403, or still shows the other record |
| `legitimate-use-retest-missing` | No owner retest status is supplied |
| `access-blocked-but-owner-regressed` | Owner retest is not 200 |
| `bounded-correction-supported` | All prior checks pass for this case |

The model uses 403 for a refused non-owner request and 200 for its owner.
It requires a 200 plus the other record's body for the original issue.
A record body paired with another status is invalid in this model.
A claimed fix cannot change the verdict. Status codes describe responses;
they are not universal proof of correct access checks.

## Save your answer before the reveal

First write your claim in your own words. Then use the labels above to fill
`answers.json`. Keep each item ID. Put your reasons in `explanation` and exact
record, field or line references in the `evidence` list. Keep the three fields
`decisions`, `explanation` and `evidence`. JSON needs double quotes, with no
comments or trailing commas. Use `notes.txt` to record help and doubts.

Save this first attempt before opening the worked example, `reference/` or
the analysis. Then compare:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
```

The check matches exact text and checks that you wrote reasons and references.
It cannot judge those reasons. A spelling or format mismatch is not proof of
poor reasoning. A person must review your work. A match does not prove mastery.

Exit 0 means the command or comparison passed. Exit 1 means an answer is
missing or differs. Exit 2 means bad input or a file error. The default case is
`fixtures/guided.json`. Input paths start from the current folder.
The `--out` path starts from this lab folder.

## Input rules

Each case has these fields: `schema_version`, `lab_id`, `case_id`, `title`,
`synthetic`, `context`, `data` and `artifacts`. Version is 1.
`synthetic` must be true. The three fixtures show the full data shape.
The helper rejects missing or extra fields, repeated IDs, empty required text,
wrong types and choices it does not support. Numbers must be whole numbers;
true and false do not count as numbers. Lists hold at most 20 unique entries.
Row lists hold 1-20 rows. The helper leaves the case unchanged.

## Keep evidence and clean up

Keep the case, supplied files, first draft, answers and notes. Put corrections
in a new draft. Mark the stage: first attempt, prompted, corrected,
independently reviewed or recall attempted. Mark any check you did not run.
Keep private evidence private.

Attempt files stay in ignored `run/`. The offline helper changes no host
settings. To clean up, close the editor. Save the evidence you need, then remove
only the attempt folder you made. Keep fixtures and private originals.

Give a reviewer your question, exact evidence references, draft, one limit and
one next action. Do not invent a result.

## Maintainer checks

```text
python test_lab.py
python lab.py verify
```

These check the offline helper and three worked reference cases. They do not
prove that a learner did the writing task or a real test.

## Limits and sources

The starter transcript is authored training data. Its checks do not prove a local attempt was done. Even a completed retest covers only its route and conditions.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [NIST SP 800-115, Appendix B and section 8](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf) - Scope, agreed limits and reporting.
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) - Identity and permission are separate checks.
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - Useful evidence and sensitive fields to exclude.
