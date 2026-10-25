# Worked example: a notice update and three unexplained changes

This supplied walkthrough uses the `mixed` variant and seed `23`. It is not a record of independent learner work. All names and file contents are made up.

## 1. Establish the scope

```console
python lab.py generate --variant mixed --seed 23 --run run-walkthrough
```

Read `run-walkthrough/scenario.json` and `run-walkthrough/approvals.json` in a text editor. The supplied history says `reference/` was checked before the change window. A fictional owner approved a change to the notice's opening time. It goes from `09:00` to `10:00`. The approval records the exact before/after file hashes. There is no approval for the config, temporary note or archive.

The scenario and approvals set the rules for this exercise. In real work, you would also check their source. You would check who held them and how they were protected.

## 2. Create the measurement

```console
python lab.py baseline --run run-walkthrough
```

The baseline has four file records. `docs/notice.txt` is 39 bytes before and after the edit. A check of size alone would miss this change. SHA-256 is based on the bytes. It can detect a change even when the length stays the same.

Making a baseline is only a measurement. Trust comes from its source history and protection. Do not make a baseline from current files just to remove findings.

## 3. Interpret the comparison

```console
python lab.py check --run run-walkthrough
python lab.py check --run run-walkthrough --json
```

The result is `REVIEW NEEDED`, exit code `1`. Its baseline status is `matches-exercise-anchor`.

| Path | Observation | Assessment and next action |
| --- | --- | --- |
| `docs/notice.txt` | Modified; same byte length, different hash | Exact hashes match `CHANGE-000023`; record as the approved update. |
| `docs/contact.txt` | Unchanged | No difference from this baseline; make no broader security claim. |
| `config/service.txt` | Modified: `remote_access=disabled` became `enabled` | Unexpected. Preserve evidence and ask the fictional owner whether a change record is missing. This text does not enable a real service. |
| `docs/temporary-note.txt` | Added | Unexpected. Establish its source and purpose before deciding what action is appropriate. |
| `reports/archive.txt` | Deleted | Unexpected. Confirm the retention requirement and whether removal was authorised; do not restore automatically. |

There is **one unchanged file, one approved change, and three unexpected changes**. That covers five observed paths. The count includes the missing baseline file and the new current file. The current folder itself has four files.

A suitable short finding is:

> The supplied baseline matches the exercise anchor. The notice update matches its exact approval. The config edit has no matching change record. Neither do the new temporary note and missing archive. I would preserve what I found and check the owner's records. Then I would decide on recovery or escalation. Hashes show differences from this baseline. They do not identify the actor or prove an attack.

## 4. Test a misleading alternative

```console
python lab.py baseline --run run-walkthrough --source current --name baseline-current.json
python lab.py check --run run-walkthrough --baseline baseline-current.json
```

This comparison shows four unchanged current files and no unexpected differences. Its baseline status becomes `does-not-match-exercise-anchor`. It still exits `1`. The new baseline has absorbed the changes. It cannot prove the earlier state. Its unused approval shows another limit. This comparison did not observe the expected notice change.

The separate `suspect-baseline` variant is harder. It has no independent anchor. Check the written requirement and source history even if the file comparison looks uneventful. Continue with [the drills](DRILLS.md).
