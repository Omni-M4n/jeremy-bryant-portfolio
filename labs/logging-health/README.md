# Check whether logs arrived

A blank attendance list might mean nobody arrived. It might also mean the
list never reached the office. Can the collected records support a quiet-window claim?



This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise log-ingestion and timeline-analysis first.
You do not need admin rights or an account. You do not need to install tools,
scan a live system or change security settings.

**Words:** Telemetry means records sent by a system. A collector receives them.
A heartbeat is a small "still here" signal. Ingestion is arrival into the collected
record store. A cutoff is the time when you stop checking. Coverage asks which
expected records are present.

## Question and exact rules

data has observed_at, delay_budget_seconds (0-3600), and intervals that do not overlap.
Each interval has id, start, end, source_ids, received and heartbeat. Times are UTC.
Use start <= event time < end. Each interval must end by the observation cutoff.
source_ids is the complete ID list supplied apart from the received records.
It is null when the source list is unknown. An empty list means a known count of
zero; null does not. Each item in received has id, event_at and ingested_at.
Arrival cannot be before the event or after the cutoff. The tool rejects duplicate
event IDs and intervals that overlap. It also rejects a received ID that is absent
from a known source list.

For each interval/coverage, check the source list first. Use **complete-at-cutoff**
if all known source IDs arrived. Use **gap-at-cutoff** if any known ID is absent.
Use **source-unverified** if the source list is unknown.

For interval/delivery, use **no-deliveries** if none arrived. Use **late-delivery**
if any delay is greater than the budget. Use **within-budget** otherwise.
Exactly 60 seconds meets a 60-second budget.

Answer interval/heartbeat with **present** or **absent**. Keep these three answers
separate. A heartbeat cannot replace the count from source to collector.

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

Make a small coverage timeline on paper or in notes.txt. For every interval,
write expected IDs, received IDs, missing IDs, and delay in seconds. Add a separate
heartbeat column. This is an offline evidence comparison, not a test of a real
collector. No collector is installed or changed.

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

Coverage compares received records with the supplied source IDs at the stated cutoff. It does not cover all activity on a host.

A heartbeat proves that its small signal arrived. It does not prove that all event records arrived.

Delays may come from records in transit, queues or clock problems. This model assumes the clocks are correct.

A complete empty source list supports a narrow claim: zero listed events in this interval. It does not show that nothing happened anywhere.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [NIST SP 800-92: log management](https://csrc.nist.gov/pubs/sp/800/92/final)
- [Python aware and naive times](https://docs.python.org/3/library/datetime.html)
- [NIST SP 800-61 Rev. 3: incident response](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
