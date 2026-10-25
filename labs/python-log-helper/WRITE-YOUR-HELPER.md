# Finish and explain two small functions

Use a text editor to copy learner_starter.py to run/attempt-01/my-helper.py.
The starter is deliberately incomplete. Keep the supplied starter unchanged.
Read its validation code first. It checks fields and keeps malformed line numbers.
The trusted operations.py remains available as a reference run.

1. In include, return true only when outcome is failure and START <= time < END.
   Time text can be compared here because every accepted time has the same UTC
   layout. Do not reuse that shortcut for mixed offsets or different layouts.
2. In add, set counts[account] to its old value plus one. If the account has no
   value yet, start from zero. Use dict.get(account, 0) to read that default.
3. Add one comment in your own words explaining the exclusive end time. Mark the
   two functions as your edits and the remaining code as the supplied scaffold.

Create run/attempt-01/tiny.jsonl with exactly these three lines:

```json
{"id":"t1","time":"2026-01-15T00:01:00Z","account":"reader","outcome":"failure"}
{"id":"t2","time":"2026-01-15T00:03:00Z","account":"reader","outcome":"failure"}
{"id":"t3","time":"2026-01-15T00:02:00Z","account":"reader","outcome":"success"}
```

Save your predicted counts before reading the check below.

The known answer is one reader failure, no rejected lines and no repeats.
Compare that with your prediction, then run from the lab folder:

```text
python run/attempt-01/my-helper.py run/attempt-01/tiny.jsonl
python run/attempt-01/my-helper.py run/attempt-01/events.jsonl
```

For guided, expect counts reader=1, rejected_lines=[2], repeats=0. Save the output
and explain every included and excluded line. Add a blank fourth line to a new
copy of tiny.jsonl. Predict its status before you run the helper. Then make
another copy in which t2 uses t1's ID. Use the conflict rule to predict whether
the run can finish. Save your reasons before checking the result.

Do not claim authorship of the scaffold. State exactly what you wrote and which
checks you ran. The authored completed version was tested locally during package
validation; your own version still needs its own evidence.
