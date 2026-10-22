# Login triage: original guided practice

Practise reading sign-in records, reconstructing a timeline, checking an alert rule, and writing a short handover. A **security operations centre (SOC)** is a team that reviews possible security problems. **Triage** means deciding what deserves attention first and what evidence is needed next.

These are original guided practice materials for a beginner. The records, organisation, accounts, notes and future timestamps are fictional. This lab is independent learner practice, not an assessed exercise or evidence of professional SOC experience. Following the worked example does not establish independent mastery, and the supplied utility is not a claim that Jeremy independently built a production security tool.

## Start here

Use Python 3.9 or newer. Only Python's standard library is required: no packages, sign-in, network traffic or live authentication. Open a terminal in this folder. On Windows, `py` can replace `python` if that is your installed Python command.

```sh
python lab.py --help
python lab.py verify
python lab.py timeline
python lab.py timeline --user practice-staff-041
python lab.py triage
python lab.py verify --report runs/report.json
```

Read the three invented account notes in [`fixture/context.json`](fixture/context.json). Write your own interpretation before opening the [worked example](WORKED-EXAMPLE.md). Continue with the [practice drills](PRACTICE.md).

`triage` writes `runs/report.json`. Open that file in a text editor to inspect the counted events and linked successes. Repeating a command that writes an existing output is refused; give `--output` a fresh name to preserve earlier work. Relative **output** paths are resolved from this lab folder. Relative **input** paths are resolved from your terminal's current folder, so run the examples here.

## Compact command contract

`lab.py` is the single maintained command entry point. It reads local synthetic files only. Generated cases, reports and test scratch files stay under this folder's ignored `runs/` directory. It will not overwrite existing outputs. Tests remove only their own temporary subdirectories. No command changes the checked-in fixture or performs account actions.

| Command | Input | Result |
| --- | --- | --- |
| `generate --seed 72 --scenario baseline` | Numeric seed and scenario name | A new `runs/seed-72-baseline/` with CSV, JSONL, context and manifest |
| `timeline [--input FILE] [--user NAME] [--source-ip IP] [--outcome failure]` | Fixture CSV by default; exact-value filters can be combined | Sorted selected events printed to the terminal; no file written |
| `triage [--input FILE] [--threshold 5] [--window-seconds 300] [--success-seconds 120] [--output runs/report.json]` | CSV or JSONL | One JSON report with settings, evidence event IDs and input hash |
| `verify [--case DIRECTORY] [--report FILE]` | Fixture directory by default | Recreates the seed's expected files, compares every byte and optionally recalculates the report |
| `test` | Supplied fixture and temporary synthetic cases | Timing, grouping, invalid-input and integrity checks; exit status 0 when all pass |

Exit status 0 means the command completed, 1 means tests failed, and 2 means invalid input or a file problem. A status is a number the terminal can use to distinguish completion from failure. `verify` checks file integrity and calculation consistency; it does **not** assess your explanation or validate the rule for a real organisation. A hash is not a digital signature or proof of who authored a file.

## What the rule actually counts

The default **threshold** is five failures. The default **window** is 300 seconds (five minutes). For each distinct failure timestamp, the program counts only failures for the **same account and same source address**, between `timestamp − 300 seconds` and that timestamp, including both endpoints. Earlier failures outside that window are excluded. Successes do not count as failures and do not reset the window.

A qualifying window is a **candidate** for review. Each qualifying end time is reported, so two overlapping windows can describe one sequence. Do not count the two windows as two proven incidents. Records are sorted by timestamp; file order does not establish event order. All failures sharing a second are counted together. Their event IDs are labels, not evidence of subsecond order.

A **linked success** means the same account and source address had a success strictly after a qualifying window ended, within the next 120 seconds, including the upper boundary. A success in the same second is not linked because the data cannot establish which event came first. `--success-seconds 0` disables links. A timing link does not establish the same person, a successful attack, or what happened after sign-in.

This is a deliberately small **heuristic**: a useful rule of thumb, not proof of compromise. It can miss failures spread across several addresses or accounts. A shared internet address can also represent several people. A lack of candidates means only that this rule found none in these records; it does not establish that an account is safe.

## Reading the evidence

The fixture contains 19 events in deliberately shuffled order. CSV and JSONL contain the same events in two formats; they are alternatives, not two independent evidence sources.

| Field | Plain-language meaning |
| --- | --- |
| `event_id` | Unique synthetic record label, such as `SYN-0001` |
| `timestamp` | Invented time in UTC, written `YYYY-MM-DDTHH:MM:SSZ`; UTC is a common time reference and `Z` marks it |
| `user` | Fictional account label beginning `practice-` |
| `source_ip` | Address recorded as the source of the attempt; all values use reserved documentation ranges |
| `outcome` | `failure` or `success` according to this fictional log |
| `reason` | `invalid_password` for a failure or `accepted` for a success; it does not identify the person typing |
| `synthetic` | The literal text `true`, making each row explicitly fictional |

**CSV** is a text table with comma-separated fields. **JSONL** is a text file with one structured JSON record per line. **JSON** names fields so a program or reader can inspect them. An **IP address** is a network address; these documentation values do not identify real hosts. A **service account** is used by an automated job rather than a person. A **stale password** is an old saved password that no longer works.

The parser rejects missing or unexpected fields, duplicate event IDs, invalid dates, unsupported outcomes, non-documentation addresses and rows without explicit synthetic labels. These constraints help keep this exercise scoped; they cannot prove that arbitrary user-edited text contains no personal data. Use the supplied generator and fictional edits only.

## Evidence, interpretation and next action

Keep these three parts separate in your notes:

1. **Observed:** name the account, source address, UTC interval, event IDs and counts. State the exact rule settings.
2. **Interpretation:** describe a plausible explanation and what remains unknown. A helpdesk note supports an explanation but is not independent verification of the actor.
3. **Next check:** request the missing evidence that could change your decision, such as confirmation from the account owner, device records, an additional sign-in verification record, or actions taken after the sign-in. In this exercise, write the request only.

A **false positive** is a rule match that turns out not to be the suspected security problem. It may still reveal an operational fault. An **escalation** asks a more experienced reviewer to investigate; a **handover** provides enough evidence for that person to continue. Neither requires claiming an attacker was identified.

## Reproducibility and scope

A **seed** is a number that produces the same fictional case again. Change the seed to vary account labels, addresses, times and file order. Use `baseline`, `late-success` or `distributed` to change the sequence's behaviour. [`fixture/manifest.json`](fixture/manifest.json) records synthetic provenance, seed, scenario, generator version and SHA-256 hashes of the data and context. **SHA-256** produces a fingerprint of file bytes; a changed file normally has a different fingerprint.

The checked-in fixture is seed 41, baseline, generator version 1.0.0. `verify` compares it with regenerated content, including the manifest, rather than merely trusting hashes written in the manifest. Preserve LF line endings when copying fixture files. Keep your notes and new cases in `runs/`; it is excluded from Git, the repository history system. No personal data, passwords or real authentication logs are needed.

Run `python lab.py test` after changing the tool. Passing software checks and following the worked answer are distinct from factual judgement or independent learner performance. This lab has no external grader, no badge and no automatic mastery claim.
