# Alert deduplication and correlation

Separate repeated deliveries from unique alerts, then group related evidence with a visible time-window rule without equating alerts with incidents.

This is an original, fictional, offline exercise for an introductory security learner. It is independent practice, not copied coursework or a claim of professional experience. Completion and competence remain unassessed.

## Before you start

Allow **30-45 minutes**: 5 minutes reading, 10 inspecting and predicting, 10 checking and explaining, and 5-20 for a changed or independent case. You need Python 3.10+ (standard library only), a terminal and a text editor. Comfort opening files, reading a small table and basic evidence notes is enough; programming, administrator rights, a Linux installation and cloud accounts are unnecessary. Previous introductory network or Wireshark practice is useful but not required.

> **Vocabulary:** Delivery: one received record. Deduplication: removing repeat delivery of the same ID and content. Correlation: bringing related evidence together. Anchor window: a period measured from the first event rather than the most recent event. Incident: a conclusion requiring investigation beyond alert counts.

## Evidence and exact rules

The case JSON is the single authoritative input. Fixtures are guided.json, changed.json and challenge.json. All data is synthetic; artifacts is empty to avoid competing editable copies. Edit only a prepared run copy. The analyser is a pure calculation and never executes evidence text.

data.window_seconds is an integer from 1-3600. Each alert has id, fictional lowercase host.test, simple account name, UTC time to seconds and kind auth-failure/auth-success/process-alert. Identical IDs with identical content represent repeat delivery. Conflicting content under one ID is rejected. Different IDs remain distinct.

Deduplicate before counting. Partition by exact host/account, sort by timestamp then ID, and start a session at the first alert. Include alerts up to window_seconds after that anchor, inclusively; a later alert begins a new session. The window does not slide. Keys are host/account/session-number. Three strictly earlier failures before a success in one session give review-auth-sequence. Otherwise process-alert plus either authentication kind gives review-mixed-signals. Remaining groups give retain-context. These are exercise triage rules, not confirmed incident counts.

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

Deduplication uses alert ID and identical full content; different IDs are retained even when text or timestamps match. Clock accuracy, sensor coverage, account ownership and authorised activity remain unverified; no service or endpoint was contacted.

Use WORKED-EXAMPLE.md after making a first prediction, and DRILLS.md for progressively less support. Do not use these rules as an operational security verdict or modify a real host as part of this exercise.

## Primary references

The following documentation supports the underlying concepts; the tiny schema and explicit teaching rules above are specific to this lab. Links were checked during authoring on 23 October 2026. Running the lab needs no internet connection.

- [NIST log management guidance](https://csrc.nist.gov/pubs/sp/800/92/final)
