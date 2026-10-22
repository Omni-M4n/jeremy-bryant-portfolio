# Trace dummy secret exposure through config, diffs and logs

Find an explicit dummy value across current configuration, retained changes and output logs. Explain exposure audiences and why removing a line is not the same as invalidating an exposed credential.

**Time:** 30-45 minutes for a first pass; use the later recall task on another day.
**Prerequisites:** Basic file navigation, editing a small JSON worksheet, and introductory networking/security vocabulary. No professional security experience, cloud account, coding background or programming changes are required.

> **Vocabulary:** **Secret**: a value granting access. **Revocation**: making a credential unusable. **Rotation**: replacing a credential and retiring the old one. **Diff**: lines added or removed by a change. **Redaction**: hiding a value in a displayed copy. **Exposure path**: an artifact and audience through which a value becomes visible.

## Evidence and exact semantics

All values are fake and deliberately begin `DEMO_ONLY_TOKEN_`. Do not replace
them with real credentials. `data.secrets` contains unique `id`, unique `marker`,
and `state` (`active` or `revoked`) for each dummy credential. A marker uses an
uppercase letter after the prefix and then uppercase letters, digits or
underscores. `data.files` contains unique `id`, `kind` (`config`, `diff`, `log`),
`audience` (`local`, `shared`, `public`), and a nonempty `lines` list. Each line
has at most 400 characters with no embedded newline; at most 100 lines per file.

Readable artifacts are `ID.txt` with the same lines and a final newline. The
analyser rejects mismatches between `data.files` and `artifacts`. When editing
a practice copy, update both representations; otherwise the evidence is
contradictory. Changing just a secret's `state` needs no artifact edit.

Only listed exact markers are matched, with no adjoining ASCII letter,
digit or underscore. This prevents `DEMO_ONLY_TOKEN_APP` from matching the
longer `DEMO_ONLY_TOKEN_APP_LONG`. All diff lines, including removed `-` lines,
remain readable exposure evidence. Locations use `filename.txt:Lnumber`,
one-based. Repeated occurrences on one line count as one location.

Use one exact string per secret ID:

| Decision | Meaning and priority |
| --- | --- |
| `not-seen-in-supplied-artifacts` | The listed value has no exact occurrence in these artifacts. |
| `confirm-revocation;clean-copies;review-use` | A listed revoked value remains visible; confirm invalidation, remove unnecessary copies and review prior use. |
| `contain;revoke-and-replace;clean-copies;review-use` | An active value appears in shared or public material; stop further exposure, invalidate/replace it with service continuity planning, clean retained copies, review use. |
| `relocate-before-sharing` | Active value appears only in local material; move it into the approved secret mechanism and prevent inclusion in shared output. |

Apply the first matching row. Real incident work can run several tasks in
parallel; the sequence stresses that cosmetic deletion cannot replace
revocation. Preserve necessary audit evidence under restricted access without
needlessly retaining live credentials. All proposed actions here are notes only.

## Run the exercise

From the repository root, enter this folder with `cd labs/secret-handling`.
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

This is an exact listed-marker exercise, not a complete secret scanner. It misses unlisted values, encoding, split values and other formats. A local-only finding may have a wider history not supplied here. No credential works, no endpoint is contacted, and no history or log is actually rewritten.

## Primary references

OWASP covers secret lifecycle, rotation, revocation, access control and auditing. The marker grammar and artifact audiences are deliberately small exercise conventions.

- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

Links are optional further reading, checked 2026-10-23. Running this lab does
not fetch them. See [the worked example](WORKED-EXAMPLE.md) after your prediction
and [the drills](DRILLS.md) for varied practice.
