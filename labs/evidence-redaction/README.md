# Make a safe copy of a synthetic excerpt

A log can show a refused request and still contain a token or personal detail. Make a separate copy. Keep the useful result and remove the supplied fake sensitive values.

This extends `secret-handling`. You make a redacted copy, check it and explain which claims it can still support.

## Before you begin

Complete `secret-handling` and `evidence-custody`. Allow 30 minutes. Use only the synthetic text shipped here.

Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

Redaction removes data from a copy. A hash is a file fingerprint. A private mapping links the copy to its source. A placeholder shows where data was removed. A seed here is a fake value chosen for removal.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

1. Read the case. Write a plan in `redaction-template.md` in your attempt folder.
2. State the claim to support. Name the fields needed for it and fields to remove. Keep `record.txt` private and untouched.
3. Save your first plan and predictions. Then run the copy command below.
4. Open `excerpt.txt` in a text editor. Search for every value listed in `remove`. None may remain. Check each fragment listed in `keep`.
5. Read all events, not just one matching line. Does each event support, limit or conflict with your claim? If there are two events, cite both.
6. Check relationships. Can a reader still tell repeated use of one value from use of two values? Can they tell events and results apart? Do the placeholders preserve the links your claim needs?
7. Check remaining clues, such as times or rare events. They may still reveal private facts. Keep the receipt and case private: they link the copy to its source.

Write the human checks in your private checklist. Use **not supplied** for
missing context. A match label does not prove the whole claim is true or
the copy is safe to share. A person must review the final copy before any
separately approved publication.

After saving the plan, create the copy:

```text
python practice.py --run run/attempt-01
```

This writes fresh `excerpt.txt` and `redaction-receipt.json` in the prepared
folder. It refuses changed originals, linked paths and existing outputs.
It checks the original hash before and after, then reads the copy back.
For another run, prepare a fresh attempt folder. Do not overwrite the first copy.

## Decision labels and model rules

The helper has two fixed check labels for valid inputs. They describe text
checks, not a review of your claim. Fill the matching worksheet checks using
these exact values.

| Exact label | Narrow meaning |
|---|---|
| `seeded-values-removed` | All strings listed in `remove` are absent from the copy |
| `listed-claims-preserved` | All fragments listed in `keep` are still present |

The same labels appear in every valid case. They do not decide whether an
event supports your claim. Your reasons, event references and relationship
checks are the main human review task.

`remove` lists exact strings to remove. `keep` lists exact text fragments to
retain. Each distinct removed value gets one marker, `[REMOVED-N]`.
The number follows its order in `remove`. Repeated occurrences get the same marker.
All occurrences are replaced. Missing strings, overlaps, reserved markers and
keep/remove conflicts are refused.

The source must be `record.txt`, start with `SYNTHETIC TRAINING RECORD` and
use UTF-8 text. UTF-8 is a text file format. The source limit is 100,000 bytes.
This tool cannot inspect images, PDF layers, file metadata or unknown secrets.
A hash checks bytes, not truth or privacy.

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

Exact text replacement is not a general secret detector. A person must check the context, hidden data and final copy.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - Useful evidence and sensitive fields to exclude.
- [OAIC APP 11 guidance](https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-11-app-11-security-of-personal-information) - Protection and retention exceptions.
