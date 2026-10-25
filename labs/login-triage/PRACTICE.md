# Repeat the exercise with less help

Keep a short note for each attempt inside `runs/`. Record the seed, scenario and rule settings. Add the time spent, help used and one fix you made. These are your own practice notes, not assessed results. Keep each earlier attempt. Save an improved answer as a new note. This makes your progress easier to check.

## 1. Guided pass

Use the checked-in fixture and the command reference in `README.md`.

1. Run `verify` to check which supplied files you are using.
2. Use `timeline --outcome failure` to select failures, then filter each account separately. **Filtering** means selecting records that match a condition. Remove the outcome filter before checking for a success.
3. Write the first and last relevant UTC times and record IDs. Count the failures in a five-minute span yourself.
4. Read the made-up account notes. Write one fact and one possible explanation for each account.
5. Run `triage` and compare its event IDs with yours. Explain why two overlapping windows do not prove two incidents.
6. Write a short handover. Include evidence, doubts and the next check. Compare it with `WORKED-EXAMPLE.md`, then note your fixes.

## 2. Hints-only pass

Create a fresh case:

```sh
python lab.py generate --seed 72
python lab.py verify --case runs/seed-72-baseline
```

Read its `context.json` and inspect `auth.csv` or `auth.jsonl`. Keep the worked example closed. Find the sequence that needs review. Explain the two other patterns. Write a handover. Then run the tool on this input and verify the report:

```sh
python lab.py triage --input runs/seed-72-baseline/auth.csv --output runs/practice-72-report.json
python lab.py verify --case runs/seed-72-baseline --report runs/practice-72-report.json
```

Use these hints only if needed. Record which ones you used.

- Sort before counting.
- Keep account and source address together.
- Count failures and reported windows separately.
- Compare the gap between retries with the window length.
- A later success still leaves the actor unknown.

## 3. No-notes pass

Generate seed 109 with the baseline scenario. Close the worked example and earlier attempts. Use only that case's data and context. You may use tool `--help` for command syntax. Record that help if you use it. Produce:

- The sequence you would escalate, in time order. Include event IDs and UTC times.
- A priority for each of the three accounts. Give reasons and another possible explanation.
- What the logs cannot prove. Name the exact evidence you would request next.
- A short handover and a separate list of unknowns.

Save the attempt first. Then compare it with the tool output and self-check below. A seed changes labels and time. It keeps the baseline pattern. This tests recall and use of familiar steps. It does not test broad detection skill.

## 4. Changing-scenario drills

Predict the effect before running triage. Use a new report filename for every run. The examples below name their input. This stops the tool from using the default fixture by mistake.

### Success arrives later

```sh
python lab.py generate --seed 86 --scenario late-success
python lab.py triage --input runs/seed-86-late-success/auth.csv --output runs/late-default.json
python lab.py triage --input runs/seed-86-late-success/auth.csv --success-seconds 600 --output runs/late-long-link.json
```

Explain why the failure matches stay the same. Why does the linked-success list change? Find the later success in the full timeline. Does no default link mean no success happened? Does a longer link prove it was the same actor?

### Failures use several addresses

```sh
python lab.py generate --seed 93 --scenario distributed
python lab.py triage --input runs/seed-93-distributed/auth.csv --output runs/distributed.json
```

The staff sequence now has six failures across three documentation addresses. Use `timeline` to put that account's events in order. Explain why the same-account-and-address rule misses it. Describe a further review grouped by account, in plain words. Zero candidates does not mean “safe”. An account-wide group may combine different users of a shared account. It needs context too.

### A wider window and a different threshold

```sh
python lab.py triage --window-seconds 3600 --output runs/wide-window.json
python lab.py triage --threshold 7 --output runs/higher-threshold.json
python lab.py triage --threshold 2 --output runs/lower-threshold.json
```

These three commands use the checked-in fixture on purpose. Explain the tradeoff. A higher threshold may miss activity that needs review. A lower threshold or wider window may add mistakes and service faults. Which matches help? Which would be false positives for an attack claim? What extra evidence would help? No single setting fits every case.

For each scenario, run `verify --case CASE_DIRECTORY --report REPORT_FILE` after triage. Use `fixture` as the case for the final three commands. Explain what a PASS does and does not tell you.

## Self-check after saving your answer

Use these prompts to review your work. They do not give a score:

- Did I cite exact records and UTC times? Or did I just repeat the tool's label?
- Did I count only failures inside the chosen window, and identify overlaps?
- Did I inspect the complete sequence after filtering failures?
- Did I separate what the log shows, a made-up note and my own view?
- Did I explain a possible harmless cause without claiming it was proven?
- Did I avoid treating a linked success or an empty report as a final security verdict?
- Could another reader continue from my handover without guessing which records I mean?

Read these check values only after making your prediction:

| Case and settings | Expected result |
| --- | --- |
| Baseline defaults | Two windows and one pair |
| Late-success defaults | Two windows; no linked successes |
| Late-success with a 600-second link | The later success links to both windows |
| Distributed defaults | Zero windows |
| Fixture with a 3600-second window | Four windows and two pairs |
| Fixture with threshold 7 | Zero windows |
| Fixture with threshold 2 | Six windows across two pairs |

These values check the maths. They do not judge your reasoning.
