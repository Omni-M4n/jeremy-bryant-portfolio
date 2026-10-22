# Timeline normalisation and uncertainty

Normalise offset timestamps to UTC, correct known clock error and decide when evidence does or does not establish strict temporal order.

This is an original, fictional, offline exercise for an introductory security learner. It is independent practice, not copied coursework or a claim of professional experience. Completion and competence remain unassessed.

## Before you start

Allow **30-45 minutes**: 5 minutes reading, 10 inspecting and predicting, 10 checking and explaining, and 5-20 for a changed or independent case. You need Python 3.10+ (standard library only), a terminal and a text editor. Comfort opening files, reading a small table and basic evidence notes is enough; programming, administrator rights, a Linux installation and cloud accounts are unnecessary. Previous introductory network or Wireshark practice is useful but not required.

> **Vocabulary:** UTC offset: the displayed timezone difference from UTC. Clock skew: device clock error relative to a reference. Uncertainty bound: the allowed interval around an estimate. Causation: one event producing another, which timing alone cannot prove.

## Evidence and exact rules

The case JSON is the single authoritative input. Fixtures are guided.json, changed.json and challenge.json. All data is synthetic; artifacts is empty to avoid competing editable copies. Edit only a prepared run copy. The analyser is a pure calculation and never executes evidence text.

data.events provides ID, timestamp with seconds and explicit Z or numeric offset, signed clock_offset_seconds, uncertainty_seconds and description. Offset is bounded to +/-86400 and uncertainty to 0-3600 seconds. data.pairs names two different known event IDs and a unique comparison ID. Naive dates and impossible timestamps are rejected.

Convert the recorded timestamp to UTC, then subtract clock_offset_seconds: positive means a fast device clock. Construct a closed interval centre +/- uncertainty. The left event is definitely-before only when its upper bound is strictly less than the right lower bound; definitely-after uses the reverse strict comparison. Every overlap, touching endpoint or identical timestamp gives order-uncertain. Ordering is temporal only and never evidence of causation by itself.

## Run the exercise

Open a terminal in this lab folder. Use your Python command (`python`, or `py -3` if that is how Python is installed). Commands below use `python` consistently.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. In run/attempt-01/answers.json, fill each decision with an exact label from the rules; add an explanation and evidence references such as record IDs or configuration line numbers. In notes.txt, separate observation, interpretation, uncertainty, next check and help used. Save your prediction before opening the answer.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

For changed/challenge use the corresponding attempt folder in show/analyse/check. prepare refuses an existing output folder. --out is relative to this lab and must be below run/; explicit input paths are relative to your terminal directory. analyse/show default to the guided fixture if --case is omitted. Exit 0 means command success or decision match; 1 means differences/incomplete written fields; 2 means invalid input or a filesystem problem. The checker verifies decision fields and the presence of writing, not the quality of reasoning. verify checks shipped examples, not learner mastery.

## Deliverable and limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. Deliver a short handover: the question, your conclusion, two precise evidence references, one alternative explanation or limitation, and the next evidence you would request. State whether you used the worked example and whether you completed a fresh case unaided. Do not describe an automated match as assessment or professional experience.

A positive clock offset means the device clock is fast and is subtracted after UTC normalisation. The supplied uncertainty is a bound, not a probability. The model assumes supplied offset and uncertainty estimates are valid; collection delay, timestamp granularity and omitted events need separate investigation.

Use WORKED-EXAMPLE.md after making a first prediction, and DRILLS.md for progressively less support. Do not use these rules as an operational security verdict or modify a real host as part of this exercise.

## Primary references

The following documentation supports the underlying concepts; the tiny schema and explicit teaching rules above are specific to this lab. Links were checked during authoring on 23 October 2026. Running the lab needs no internet connection.

- [NIST Guide to Computer Security Log Management](https://csrc.nist.gov/pubs/sp/800/92/final)
