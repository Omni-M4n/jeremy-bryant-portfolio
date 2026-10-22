# Worked example: a notice update and three unexplained changes

This supplied walkthrough uses the `mixed` variant and seed `23`. It is not a
record of independent learner work. All names and file contents are fictional.

## 1. Establish the scope

```console
python lab.py generate --variant mixed --seed 23 --run run-walkthrough
```

Read `run-walkthrough/scenario.json` and `run-walkthrough/approvals.json` in a
text editor. The supplied exercise history says that `reference/` was checked
before the change window. A fictional owner approved the notice's opening time
changing from `09:00` to `10:00`. The approval records the exact before/after
file hashes. No approval is supplied for the config, temporary note, or archive.

The scenario and approvals are the exercise's authority. In real work, their
source, custody, and protection would also need verification.

## 2. Create the measurement

```console
python lab.py baseline --run run-walkthrough
```

The baseline contains four file records. `docs/notice.txt` is 39 bytes before
and after its edit: a size-only check would miss that change. SHA-256 compares
the bytes, so equal length does not prevent detection.

Creating a baseline is only measurement. Confidence comes from the history and
protection of its source. Do not create a new baseline from current files merely
to remove findings.

## 3. Interpret the comparison

```console
python lab.py check --run run-walkthrough
python lab.py check --run run-walkthrough --json
```

The result is `REVIEW NEEDED`, exit code `1`. Its baseline status is
`matches-exercise-anchor`.

| Path | Observation | Assessment and next action |
| --- | --- | --- |
| `docs/notice.txt` | Modified; same byte length, different hash | Exact hashes match `CHANGE-000023`; record as the approved update. |
| `docs/contact.txt` | Unchanged | No difference from this baseline; make no broader security claim. |
| `config/service.txt` | Modified: `remote_access=disabled` became `enabled` | Unexpected. Preserve evidence and ask the fictional owner whether a change record is missing. This text does not enable a real service. |
| `docs/temporary-note.txt` | Added | Unexpected. Establish its source and purpose before deciding what action is appropriate. |
| `reports/archive.txt` | Deleted | Unexpected. Confirm the retention requirement and whether removal was authorised; do not restore automatically. |

There is **one unchanged file, one approved change, and three unexpected
changes** across five observed paths. The count includes the missing baseline
file and the new current file. The current folder itself contains four files.

A suitable short finding is:

> The supplied baseline matches the exercise anchor. The notice update matches
> its exact approval. The config edit, new temporary note, and missing archive
> have no matching change record. I would preserve these observations and check
> the owner's records before deciding on recovery or escalation. Hashes establish
> differences from this baseline; they do not identify the actor or prove an attack.

## 4. Test a misleading alternative

```console
python lab.py baseline --run run-walkthrough --source current --name baseline-current.json
python lab.py check --run run-walkthrough --baseline baseline-current.json
```

This comparison shows four unchanged current files and no unexpected differences.
However, its baseline status becomes `does-not-match-exercise-anchor`, and it
still exits `1`. The new measurement has absorbed the changes, so it cannot
establish the earlier state. Its unused approval also shows that the expected
notice transition was not observed in this comparison.

The separate `suspect-baseline` variant is harder: no independent anchor exists.
The written requirement and the source history must be considered even when
the file comparison itself looks uneventful. Continue with [the drills](DRILLS.md).
