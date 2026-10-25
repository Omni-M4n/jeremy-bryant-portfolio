# Build a cloud audit evidence timeline

Build a time line of actions from a cloud log. Link records using the rules below. Keep failed attempts separate from actions that worked. State where logs have gaps. An account label alone cannot prove which person acted.

**Time:** Allow 30-45 minutes for your first pass. Try the recall task on another day.
**Before you start:** You need to open files and edit a small JSON worksheet. JSON stores named fields and lists as text. Basic network and security terms will help. You do not need work experience, a cloud account or coding skills. You will not change code.

## Key words

An **audit event** records an attempted action and its result. **Correlation** means linking records with evidence. **Attribution** means finding out who acted. A **management event** concerns a change or an identity action. A **data event** concerns an object, such as a stored file. A **coverage gap** means some types of activity may not be logged. **UTC** is the time standard used here. A **Boolean** is `true` or `false`.

## Evidence and exact rules

This is a **made-up schema**, or data format. It is not a real provider's log format. The `data` field has `window_start`, `window_end`, `logging`, `approved_changes` and `events`. The events list must not be empty. The start and end times use UTC. The `logging` field has Boolean `management` and `data` flags. These show the logging setup at the start of the window.

A few records can still exist for a type with logging turned off. Those records do not prove that the log is complete.

Each event has a unique `id`. It also has `at`, `identity`, `session`, `action`, `result` and `resource`. All IDs are lowercase labels. They are not real account IDs. A session links activity during a period of use.

| Field or rule | Exact values |
| --- | --- |
| `action` | `sign-in`, `read-object`, `change-policy` or `disable-logging`. |
| `result` | `success` or `denied`. |
| Sign-in resource | Must be `identity-service`. |
| Data action | `read-object`. All other actions are management actions. |
| Reserved ID | `logging` is for the extra coverage decision. |
| Time form | Exactly `YYYY-MM-DDTHH:MM:SSZ`. |

Each event time must be within the window, including its start and end. The window's end must be later than its start.

An approval has just `identity`, `action`, `resource`, `from` and `to`. Only `change-policy` and `disable-logging` can be approved. Both ends of the approval window count.

To link an action to a sign-in, check all these rules:

1. The sign-in must have succeeded.
2. Both identity **and** session must match.
3. The sign-in must be at or before the action.
4. The gap must be at most 15 minutes. Exactly 15 minutes counts.

Do not trust the input order. The output sorts records by time, then ID.

Use the first matching rule for each event ID:

| Label | Rule |
| --- | --- |
| `denied-no-success-evidence` | The result is denied. It does not prove a change worked. |
| `authentication-only` | Sign-in worked. This record alone proves no later action. |
| `successful-action-unattributed` | A non-sign-in action worked, but has no link that meets the rules. |
| `successful-read-correlated` | An object read worked and has the required sign-in link. |
| `approved-change-correlated` | A change worked, has the sign-in link, and matches an approval's identity, action, resource and time window. |
| `unapproved-change-correlated` | A change worked and has the sign-in link, but has no such approval match. |

There is also a `logging` decision. Use `coverage-configured` if both log types are enabled. Otherwise use `coverage-gap:ITEMS`. Here `ITEMS` is `data`, `management` or `data,management`, in that order.

Append `;interruption-observed` if any `disable-logging` event succeeded. This applies even without approval or a sign-in link. A denied event never adds that suffix. A log may be configured and still fail to deliver every event.

## Run the exercise

From the repository root, enter this folder with `cd labs/cloud-audit-triage`.

Use Python 3.10 or newer. On Windows, you may use `py` in place of `python` if it is your installed launcher. You do not need to install packages or set up an account or billing. All commands run offline. They change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any `.txt` evidence files. Open the blank `run/attempt-01/answers.json` worksheet. Fill in each decision with an exact label from the rules above. Write your own reason for each choice. In `evidence`, cite record IDs or line numbers from this case. Use `notes.txt` to record your first prediction, doubts and any help used.

Save your prediction before you run these commands:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has just three fields:

- `decisions` is an object. It pairs each record ID with your chosen label.
- `explanation` is text. Write why you chose those labels.
- `evidence` is a list of text references. You could name a record ID and its field. Use IDs from your case. Do not invent them.

`check` compares the decision labels. It also checks that you filled in the written fields. A person must judge whether those words are right. `verify` checks the supplied test cases. It does not assess your skill.

The exit code tells you what happened. Code 0 means success or a match. Code 1 means a mismatch or blank written fields. Code 2 means invalid input. If you omit `--case`, the command uses the guided case beside the script. Input paths start from your current terminal folder. The `--out` path starts from this lab folder. It must name a new folder below `run/`.

Use fresh folders for the next cases:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with your chosen folder. Edit practice copies only. Do not overwrite the supplied fixtures or reference answers. Fixtures are the starting cases.

## Deliverable and handover

Save a filled worksheet and a short evidence note for each case. Include your first prediction and any change to it. State what is still unclear. Name one next check that these files cannot answer. Record any help used, including the worked example.

Ask a reviewer: "Can you reach my decision from these record IDs? Which claim goes beyond the evidence?" Your skill at doing this alone is still **unassessed**. A matching output does not prove skill, a qualification or work experience. These are made-up practice cases. They are not work for assessment.

## Limits

The model does not read a real cloud log. It does not check signed proof of a log's source or infer a person's intent. It does not cover every sign-in route, restore logs or query a service. The 15-minute limit is a teaching rule. "Unattributed" means the supplied links are too weak. It does not prove an attack.

## Primary references

The official guide shows how real audit records store time, identity, action and results. This lab uses a smaller, made-up format. It cannot read a provider's logs or prove that all events were logged.

- [AWS CloudTrail: event record contents](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html)

The links are optional extra reading. They were checked on 2026-10-23. The lab does not fetch them. Read [the worked example](WORKED-EXAMPLE.md) after you save your prediction. Use [the drills](DRILLS.md) for more practice.
