# Trace dummy secret exposure through config, diffs and logs

Find a fake secret in settings, saved changes and logs. Check who could see each copy. Explain why deleting a line does not stop a stolen sign-in value from working.

**Time:** Allow 30-45 minutes for your first pass. Try the recall task on another day.
**Before you start:** You need to open files and edit a small JSON worksheet. JSON stores named fields and lists as text. Basic network and security terms will help. You do not need work experience, a cloud account or coding skills. You will not change code.

## Key words

A **secret** is a value that grants access. A **credential** is proof used to gain access, such as a token. **Revocation** makes it stop working. **Rotation** replaces it and retires the old one. A **diff** shows lines added or removed in a change. **Redaction** hides a value in a displayed copy. An **artifact** is a supplied evidence file. An **exposure path** is a file and audience through which someone can see a value.

## Evidence and exact rules

All values are fake. They start with `DEMO_ONLY_TOKEN_`. Do not replace them with real credentials.

The `data.secrets` list names each dummy credential. Each has a unique `id`, a unique `marker` and a `state`. State is `active` or `revoked`. A marker starts with the prefix above. Next comes an uppercase letter. Any later characters must be uppercase letters, digits or underscores.

The `data.files` list has a unique `id` for each file. It also has `kind`, `audience` and `lines`. Kind is `config`, `diff` or `log`. Audience is `local`, `shared` or `public`. The lines list must not be empty. It can have at most 100 lines per file. Each line has at most 400 characters and no newline within it.

The readable artifact is `ID.txt`. It has the same lines and a final newline. The tool rejects a mismatch between `data.files` and `artifacts`. If you edit the lines in a practice copy, update both forms. They must give the same evidence. If you change only a secret's `state`, no artifact edit is needed.

The tool matches only the exact listed markers. No ASCII letter, digit or underscore may touch the marker. ASCII is a basic set of text characters. Thus `DEMO_ONLY_TOKEN_APP` does not match part of `DEMO_ONLY_TOKEN_APP_LONG`.

All diff lines remain readable evidence. This includes removed lines marked with `-`. Locations use `filename.txt:Lnumber`. Line numbers start at 1. Two or more matches on one line count as one location.

Use one exact string per secret ID. Apply the first matching row:

| Decision | Meaning and priority |
| --- | --- |
| `not-seen-in-supplied-artifacts` | The listed value has no exact match in these files. |
| `confirm-revocation;clean-copies;review-use` | A revoked value is still visible. Confirm it cannot be used. Remove copies that are not needed and review past use. |
| `contain;revoke-and-replace;clean-copies;review-use` | An active value is in shared or public material. Stop further exposure. Plan how to keep the service working while you revoke and replace it. Clean retained copies and review use. |
| `relocate-before-sharing` | An active value appears only in local material. Move it into the approved secret store. Keep it out of shared output. |

Real response work may involve several tasks at once. This order stresses that hiding or deleting a value does not revoke it. Keep needed audit evidence under restricted access. Avoid keeping live credentials without a need. All proposed actions here are notes only.

## Run the exercise

From the repository root, enter this folder with `cd labs/secret-handling`.

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

This tool looks for listed markers. It is not a complete secret scanner. It misses unlisted values, encoded values, split values and other formats. A value seen only in a local file may have a wider past that is not shown here. None of these credentials work. The tool contacts no endpoint. It does not rewrite history or logs.

## Primary references

OWASP covers how to manage secrets through their life. It includes rotation, revocation, access rules and audits. This exercise uses small, fixed rules for marker text and who can see each file.

- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

The links are optional extra reading. They were checked on 2026-10-23. The lab does not fetch them. Read [the worked example](WORKED-EXAMPLE.md) after you save your prediction. Use [the drills](DRILLS.md) for more practice.
