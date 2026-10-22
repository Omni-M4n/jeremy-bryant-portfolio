# Repeat the exercise with less help

Keep a short note for each attempt inside `runs/`. Record the seed, scenario, rule settings, time spent, help used and one correction you made. These are self-reported practice notes, not assessed results. Do not replace an earlier attempt with an improved answer; a separate note makes progress easier to inspect.

## 1. Guided pass

Use the checked-in fixture and the command reference in `README.md`.

1. Run `verify` to establish which supplied files you are using.
2. Use `timeline --outcome failure` to select failures, then filter each account separately. **Filtering** means selecting records that match a condition. Remove the outcome filter before checking for a success.
3. Write the first and last relevant UTC times and record IDs. Count the failures in a five-minute interval yourself.
4. Read the invented account notes. Write one observed fact and one possible explanation for each account.
5. Run `triage`, compare its event IDs with yours, and explain why two overlapping windows do not establish two incidents.
6. Draft a short handover with evidence, uncertainty and the next check. Compare it with `WORKED-EXAMPLE.md`, then note your corrections.

## 2. Hints-only pass

Create a fresh case:

```sh
python lab.py generate --seed 72
python lab.py verify --case runs/seed-72-baseline
```

Read its `context.json` and inspect `auth.csv` or `auth.jsonl`. Without the worked example, identify the sequence that deserves review, explain the two other patterns, and write a handover. Then run the tool against this input and verify the report:

```sh
python lab.py triage --input runs/seed-72-baseline/auth.csv --output runs/practice-72-report.json
python lab.py verify --case runs/seed-72-baseline --report runs/practice-72-report.json
```

Use these hints only if needed: sort before counting; keep account and source address together; distinguish the number of failures from the number of reported windows; compare retry spacing with the window length; a later success still leaves the actor unknown. Record which hints you used.

## 3. No-notes pass

Generate seed 109 with the baseline scenario. Close the worked example and previous attempts. Use only that case's data and context. Tool `--help` is allowed for command syntax; record that you used it. Produce:

- A chronological account of the sequence you would escalate, with event IDs and UTC times.
- A reasoned priority for each of the three accounts, including a competing explanation.
- A statement of what the logs cannot establish and the specific next evidence you would request.
- A concise handover and a separate list of unknowns.

Only after saving the attempt, compare it with the tool output and the self-check below. A seed changes labels and time but preserves the baseline pattern; this tests recall and basic transfer, not broad detection skill.

## 4. Changing-scenario drills

Predict the effect before running triage. Use a new report filename for every run. The examples below name the input so that the tool cannot silently use the default fixture instead.

### Success arrives later

```sh
python lab.py generate --seed 86 --scenario late-success
python lab.py triage --input runs/seed-86-late-success/auth.csv --output runs/late-default.json
python lab.py triage --input runs/seed-86-late-success/auth.csv --success-seconds 600 --output runs/late-long-link.json
```

Explain why the failure matches remain the same while the linked-success list changes. Find the actual later success in the full timeline. Does the absence of a default link mean no success happened? Does a longer link establish the same actor?

### Failures use several addresses

```sh
python lab.py generate --seed 93 --scenario distributed
python lab.py triage --input runs/seed-93-distributed/auth.csv --output runs/distributed.json
```

This changes the staff sequence to six failures spread across three documentation addresses. Reconstruct it by account with `timeline`. Explain why the same-account-and-address rule misses it. Describe an additional account-level review in plain language; do not change the conclusion to “safe” because the report has zero candidates. Account-wide grouping can also combine unrelated users of a shared account, so it needs context.

### A wider window and a different threshold

```sh
python lab.py triage --window-seconds 3600 --output runs/wide-window.json
python lab.py triage --threshold 7 --output runs/higher-threshold.json
python lab.py triage --threshold 2 --output runs/lower-threshold.json
```

These three commands deliberately use the checked-in fixture. Identify the tradeoff: a higher threshold may miss concerning activity; a lower threshold or wider window may add ordinary mistakes and service faults. Which matches are useful, which would be false positives for an attack claim, and which extra evidence would help? No single setting is universally correct.

For each scenario, run `verify --case CASE_DIRECTORY --report REPORT_FILE` after triage; use `fixture` as the case for the final three commands. Explain what a PASS does and does not tell you.

## Self-check after saving your answer

Use these prompts for reflection rather than a numerical score:

- Did I cite specific records and UTC times instead of merely repeating the tool's label?
- Did I count only failures inside the chosen window, and identify overlaps?
- Did I inspect the complete sequence after filtering failures?
- Did I separate a log observation, an invented context note and my inference?
- Did I explain a plausible benign cause without declaring it independently proven?
- Did I avoid treating a linked success or an empty report as a final security verdict?
- Could another reader continue from my handover without guessing which records I mean?

Suggested check values, to read only after predicting: baseline defaults produce two windows and one pair; late-success defaults produce two windows with no linked successes, while a 600-second link includes the later success in both; distributed defaults produce zero windows. On the fixture, a 3600-second window produces four windows and two pairs, threshold 7 produces zero, and threshold 2 produces six windows across two pairs. These values check calculations, not the quality of your interpretation.
