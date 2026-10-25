# Check a detector against labelled examples

A door bell that rings for every passing bird catches visitors too. Counting
only the visitors it catches hides the noise. How does a changed alert threshold
affect both missed examples and false alarms?

This extends **snort-rule-testing**. It adds labelled corpus counts and a held-aside check. It does not claim to run Snort.

This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise snort-rule-testing and soc-query-workbook first.
No administrator rights, account, installation, live scan, or security changes are needed.

**Words:** A corpus is a collection of examples. A label states the supplied
truth for an example. A threshold is the number that triggers a result. Tune rows
help choose a rule. Holdout rows are kept aside to check that choice. A denominator
is the total under a fraction. A false alarm is an alert on a routine example.

## Question and exact rules

Each event is one independent fictional five-minute account window. Its fields
are id, failures (0-100), label (routine/exercise), and partition (tune/holdout).
IDs must be unique across both partitions. data.thresholds contains two increasing
integers from 1-20. The supplied pair is 3 and 5. Alert when failures >= threshold.
No raw attack is carried out; the count is harmless supplied data.

The answer for each rN/partition key has this form: **tp=N,fp=N,fn=N,tn=N**.
Replace each N with your count for that cell.
Use lower case, this order, and no spaces. TP means an exercise row that alerts.
FP means a routine row that alerts. FN means an exercise row missed. TN means a
routine row with no alert. Add the four counts to get the partition size.

Report false alarms as FP/(FP+TN), misses as FN/(TP+FN), alerts as (TP+FP)/all
rows, and false share of alerts as FP/(TP+FP). These denominators answer different
questions. A zero denominator gives **undefined(0/0)**, not a zero rate. Keep the
fractions unsimplified so the tested counts stay visible.

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
python operations.py tune --case run/attempt-01/case.json
```

Keep case.json, the worked example and the reference folder closed for now.
Do not run show or analyse yet: those commands reveal the full case.
The tune command prints only tune rows. Make a four-cell count table for each
threshold it lists. Save these counts and your reasons in notes.txt.

Choose one threshold based on those rows and the costs you want to balance.
The command below is a template. Replace N and the quoted reason with your own
choice. It writes choice.json once and will not replace an earlier choice.

```text
python operations.py choose --case run/attempt-01/case.json --threshold N --reason "My reason based on tune rows"
python operations.py holdout --case run/attempt-01/case.json
```

The holdout command needs that saved choice. It refuses a case changed since
the choice. Count the holdout results with your threshold fixed. Keep a table
of each row and whether it alerts. Record misses and false alarms, even if the
result is worse than you hoped. Do not tune the choice to fit these rows.

Now fill answers.json with your counts for both thresholds and both sets.
Use the exact form above, an explanation and row IDs. Keep the first attempt;
put any corrections below it. If you read the holdout rows early, record that.
They no longer count as an unseen check. Use a fresh case for the next attempt.

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

Keep case.json, answers.json, choice.json and notes.txt. Record the commands, outputs, first
prediction, observed facts, interpretation, unknowns, next check, and help used.
Give each fact a record ID. End with a short handover: question, scoped finding,
two evidence references, a competing explanation, and the next evidence needed.
Mark your stage as attempted, checked with help, or attempted again unaided.
Do not call a script match mastery.

Cleanup is optional. After saving your work elsewhere, remove only the chosen
run/attempt folder using your file manager. Check its full path first. No system
setting needs rollback. Keep supplied fixtures and first attempts.

## Limits

All events are harmless synthetic examples. Exercise labels are supplied teaching truth, not observed attacks.

Fractions describe only their named partition and denominator. This corpus cannot establish production accuracy.

Choose a candidate using tune rows before inspecting holdout rows. Reusing holdout to tune removes that independent check.

The tune, choose and holdout commands help keep this order. It cannot stop you opening the full case
or changing local files. A saved choice is practice evidence, not proof that
the holdout was unseen. Be clear about what you read and any help you used.

A count threshold is a simplified query, not a tested Snort rule or a complete detection system.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [NIST SP 800-94: intrusion detection](https://csrc.nist.gov/pubs/sp/800/94/final)
- [scikit-learn evaluation definitions](https://scikit-learn.org/stable/modules/model_evaluation.html#confusion-matrix)
