# Login triage: original guided practice

Which sign-in records need a closer look? Read the records and put them in time order. Check an alert rule, then write a short handover. A handover gives the next reviewer what they need. A **security operations centre (SOC)** reviews possible security problems. **Triage** means choosing what to review first. It also means deciding what evidence to seek next.

This is new guided practice for a beginner. The records, organisation, accounts, notes and future times are made up. It is separate learner practice. It is not assessed work or proof of professional SOC experience. Following the worked example does not prove independent mastery. The supplied tool does not show that Jeremy built a production security tool without help.

## Start here

Use Python 3.9 or newer. Only Python's standard library is needed. There are no packages to add. There is no sign-in, network traffic or live authentication. Open a terminal in this folder. On Windows, `py` can replace `python` if that is your installed Python command.

```sh
python lab.py --help
python lab.py verify
python lab.py timeline
python lab.py timeline --user practice-staff-041
python lab.py triage
python lab.py verify --report runs/report.json
```

Read the three made-up account notes in [`fixture/context.json`](fixture/context.json). Write what you think the records show. Then open the [worked example](WORKED-EXAMPLE.md). Continue with the [practice drills](PRACTICE.md).

`triage` writes `runs/report.json`. Open it in a text editor. Check the counted events and linked successes. The tool refuses to write over an existing output. Give `--output` a fresh name to keep earlier work. Relative **output** paths start from this lab folder. Relative **input** paths start from your terminal's current folder. Run the examples here so the inputs are found.

## Compact command contract

`lab.py` is the single maintained command entry point. It reads only local, made-up files. New cases, reports and test scratch files stay in `runs/`. Git ignores this folder. The tool will not overwrite outputs. Tests remove only the temporary subfolders they created. No command changes the checked-in fixture or acts on an account.

| Command | Input | Result |
| --- | --- | --- |
| `generate --seed 72 --scenario baseline` | Numeric seed and scenario name | A new `runs/seed-72-baseline/` with CSV, JSONL, context and manifest |
| `timeline [--input FILE] [--user NAME] [--source-ip IP] [--outcome failure]` | Fixture CSV by default; exact-value filters can be combined | Sorted selected events printed to the terminal; no file written |
| `triage [--input FILE] [--threshold 5] [--window-seconds 300] [--success-seconds 120] [--output runs/report.json]` | CSV or JSONL | One JSON report with settings, evidence event IDs and input hash |
| `verify [--case DIRECTORY] [--report FILE]` | Fixture directory by default | Recreates the seed's expected files, compares every byte and optionally recalculates the report |
| `test` | Supplied fixture and temporary synthetic cases | Timing, grouping, invalid-input and integrity checks; exit status 0 when all pass |

An exit status is a number the terminal can read. It shows whether a command finished or failed.

| Exit status | Meaning |
| --- | --- |
| 0 | Command completed |
| 1 | Tests failed |
| 2 | Invalid input or a file problem |

`verify` checks the files and repeats the calculations. It does **not** assess your explanation. It does not validate the rule for a real organisation. A hash is not a digital signature. It does not prove who wrote a file.

## What the rule actually counts

The **threshold** is the count needed to match the rule. Its default is five failures. The **window** is the span of time to count. Its default is 300 seconds, or five minutes.

For each distinct failure time, apply these rules:

| Rule | What counts |
| --- | --- |
| Group | Only failures for the **same account and same source address** |
| Start | `timestamp − 300 seconds`, included |
| End | That failure timestamp, included |
| Earlier failures | Excluded if outside this window |
| Successes | Do not count as failures and do not reset the window |

A window that meets the threshold is a **candidate** for review. Each matching end time is reported. Two windows can overlap and describe one sequence. Do not count them as two proven incidents. The tool sorts records by time. File order does not prove event order. It counts all failures in the same second together. Event IDs are labels. They cannot show the order within a second.

A **linked success** is a later success for the same account and source address. The link uses these exact limits:

| Limit | Rule |
| --- | --- |
| Start | Strictly after a qualifying window ends |
| End | Within the next 120 seconds, including second 120 |
| Same second as the window end | Not linked; the data cannot show which event came first |
| `--success-seconds 0` | Turns links off |

A time link does not prove it was the same person. It does not prove an attack worked. It says nothing about actions after sign-in.

This small **heuristic** is a rule of thumb. It does not prove that someone broke into an account. It can miss failures spread across several addresses or accounts. Several people may share one internet address. No candidates means this rule found none in these records. It does not prove that an account is safe.

## Reading the evidence

The fixture has 19 events in shuffled order. CSV and JSONL hold the same events in two formats. Choose either format. They are not two separate evidence sources.

| Field | Plain-language meaning |
| --- | --- |
| `event_id` | Unique synthetic record label, such as `SYN-0001` |
| `timestamp` | Invented time in UTC, written `YYYY-MM-DDTHH:MM:SSZ`; UTC is a common time reference and `Z` marks it |
| `user` | Fictional account label beginning `practice-` |
| `source_ip` | Address recorded as the source of the attempt; all values use reserved documentation ranges |
| `outcome` | `failure` or `success` according to this fictional log |
| `reason` | `invalid_password` for a failure or `accepted` for a success; it does not identify the person typing |
| `synthetic` | The literal text `true`, making each row explicitly fictional |

| Term | Meaning |
| --- | --- |
| **CSV** | A text table with fields split by commas |
| **JSONL** | A text file with one structured JSON record per line |
| **JSON** | A format with named fields for a program or reader to inspect |
| **IP address** | A network address; these documentation values do not identify real hosts |
| **Service account** | An account for an automated job rather than a person |
| **Stale password** | An old saved password that no longer works |

The parser rejects missing or extra fields. It also rejects these inputs:

| Invalid input | Reason |
| --- | --- |
| Duplicate event IDs | Each record needs its own ID |
| Invalid dates or unsupported outcomes | The tool cannot read these as valid events |
| Non-documentation addresses | Only reserved example addresses belong in this lab |
| Rows with no explicit synthetic label | Each row must be marked as made up |

These rules help keep the exercise within its scope. They cannot prove that edited text has no personal data. Use the supplied generator and fictional edits only.

## Evidence, interpretation and next action

Keep these three parts separate in your notes:

1. **Observed:** name the account, source address and UTC interval. Add event IDs, counts and the exact rule settings.
2. **Interpretation:** give a possible explanation. State what is still unknown. A helpdesk note can support your view. It does not confirm who used the account.
3. **Next check:** request missing evidence that could change your view. You could ask the account owner to confirm the activity. You could seek device records, an extra sign-in verification record, or actions after sign-in. In this exercise, write the request only.

A **false positive** starts with a rule match. Further review shows it is not the suspected security problem. It may still show a fault that needs fixing. An **escalation** asks a more skilled reviewer to investigate. A **handover** gives them enough evidence to continue. Neither needs a claim that you found an attacker.

## Reproducibility and scope

A **seed** is a number that makes the same fictional case again. A new seed changes account labels, addresses, times and file order. To change how the sequence behaves, choose `baseline`, `late-success` or `distributed`. [`fixture/manifest.json`](fixture/manifest.json) records the made-up origin, seed, scenario and generator version. It also holds SHA-256 hashes of the data and context. **SHA-256** makes a fingerprint of file bytes. A changed file normally has a different fingerprint.

The checked-in fixture is seed 41, baseline, generator version 1.0.0. `verify` rebuilds the content, including the manifest, and compares it. It does not just trust the hashes in the manifest. Keep LF line endings when copying fixture files. Put your notes and new cases in `runs/`. Git, the file history system, ignores it. You need no personal data, passwords or real authentication logs.

Run `python lab.py test` after changing the tool. Passing checks tests the software. Following the worked answer gives practice. Neither proves sound judgement or skill without help. This lab has no external grader or badge. It makes no automatic mastery claim.
