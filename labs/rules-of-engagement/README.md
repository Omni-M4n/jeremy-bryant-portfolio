# Write the rules before a lab

You agree to read a toy computer log for half an hour. Does that also let you change its settings? Write the limits before you touch a system.

## Before you begin

Know what ownership and permission mean. Allow 25 minutes.

Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

Scope means the exact work allowed. An owner can approve work they control. A stop condition is a reason to pause. Evidence is what you keep to support a claim.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

1. Read the case. Fill `scope-template.md` in your attempt folder.
2. Name the fictional owner role and purpose. List the included and excluded targets.
3. List allowed and excluded actions, the time window and the stop contact.
4. State who may read the evidence, how long to keep it and when to review deletion.
5. Keep your draft approval as **pending**. The case assumes fictional approval for its requests. Your draft gives no real authority.
6. Assess each request. Name one excluded target. Explain why knowing its name gives no permission.

If an owner, time zone or contact detail is absent, write **not supplied**.
Add a question for the owner. Do not invent approval or a contact.

## Decision labels and model rules

The helper first checks that inputs are valid. It then checks the rules below
in order. Stop at the first rule that applies.

| Exact label | When it applies |
|---|---|
| `stop-and-contact-owner` | A stop is active |
| `do-not-start-plan-incomplete` | Ownership, isolation or approval is false |
| `outside-target-scope` | The exact target is absent from the plan |
| `outside-activity-scope` | The action is absent from the plan |
| `outside-time-window` | The request falls outside the time window |
| `within-written-plan-only` | All those checks pass; paper result only |

Minutes run from midnight on one fictional day. The start minute is included.
The end minute is excluded. Only `read-config` and `read-log` may be approved.
A request may name another action so you can reject it.

Targets must be lowercase ASCII hostnames ending in `.test`.
ASCII means plain English letters, digits and the listed symbols here.
Each name part has 1-63 letters, digits or interior hyphens.
The whole name has at most 253 characters. For example, `logs.training.test`
is a host name. URLs, ports, paths, query strings, fragments, spaces and a
trailing dot are not allowed. Names must match exactly. A plan for
`training.test` does not include `logs.training.test`.

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

This is a review of a fictional written plan. It grants no permission and starts no test.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [NIST SP 800-115, Appendix B and section 8](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf) - Scope, agreed limits and reporting.
- [NIST IR 8286A Rev. 1](https://csrc.nist.gov/pubs/ir/8286/a/r1/final) - Risk scenarios, likelihood, impact and registers.
