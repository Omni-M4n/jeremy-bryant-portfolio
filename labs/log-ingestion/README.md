# Import a small log file

A sign-in list can use two names for the same field. Its clock may also use a
different time zone. Can you import the list without losing or counting a row twice?



This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise login-triage and timeline-analysis first.
No administrator rights, account, installation, live scan, or security changes are needed.

**Words:** A log is a saved event record. Import means copy records into a tool.
Normalise means use one agreed format. UTC is the shared time reference used here.
A time offset says how far a local clock is from UTC. A rejected row is kept aside.

## Question and exact rules

The source is artifacts.records.txt. data.format is csv or json. CSV has exactly
event_id,timestamp,user,status in that order. Map those fields to id,time,account,
outcome. JSON is a list already using the four target names. A record has a short
lowercase ID and account; outcome is exactly success or failure. Times need seconds
and Z or an explicit offset no larger than 14 hours. Convert each valid time to UTC.

The exact row labels are **import**, **repeat**, **reject**. Number source data rows
from 1; the CSV header is not a row. Invalid fields go to reject. Repeated ID plus
identical normalised content goes to repeat. A different ID stays separate even
if all other fields match. Conflicting content under the same ID stops the whole
import. Broken file structure or wrong headers also stop it. Limit: 100 source rows.
The CSV reader ignores empty physical lines; row numbers count CSV records.
Check that imports + repeats + rejects equals source rows.

The case JSON is the input record. Its artifacts are readable copies of raw
evidence when prepared. Change only a run copy. For a repeated model check,
edit the evidence inside case.json; editing an extracted artifact alone does
not change case.json. Each program rejects unsupported structure. Record-level
rejections are named below where that is part of the lesson.

## Practice commands

Open a terminal in this lab folder. Replace `python` with `py -3` if needed.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. Save a prediction in notes.txt before seeing an answer.
Fill the decisions in answers.json with the exact vocabulary above. Add an
explanation and evidence IDs. Keep the first attempt; write corrections below it.

Do the real local import after saving your expected counts:

```text
python operations.py --source run/attempt-01/records.txt --format csv --out run/attempt-01/imported
```

This reads the extracted raw file, creates events.sqlite, then queries it back.
Open imported/import-report.json and imported/rejected.json. Reconcile e01 and
e02 to source rows. Keep source.txt as an input copy. For attempt-02 use --format
json. For attempt-03 use csv. Each output must be a new folder below run/.
This practical import reads records.txt; the model reads the copy inside case.json.
If you edit one, record the change and do not pretend the two inputs still match.

After your prediction and practical work, compare the model:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

Use the matching attempt path for the later cases. Prepare refuses to replace
an existing folder. Its output must be below run/. Other explicit paths are
relative to the terminal directory. Exit 0 means success or an answer match;
1 means a mismatch or missing writing; 2 means invalid input or a file error.
A match checks labels and the presence of writing. A person must review whether
the explanation is sound. Tests and verify check the package, not learner skill.

## Save evidence and hand over

Keep case.json, answers.json and notes.txt. Record the commands, outputs, first
prediction, observed facts, interpretation, unknowns, next check, and help used.
Give each fact a record ID. End with a short handover: question, scoped finding,
two evidence references, a competing explanation, and the next evidence needed.
Mark your stage as attempted, checked with help, or attempted again unaided.
Do not call a script match mastery.

Cleanup is optional. After saving your work elsewhere, remove only the chosen
run/attempt folder using your file manager. Check its full path first. No system
setting needs rollback. Keep supplied fixtures and first attempts.

## Limits

Rows describe fictional login records, not confirmed incidents.

UTC conversion needs an explicit offset; clock accuracy remains unverified.

A rejected row is retained as evidence and is not evidence of a safe event.

The authoring check ran this local file import and database readback. No SIEM service was installed or tested.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [Python CSV reader and writer](https://docs.python.org/3/library/csv.html)
- [Python SQLite interface](https://docs.python.org/3/library/sqlite3.html)
- [Python aware and naive times](https://docs.python.org/3/library/datetime.html)
- [NIST SP 800-92: log management](https://csrc.nist.gov/pubs/sp/800/92/final)
