# Explain what is known and what comes next

Several staff see repeated sign-in prompts. They need one clear action. The technical team needs evidence and open questions. Draft both messages without guessing the cause.

## Before you begin

Complete `login-triage` and `timeline-analysis`. Allow 30 minutes.

Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

Confirmed means supported by the supplied evidence. A hypothesis is a possible cause. A handover helps the next person continue. An action owner is the role that must do a task. An audience is the group allowed to receive a statement.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

1. Read the case. Fill `communications-template.md` in your attempt folder. Mark every section **NOT SENT**.
2. Make a fact, hypothesis, unknown and action register. Keep each source, audience and owner. Mark absent facts **not supplied**.
3. Draft a technical handover with evidence and open checks. Draft a manager update with effects and the next decision. Name any gaps instead of making up details.
4. Choose a staff draft or a justified hold. A staff draft needs a staff-approved confirmed fact, one staff action and the intended recipients.
5. If all three are present, write 40-70 calm words. Use only material for that audience. Give the known internal route `service-desk.test` and the exact next-update time.
6. If any part is missing, write **HOLD - NOT SENT**. Name the gap and evidence IDs. Draft an unsent request to the stated owner for the missing wording or recipient decision before the next update.

The route is already known to the fictional staff. Add no sign-in link or
password request. A staff label does not permit a notice to the whole
organisation. Keep manager facts within that audience. Do not turn a guess
into a fact or give staff an action meant for the technical team.

## Decision labels and model rules

The supplied status states each claim's evidence level. The helper does not
find out what is true. Every statement, including an action, stays with its
named audience. Use one exact label below for each statement.

| Status and audience | Exact label |
|---|---|
| `confirmed`, `staff` | `use-confirmed-fact-for-staff` |
| `confirmed`, `technical` | `use-confirmed-fact-for-technical` |
| `confirmed`, `manager` | `use-confirmed-fact-for-manager` |
| `hypothesis`, any allowed audience | `label-hypothesis-do-not-present-as-fact` |
| `unknown`, any allowed audience | `state-unknown-and-next-check` |
| `action`, any allowed audience | `assign-action-and-owner` |

You may simplify words for their audience. Keep the meaning and degree of
certainty. Moving a statement to another audience needs new approval in
the fictional packet. A guess must stay labelled. An unknown needs a next
check; an action needs an owner. State gaps without inventing facts.

Time is minutes after midnight on one fictional day. The next update must
be later that day. The only route is the known fictional service desk.
The helper labels each statement. A person must judge whether the staff
draft has enough facts, a permitted audience and one clear action.
No helper result permits sending anything.

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

These are drafts about fictional facts. No message is sent. No real incident, breach or person is assessed.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [NIST SP 800-61 Rev. 3](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf) - Response roles and communication.
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - Useful evidence and sensitive fields to exclude.
