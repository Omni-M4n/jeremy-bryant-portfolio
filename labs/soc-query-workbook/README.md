# Query a small SOC workbook

A help desk has two failed sign-ins and two process notices for one person.
Joining the lists can produce four rows. How many sign-ins does that actually describe?

This extends **login-triage** and **alert-correlation**. It adds actual SQL filters, counts and joins in a saved local database.

This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise log-ingestion, login-triage and alert-correlation first.
No administrator rights, account, installation, live scan, or security changes are needed.

**Words:** SOC means a team that watches security evidence. A query asks a data
table a question. A filter keeps matching rows. A join pairs rows across tables.
Distinct means counted once. HTTP is the request-and-response system used by the web.

## Question and exact rules

data contains login, endpoint and web lists. Each row has id, host, account and
one table field: outcome (failure/success), kind (process/inventory), or status
(integer 100-599). Host names end in .test. Each list allows up to 100 deliveries.
Repeated identical IDs within a table are one event. Conflicting duplicates fail.
IDs from different tables are separate. Empty tables are valid.

The answer keys are failures, joined, linked and web. Each answer is an exact
nonnegative decimal count, such as "0" or "2". failures counts failed login rows.
joined counts every pair of a failed login and a process row with equal host AND
account. linked counts distinct login IDs in those pairs. web counts status 400-599.
These are counts over the whole supplied dataset, with no time-window claim.

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

Create and query a real local database:

```text
python operations.py build --case run/attempt-01/case.json --out run/attempt-01/workspace
python operations.py query --db run/attempt-01/workspace/events.sqlite --sql run/attempt-01/workspace/failures.sql
python operations.py query --db run/attempt-01/workspace/events.sqlite --sql run/attempt-01/workspace/joined.sql
python operations.py query --db run/attempt-01/workspace/events.sqlite --sql run/attempt-01/workspace/linked.sql
python operations.py query --db run/attempt-01/workspace/events.sqlite --sql run/attempt-01/workspace/web.sql
```

Read the four small SQL files. Save a copy of failures.sql as by-account.sql.
Replace its query with this one, then run it using --sql and that new path:

```sql
SELECT account, COUNT(*) AS failures FROM login
WHERE outcome='failure' GROUP BY account ORDER BY account;
```

Before running it, count the rows by hand and write the expected table. Compare
joined.sql with linked.sql and explain the changed counting unit. The runner
allows one read-only query, COUNT as its only function, and up to 100 result rows. It rejects edits, multiple
statements and queries that exceed its work limit. Save query text and output.
For later cases, build a new workspace under the matching attempt folder.

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

Joins link equal host and account fields in this small dataset; they do not prove cause or compromise.

One row is one distinct event ID in its own table. Repeated deliveries are removed before querying.

Time, sensor coverage and account ownership need separate checks before an incident claim.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [Python SQLite interface](https://docs.python.org/3/library/sqlite3.html)
- [SQLite SELECT and joins](https://sqlite.org/lang_select.html)
- [NIST SP 800-92: log management](https://csrc.nist.gov/pubs/sp/800/92/final)
