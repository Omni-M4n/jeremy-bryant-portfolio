# Worked example: record set A

Read this after saving your first attempt.

The window is 00:01 inclusive to 00:03 exclusive. Line 1 is a failure exactly
at the start, so count it. Line 2 is broken JSON, so retain a rejection. Line 3 is
a success inside the window, so label it other-outcome. Line 4 is exactly at the
end, so label it outside. The result is **reader: 1** with **one rejected line**.

Do not report only "one failure". Add "one of four lines could not be parsed".
The authoring check actually ran the helper against the prepared local file.

Write the evidence separately from your interpretation. State one thing these
records cannot establish. Keep the first answer and the corrected answer.

## Two-function comparison, after your own attempt

```python
def include(row):
    return row["outcome"] == "failure" and START <= row["time"] < END

def add(counts, account):
    counts[account] = counts.get(account, 0) + 1
```

The starter checks the time format before include sees it. The count changes
only after the duplicate check. Explain why moving it earlier would count repeats.
