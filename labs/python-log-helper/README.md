# Read and explain a tiny Python log helper

Imagine counting late arrivals from a class list. A torn line must not vanish
without a note. Can a short script count only the records you meant to count?



This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise variables, loops, files and login-triage first.
No administrator rights, account, installation, live scan, or security changes are needed.

**Words:** JSON is a text format for named values. JSON lines puts one record on
each line. Validate means check that an input follows the rules. A half-open window
includes its start but excludes its end. A dictionary stores values under names.

## Question and exact rules

The source is artifacts.events.jsonl. Each physical line needs exactly id,
time, account and outcome. IDs and accounts use simple lowercase names. The time
must be UTC with seconds and Z. Outcome is failure or success. The case data has
start and end UTC times, with start before end. Limit: 100 physical lines.

Use these exact labels: **count** for a unique failure at start <= time < end;
**other-outcome** for a unique success inside that window; **outside** for a unique
valid event outside it; **repeat** for an identical ID and full record already
seen; **reject** for a malformed line. Blank lines and repeated JSON keys are
rejected. A final line ending is not an extra blank line. Conflicting content under
one ID stops the whole count. Check repeat status before window/outcome status.
Count only failures by account. A rejected line is not silently treated as success.

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

Read count_lines in lab.py from top to bottom. Mark input checks, the loop,
the repeat check, the time filter, and the count update. Then process the real file:

```text
python operations.py --source run/attempt-01/events.jsonl --start 2026-01-15T00:01:00Z --end 2026-01-15T00:03:00Z --out run/attempt-01/count-output
```

Open count-output/report.json and compare each line status with your hand count.
The saved source.jsonl keeps the exact input bytes. Repeat in each later attempt
with a new output folder. The operational helper reads the extracted events.jsonl;
the model reads case.json. Keep them aligned or record why they differ.

Now do the required writing task in WRITE-YOUR-HELPER.md. Copy learner_starter.py
into your attempt folder as my-helper.py and finish its two short functions.
Its supplied file-reading and validation code is part of the scaffold, not code
you should claim to have written. Explain which lines are yours. Check its tiny
known-answer sample, then process events.jsonl and compare the counts.

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

The helper counts unique valid failure records in a half-open UTC window; it makes no incident decision.

Malformed lines are retained by line number; skipped lines can change the conclusion.

No network, host log or live account is read. A successful run does not show script mastery.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [Python aware and naive times](https://docs.python.org/3/library/datetime.html)
- [NIST SP 800-92: log management](https://csrc.nist.gov/pubs/sp/800/92/final)
- [Python JSON decoding](https://docs.python.org/3/library/json.html)
