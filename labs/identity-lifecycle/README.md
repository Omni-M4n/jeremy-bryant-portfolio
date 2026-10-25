# Reconcile joiner, mover and leaver access

Turn a dated staff change into a list of access changes. Keep the access needed for new duties. Remove access that is no longer needed. Check when a short-term handover rule ends.

**Time:** Allow 30-45 minutes for your first pass. Try the recall task on another day.
**Before you start:** You need to open files and edit a small JSON worksheet. JSON stores named fields and lists as text. Basic network and security terms will help. You do not need work experience, a cloud account or coding skills. You will not change code.

## Key words

A **joiner** is starting a role. A **mover** is changing duties. A **leaver** must lose access. An **entitlement** is one named item of access. A **delta** is the change from current access to target access. The **target** is the access the person should have. An **exception** allows a specific, approved break from the usual rule for a limited time. A **set** is a group of items with no repeats.

## Evidence and exact rules

The `data` field has a review date, `as_of`, in `YYYY-MM-DD` form. It also has a `people` list that must not be empty. Each person has `id`, `event`, `effective_on`, `current`, `required` and `exceptions`. The event must be `joiner`, `mover` or `leaver`. Access lists use unique lowercase labels.

An exception has just `access`, `approved_by` and `expires_on`. Only movers can have exceptions. Each one must name current access that is absent from `required`. It must name an approver with a nonempty ID. Its end date must be on or after the move date. Leavers must have an empty `required` list and no exceptions. Bad dates and unknown fields fail the check.

Dates are whole UTC days. UTC is the time standard used here. An event is due when `effective_on <= as_of`. This means its start date is on or before the review date. An exception still works on its end date. Here, "active-exceptions" means exceptions that have not expired. They affect the target only once the move is due.

| Situation | Target access |
| --- | --- |
| Due joiner | Required access. |
| Due mover | Required access plus handover exceptions that have not expired. |
| Due leaver | No access. |
| Future joiner | No access. Propose removal of early access. |
| Future mover or leaver | Current access. The event is not due yet. |

Use this exact syntax for each person: `add:ITEMS;remove:ITEMS;retain:ITEMS`. Each `ITEMS` is a list sorted from A to Z. Put commas between items, with no spaces. Use the literal word `none` for an empty list.

- The items to add are `target - current`. These are needed but not held yet.
- The items to remove are `current - target`. These are held but no longer needed.
- The items to retain are `current intersection target`. These are in both sets.

For example, `add:new-queue;remove:old-queue;retain:mail` has valid syntax. The word `none` means an empty set. It is not an access item.

## Run the exercise

From the repository root, enter this folder with `cd labs/identity-lifecycle`.

Use Python 3.10 or newer. On Windows, you may use `py` in place of `python` if it is your installed launcher. You do not need to install packages or set up an account or billing. All commands run offline. They change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any `.txt` evidence files. Open the blank `run/attempt-01/answers.json` worksheet. Fill in each decision with an exact label from the rules above. Write your own reason for each choice. In `evidence`, cite record IDs or line numbers from this case. Use `notes.txt` to record your first prediction, doubts and any help used.

Save your prediction before you run these commands:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has just three fields:

- `decisions` is an object. It pairs each record ID with your chosen label.
- `explanation` is text. Write why you chose those labels.
- `evidence` is a list of text references. You could name a record ID and its field. Use IDs from your case. Do not invent them.

`check` compares the decision labels. It also checks that you filled in the written fields. A person must judge whether those words are right. `verify` checks the supplied test cases. It does not assess your skill.

The exit code tells you what happened. Code 0 means success or a match. Code 1 means a mismatch or blank written fields. Code 2 means invalid input. If you omit `--case`, the command uses the guided case beside the script. Input paths start from your current terminal folder. The `--out` path starts from this lab folder. It must name a new folder below `run/`.

Use fresh folders for the next cases:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with your chosen folder. Edit practice copies only. Do not overwrite the supplied fixtures or reference answers. Fixtures are the starting cases.

## Deliverable and handover

Save a filled worksheet and a short evidence note for each case. Include your first prediction and any change to it. State what is still unclear. Name one next check that these files cannot answer. Record any help used, including the worked example.

Ask a reviewer: "Can you reach my decision from these record IDs? Which claim goes beyond the evidence?" Your skill at doing this alone is still **unassessed**. A matching output does not prove skill, a qualification or work experience. These are made-up practice cases. They are not work for assessment.

## Limits

This made-up policy does not change a directory or prove who approved an exception. It does not handle active sessions or access gained through groups. It does not disable accounts or deal with leave, urgent departures or asset ownership changes. A future mover keeps current access in this model. Any separate breach of the normal access rules needs its own review.

## Primary references

The official guide describes joiners, movers, leavers and time-based rules. This lab's set rules are made up for practice. So is its rule that an exception works through its end date.

- [Microsoft: lifecycle workflows](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)

The links are optional extra reading. They were checked on 2026-10-23. The lab does not fetch them. Read [the worked example](WORKED-EXAMPLE.md) after you save your prediction. Use [the drills](DRILLS.md) for more practice.
