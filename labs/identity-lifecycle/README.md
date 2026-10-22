# Reconcile joiner, mover and leaver access

Turn a dated staffing change into an access delta. Preserve legitimate new duties, remove stale access, and explain why an approved handover exception ends at a specific date.

**Time:** 30-45 minutes for a first pass; use the later recall task on another day.
**Prerequisites:** Basic file navigation, editing a small JSON worksheet, and introductory networking/security vocabulary. No professional security experience, cloud account, coding background or programming changes are required.

> **Vocabulary:** **Joiner**: someone starting a role. **Mover**: someone changing duties. **Leaver**: someone whose access must end. **Entitlement**: one named access item. **Delta**: the difference between current and target access. **Exception**: a limited, approved departure from the normal target.

## Evidence and exact semantics

`data` has `as_of` (`YYYY-MM-DD`) and nonempty `people`. Each person has
`id`, `event` (`joiner`, `mover`, `leaver`), `effective_on`, `current`, `required`,
and `exceptions`. Access lists contain unique lowercase labels. An exception
has exactly `access`, `approved_by`, and `expires_on`. Only movers can have
exceptions; each must name existing access that is absent from `required`, have
a nonempty approver ID, and expire on or after the move date. Leavers must have
empty `required` and no exceptions. Invalid dates and unknown fields fail.

Dates are whole UTC days. An event is due when `effective_on <= as_of`.
Exception expiry is inclusive: an exception expiring on the review day remains
valid through that day. Here "active-exceptions" means unexpired exceptions;
they contribute to the target only when the move is due.

| Situation | Target access |
| --- | --- |
| Due joiner | Required access. |
| Due mover | Required access plus unexpired handover exceptions. |
| Due leaver | Empty. |
| Future joiner | Empty; early access is proposed for removal. |
| Future mover or leaver | Current access; the future event is deferred. |

For each person use the exact decision syntax
`add:ITEMS;remove:ITEMS;retain:ITEMS`. Each `ITEMS` is a comma-separated,
alphabetically sorted list with no spaces, or the literal `none`. The three
sets are `target - current`, `current - target`, and `current intersection target`.
For example, `add:new-queue;remove:old-queue;retain:mail` is valid syntax.
The reserved output word `none` means an empty set, not an entitlement.

## Run the exercise

From the repository root, enter this folder with `cd labs/identity-lifecycle`.
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

This fictional policy does not implement directory changes, approval authenticity, sessions, access inherited through groups, account disablement, leave of absence, emergency termination or asset ownership transfer. A future mover keeps current access in this bounded model; separate baseline violations would need another review.

## Primary references

The official overview distinguishes joiner, mover and leaver processes and time-based conditions. The set operations and inclusive exception rule here are explicit fictional practice policy.

- [Microsoft: lifecycle workflows](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)

Links are optional further reading, checked 2026-10-23. Running this lab does
not fetch them. See [the worked example](WORKED-EXAMPLE.md) after your prediction
and [the drills](DRILLS.md) for varied practice.
