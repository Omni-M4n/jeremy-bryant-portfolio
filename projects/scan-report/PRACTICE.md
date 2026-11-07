# Practice record — not completed work

The supplied fixture and tests are programmatic examples. No learner completion or mastery is claimed. Save your own notes, changed files and observed results separately. Use fictional data throughout these drills.

## Read, predict, run

1. Read `sample.json` without running the tool. Predict the order of the three IDs, the five severity counts and the confidence shown for the first observation.
2. Run `python report.py sample.json practice-01.html`. Open the report and compare it with your prediction. Explain why the low confidence label did not change the supplied severity or sort order.
3. Run `python -m unittest -v`. Pick one test and explain what failure it would catch, what it cannot prove and why a passing suite does not establish that the sample findings are real.

Evidence to save: your prediction, the command result and a short explanation of the first sorted observation. Do not treat the checked example as your own completed exercise.

## Fresh input and failure boundaries

Make a copy called `practice.json`. For each trial, predict success or failure first and use a new output name.

| Change | Explain after running |
| --- | --- |
| Add a second high-severity observation with an earlier ID | How does the tie break work? |
| Set `findings` to an empty array | Why is this accepted without claiming security? |
| Put `<script>alert(1)</script>` in one evidence string | Which source characters change in HTML? Why does no script run? |
| Set a resource to `javascript:alert(1)` | Why is it displayed without a clickable link? |
| Change `schema_version` from `1` to `true` | Why does Python's boolean/integer relationship matter? |
| Repeat an ID or add an unknown field to the final observation | Why must validation finish before writing? |
| Use the input path as the output path | Verify the input bytes remain unchanged. |
| Run again with an existing output name | Verify the previous output bytes remain unchanged. |

Evidence to save: your fictional input copy, two successful reports, one rejected input and an explanation of the rejection. Do not include real system details or credentials in practice evidence.

## Small implementation change

In a separate working copy, add a `scanner` text field to the report header. First decide the exact limit and whether it is required. Update validation, rendering, the fixture, tests and the README contract together. Add a test proving that a scanner value containing HTML remains text. Explain why adding it only to rendering would violate the current strict schema.

Acceptance: all existing tests pass, your new test fails before the change and passes after it, and the new header contains no executable markup.

## Break and repair

Perform one change at a time in a disposable working copy, run the relevant test and restore the original before moving on:

1. Remove the evidence escaping call. Identify the injection test that fails and explain the broken trust boundary.
2. Change the schema version test to accept `isinstance(value, int)`. Identify the boolean case that now passes incorrectly.
3. Replace the final no-clobber publication operation with an overwriting operation. Explain the data-loss risk; run the collision tests only with their disposable fixtures.
4. Remove the severity key from sorting. Identify which expected report order changes.

Finish by explaining the data flow from memory and reproducing a fresh valid report. A reviewer should check the explanation and results before recording learner mastery.
