# Give each record a handling rule

A booking reminder needs a booking code and an email address. It does not need a birthday. Build a register that shows what to keep and what to leave out.

## Before you begin

Complete `access-review` and `secret-handling`. Allow 30 minutes.

Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

Classification gives data a handling label. Retention means how long to keep it. A hold pauses disposal for a stated reason. Minimisation means collecting only what the task needs.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

1. Read the case. Fill `register-template.md` in your attempt folder.
2. For each row, name its owner role and purpose. List fields to keep and leave out.
3. Add its label, storage rule, reader roles, review date and sharing decision. Give a reason for each choice.
4. Draft one proposed exception. State its reason, approver role and expiry. Label it **proposed**, not approved.
5. Read the disposal statement for each case you attempt. Which listed copies does it cover? What does it leave uncertain?
6. Record the authorising role, date, method and checks only when supplied. Otherwise write **not supplied** and state what you need to ask for.

Keep every supplied file. This is a paper review; do not delete any record.
If a calendar review date is missing, do not make one from the supplied age.

## Decision labels and model rules

Each decision has four parts in this order. Join them with semicolons and no
spaces: `label;retention;sharing;receipt`. Select one value from each row below.
The format has no case IDs or case answers.

| Part | Exact choices and rules |
|---|---|
| Label | `restricted` for secret content; else `confidential` for personal content; else `public` for approved non-sensitive content; else `internal` |
| Retention | `retain-on-hold` when hold is true; else `disposal-due` when age is at least `retain_days`; else `retain-until-review` |
| Sharing | `share-as-approved` when the exact recipient role is in `allowed_receivers`; otherwise `do-not-share` |
| Receipt | `no-receipt` for `none`; `receipt-incomplete` for `primary-only`; `receipt-covers-listed-copies` for `all-listed-copies` |

These are the fictional team's labels. A hold takes priority over age.
Public approval cannot appear with personal or secret content.
A disposal receipt is allowed only when disposal is due and no hold exists.
All needed fields must be in the supplied field list.
The receipt label describes its stated scope. It proves no real erasure.

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

These handling rules are invented. They are not legal advice or proof of deletion.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [OAIC APP 3 guidance](https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-3-app-3-collection-of-solicited-personal-information) - Collect only fields needed for a purpose.
- [OAIC APP 11 guidance](https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-11-app-11-security-of-personal-information) - Protection and retention exceptions.
