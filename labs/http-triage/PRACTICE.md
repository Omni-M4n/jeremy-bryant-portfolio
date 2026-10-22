# Practice drills

Use the utility as supplied. You do not need to write Python, memorise flags or
replay requests. Keep notes under `runs/`, using a new filename for each attempt.
The generator refuses an existing case directory, even if it contains only notes.

## 1. Guided reading

Run the reference timeline and identify one request method, target, status and
response-body size. Explain why `HEAD /guides`, status `200`, with zero body bytes
is not a failed request. Find the contact-form request and name the missing
header that would tell you where its redirect leads.

```sh
python lab.py timeline
python lab.py timeline --source-ip 203.0.113.138
```

Write the difference between “the server returned a successful HTTP response”
and “someone successfully authenticated.” Check the worked example only after
writing your answer.

## 2. Use a short checklist

```sh
python lab.py generate --seed 72 --scenario mixed
python lab.py timeline --case runs/seed-72-mixed
python lab.py triage --case runs/seed-72-mixed --output runs/attempt-72.json
python lab.py check --case runs/seed-72-mixed --report runs/attempt-72.json
```

Keep the worked answer closed. Record the coverage, busiest source, watched-path
source, evidence IDs, one plausible benign explanation and one next check.
Explain why the two sources can share a user-agent without being the same actor.
The changed seed alters labels and times; it does not create a different reasoning
problem. Complete one of the next variants to test transfer.

## 3. Change the response

```sh
python lab.py generate --seed 88 --scenario soft-200
python lab.py timeline --case runs/seed-88-soft-200
python lab.py triage --case runs/seed-88-soft-200 --output runs/attempt-88.json
```

Identify what changed in the evidence and which prompt was added. Give two
possible explanations for the watched-path `200`. Name the evidence that would
distinguish them. Explain why a byte count and a fallback-route note are not
equivalent to seeing the response body.

## 4. Lose part of the evidence

```sh
python lab.py generate --seed 91 --scenario logging-gap
python lab.py timeline --case runs/seed-91-logging-gap
python lab.py triage --case runs/seed-91-logging-gap --output runs/attempt-91.json
```

Name the gap interval, the retained requests and which rule no longer matches.
Write a conclusion that remains valid despite the missing records. What should
you request before treating the lower count as a reduction in suspicious activity?
Event IDs with gaps alone are not a universal method for proving missing logs;
use the provided coverage record in this case.

## 5. Challenge a noisy rule

```sh
python lab.py generate --seed 102 --scenario crawler-only
python lab.py triage --case runs/seed-102-crawler-only --output runs/attempt-102.json
python lab.py triage --case runs/seed-102-crawler-only --volume-threshold 13 --output runs/attempt-102-threshold13.json
```

Explain why the default volume rule matches and why increasing its threshold
removes the prompt. The records did not change. Does a quieter report establish
that the new threshold is better? Describe what real baseline and missed-case
evidence you would need before deciding.

## 6. Explain an unfamiliar case

Ask a study partner to choose a fresh seed and one of the four scenarios. They
should give you the case folder, not their answer. If working alone, choose a
different scenario after a break and keep the reference answer closed.

Produce a short handover containing:

- Collection scope, coverage and exact settings.
- A finding tied to event IDs and observed methods, paths and statuses.
- A plausible alternative explanation and a limit on what can be concluded.
- A next evidence request that could change your decision.
- One example of a false positive or a case the simple rules could miss.

Then use `check --case YOUR-CASE --report YOUR-REPORT` for file and calculation
integrity. Compare your reasoning with the scenario discussion in the worked
example. Record corrections honestly. A passing software check is not proof of
understanding; explaining a fresh variant without the answer is stronger evidence.
