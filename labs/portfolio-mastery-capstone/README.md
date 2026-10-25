# Explain a fresh case to a reviewer

You can follow an example and still be unsure when facts change. Ask a reviewer for a fresh case. Save your first explanation. Show which facts changed your mind.

This extends `dns-triage`, `login-triage`, `access-review` and `vulnerability-retest`. You combine evidence from completed tracks, defend a narrow claim and try again later without the guide.

## Before you begin

Finish an independently reviewed network, endpoint, web or identity track.
Also complete `finding-report`, including its required local-evidence stage,
and `evidence-redaction`. Before the fresh combined case, have completed work
from each of the two or three tracks it will use. The reviewer checks this
readiness; reading a guide alone does not count.
Allow 40 minutes now and 10 minutes for recall after 2-7 days.


Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

Transfer means using a skill on new facts. A rubric lists what a reviewer looks for. A help log records hints and sources used. Recall means explaining again later without the guide. DNS looks up a name. HTTP is used for web requests and responses.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

1. Read the supplied practice case. Fill `portfolio-template.md` in your attempt folder.
2. Save a dated first answer before hints. Give a short report, evidence list, help log, limits and next action.
3. Treat the three shipped cases as rehearsal. Then follow [REVIEWER.md](REVIEWER.md) for the required fresh case.
4. The reviewer must combine fresh facts from two or three completed tracks. Renaming a shipped case is not enough. Keep the answer key closed until the first attempt is saved.
5. Keep corrections in a separate file. Leave review status **unassessed** until a person reviews the evidence.
6. Arrange your own recall attempt after 2-7 days. This package creates no reminder. Leave recall status **unassessed** until you attempt it.

Mark missing facts **not supplied**. The helper cannot certify you as ready
or fill a learner's results. Do not use a match or the package name as proof
of mastery.

## Decision labels and model rules

Use one exact label per claim.

| Exact label | Meaning |
|---|---|
| `supported-within-case` | The supplied facts support this narrow claim |
| `revise-claim` | The supplied facts conflict with the claim |
| `collect-bounded-evidence` | Needed evidence is missing or cannot settle the claim |

The helper covers two or three tracks in each case. These are its rules:

1. A DNS answer supports name resolution only. The `page-works` claim needs HTTP 200 in this model. Another supplied status conflicts with that claim. A missing status leaves it incomplete.
2. Failed sign-in counts and a later success cannot prove who typed. They cannot confirm an intruder, even with a report of a typing error.
3. An absent `editor` role supports only that role-table claim. Account counts alone cannot prove that all permissions are correct.
4. A comparable non-owner 403 and owner 200 support one bounded correction. Another pair of observed statuses conflicts with it. A missing status or changed route leaves it incomplete.

The reviewer creates fresh facts and keeps the answer key separate. A person
must judge your claim, evidence, limits and next check.

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

The helper checks a small set of supplied facts. A fresh case, human review and later recall are required. Mastery is not assessed.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [NIST SP 800-115, Appendix B and section 8](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf) - Scope, agreed limits and reporting.
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) - Identity and permission are separate checks.
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - Useful evidence and sensitive fields to exclude.
