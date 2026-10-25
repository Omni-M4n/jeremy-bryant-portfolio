# Turn a concern into an owned action

A loan laptop is missing. A score alone does not tell anyone what to do. Write who owns the concern, what they will change and when they will review it.

This extends `vulnerability-prioritisation`. You assign an owner to a proposed response. You set review dates and explain the risk left after that response.

## Before you begin

Complete `vulnerability-prioritisation` and `data-classification`. Allow 30 minutes.

Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

Risk combines the chance of harm and how large it could be. Treatment means a response. Reduce means limit harm or its chance. Avoid means stop the risky activity. Transfer means agree who carries a set duty or cost. Accept means an owner agrees to keep the risk. Residual risk is the risk left. An assumption is an unproved idea.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

1. Read the case and `risk-notes.txt`. Fill `risk-template.md` in your attempt folder.
2. Write: if this event occurs, this asset could suffer this harm.
3. Use the rubric below. Give an evidence line for each score. The supplied scores are proposals. Support or challenge them with facts about the chance and harm.
4. Assess the treatment already in the JSON. In your register, justify it or propose an alternative. Name the owner, action, due date, risk left and open assumption.
5. Add physical, process and technical controls. These are barriers, work rules and device settings that could limit harm. Explain what each would change.
6. Draft a reporting action, marked **NOT SENT**. Record the last known time and place. Name the fictional service desk's known internal route. Let the owner decide how to contain harm.

For absent facts, write **not supplied** and add a question. Do not confront a
visitor, test a real person or remotely wipe a device.

The helper uses the JSON's scores and treatment. Put that result in
`answers.json`. Keep your own proposal in the register. A reviewer may accept
another score or treatment if you give sound reasons from the same rubric.
An exact-text mismatch alone does not make those reasons wrong.

## Decision labels and model rules

Use this invented rubric only. It gives no measured chance of an event.

| Score | Likelihood: chance in this case | Impact: harm in this case |
|---|---|---|
| 1 | Needs an unusual chance | Small local delay |
| 2 | Has a plausible chance | Team disruption or limited record exposure |
| 3 | Has repeated chances | Serious service loss or sensitive record exposure |

Multiply likelihood by impact. Scores 1-2 are low, 3-5 medium and 6-9 high.
Review is due on its date. Use real dates in exactly `YYYY-MM-DD` form.
Basic dates, week dates and timestamps are not supported.

Each answer has four parts: `band;treatment;review;residual`.
Join them with semicolons and no spaces. Use the supplied values for this check.

| Part | Exact choices and rules |
|---|---|
| Band | `low`, `medium` or `high`, from the original score |
| Treatment | Copy the proposed `reduce`, `avoid`, `transfer` or `accept` |
| Review | `owner-acceptance-needed` if treatment is `accept` and acceptance is false; else `review-due` if review is on or before `as_of`; else `review-planned` |
| Residual | `supported-in-case` when `control_verified` is true; else `projection-only` |

`likelihood` and `impact` describe the starting state. Fields ending in `_after`
describe the proposed state. Both proposed scores must stay the same or fall.
Choosing `accept` cannot lower either score. It also needs an owner decision.

`control_verified` says whether the fictional packet includes a control check.
The helper does not judge its coverage or your reasons for a score.
State what the check covers and what is still missing. A projected lower
score does not prove less risk. These notes describe no real device test.

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

Scores are a teaching scale. Proposed controls do not prove a lower real risk.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [NIST IR 8286A Rev. 1](https://csrc.nist.gov/pubs/ir/8286/a/r1/final) - Risk scenarios, likelihood, impact and registers.
- [NIST SP 800-61 Rev. 3](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf) - Response roles and communication.
