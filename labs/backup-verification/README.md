# Backup scope, freshness and synthetic restore verification

Evaluate retained scope and recovery-point age, then actually decode and hash tiny fictional backup payloads in memory against a supplied manifest.

This is an original, fictional, offline exercise for an introductory security learner. It is independent practice, not copied coursework or a claim of professional experience. Completion and competence remain unassessed.

## Before you start

Allow **30-45 minutes**: 5 minutes reading, 10 inspecting and predicting, 10 checking and explaining, and 5-20 for a changed or independent case. You need Python 3.10+ (standard library only), a terminal and a text editor. Comfort opening files, reading a small table and basic evidence notes is enough; programming, administrator rights, a Linux installation and cloud accounts are unnecessary. Previous introductory network or Wireshark practice is useful but not required.

> **Vocabulary:** RPO: recovery point objective, the maximum acceptable age of a recovery point. RTO: recovery time objective, a different measure of restoration duration. Retention: how long a copy is kept. SHA-256: a digest used here to compare exact bytes. Restore test: exercising recovery and checking the result, with scope stated precisely.

## Evidence and exact rules

The case JSON is the single authoritative input. Fixtures are guided.json, changed.json and challenge.json. All data is synthetic; artifacts is empty to avoid competing editable copies. Edit only a prepared run copy. The analyser is a pure calculation and never executes evidence text.

data contains recovery_time (UTC seconds), integer rpo_hours from 0-168, required_sha256 mapping synthetic .txt/.csv basenames to SHA-256 values, and backups. Each backup has ID, captured_at, retained_until and payload_base64. Payload names must be a subset of required scope. Invalid base64, future captures and invalid retention periods are rejected. The manifest is supplied authority; it is not read from your disk.

For each copy decode supplied payloads in memory and compute SHA-256. Evaluate at recovery_time; retention expires exactly at retained_until. Decision precedence is retention-expired, required-scope-missing, restore-bytes-mismatch, rpo-exceeded, then qualified-synthetic-copy. Age equals recovery time minus capture time in seconds. Age exactly equal to RPO meets the age limit. The recovery answer is `select:<backup-id>` for the most recent qualifying copy, replacing `<backup-id>` with its exact ID (for example, `select:copy-a` for a qualifying copy named copy-a). If captures tie, the lexically greatest ID wins using case-sensitive string order, not numeric order. If none qualifies, the answer is `no-qualified-copy`. Earlier failures take precedence in the decision, but observations expose every measured scope/hash/age result.

## Run the exercise

Open a terminal in this lab folder. Use your Python command (`python`, or `py -3` if that is how Python is installed). Commands below use `python` consistently.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
python inspect_payloads.py --case run/attempt-01/case.json
```

The inspector prints each embedded file's decoded UTF-8 text, exact bytes as hexadecimal, byte length and measured SHA-256. Non-UTF-8 bytes have null in decoded_utf8; the hexadecimal bytes remain exact. It prints no matches, recovery decisions or answer labels, and does not call the analyser. It decodes only the embedded fictional payloads in memory, writes no recovered files and executes no payload text. Exit 0 means measurements were produced; exit 2 means invalid input or a filesystem problem. The default case is the guided fixture; an explicit --case path is relative to your terminal directory.

Compare the inspector's sha256 for each backup ID/file with required_sha256 in case.json. Check the manifest's required filenames against the files actually measured, then calculate age and retention from the case timestamps. Record these measurements before predicting whether each copy qualifies. In run/attempt-01/answers.json, fill each decision with an exact label from the rules; add an explanation and evidence references such as b1/notes.txt and its measured digest. In notes.txt, separate observation, interpretation, uncertainty, next check and help used. Save your prediction before opening the answer.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py test_inspect_payloads.py
python lab.py verify
```

For changed/challenge use the corresponding attempt folder in show, inspect_payloads.py, analyse and check. Run the inspector before saving the prediction and before analyse. prepare refuses an existing output folder. --out is relative to this lab and must be below run/; explicit input paths are relative to your terminal directory. analyse/show default to the guided fixture if --case is omitted. Exit 0 means command success or decision match; 1 means differences/incomplete written fields; 2 means invalid input or a filesystem problem. The checker verifies decision fields and the presence of writing, not the quality of reasoning. verify checks shipped examples, not learner mastery.

## Deliverable and limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. Deliver a short handover: the question, your conclusion, two precise evidence references, one alternative explanation or limitation, and the next evidence you would request. State whether you used the worked example and whether you completed a fresh case unaided. Do not describe an automated match as assessment or professional experience.

Only embedded fictional payloads were decoded into memory and hashed. No real backup, disk file or application was restored. Retention is evaluated from supplied metadata; embedded evidence of an expired copy does not establish its real availability. Media health, encryption keys and full recovery procedures are outside scope.

Use WORKED-EXAMPLE.md after making a first prediction, and DRILLS.md for progressively less support. Do not use these rules as an operational security verdict or modify a real host as part of this exercise.

## Primary references

The following documentation supports the underlying concepts; the tiny schema and explicit teaching rules above are specific to this lab. Links were checked during authoring on 23 October 2026. Running the lab needs no internet connection.

- [NIST contingency planning guidance, updated revision](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
