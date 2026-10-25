# Practice drills

Use the tool as supplied. You do not need to write Python or memorise flags. Do not replay requests. Keep notes under `runs/`. Use a new filename for each attempt. The generator refuses an existing case folder, even one with only notes.

## 1. Guided reading

Run the reference timeline. Find one request's method, target, status and response-body size. Look at `HEAD /guides`, status `200`, with zero body bytes. Explain why it is not a failed request. Find the contact-form request. Name the missing header that would show where its redirect leads.

```sh
python lab.py timeline
python lab.py timeline --source-ip 203.0.113.138
```

Compare two claims: “the server returned a successful HTTP response” and “someone successfully authenticated.” Explain how they differ. Write your answer before checking the worked example.

## 2. Use a short checklist

```sh
python lab.py generate --seed 72 --scenario mixed
python lab.py timeline --case runs/seed-72-mixed
python lab.py triage --case runs/seed-72-mixed --output runs/attempt-72.json
python lab.py check --case runs/seed-72-mixed --report runs/attempt-72.json
```

Keep the worked answer closed. Record the coverage, busiest source and watched-path source. Add evidence IDs, one possible harmless explanation and one next check. Explain why two sources can share a user-agent without being the same actor. A new seed changes labels and times. It does not change the reasoning problem. Try one of the next variants to test those skills in a new case.

## 3. Change the response

```sh
python lab.py generate --seed 88 --scenario soft-200
python lab.py timeline --case runs/seed-88-soft-200
python lab.py triage --case runs/seed-88-soft-200 --output runs/attempt-88.json
```

Find what changed in the evidence. Which prompt was added? Give two possible causes for the watched-path `200`. Name evidence that could tell them apart. You have a byte count and a fallback-route note. Explain why these are not the same as seeing the response body.

## 4. Lose part of the evidence

```sh
python lab.py generate --seed 91 --scenario logging-gap
python lab.py timeline --case runs/seed-91-logging-gap
python lab.py triage --case runs/seed-91-logging-gap --output runs/attempt-91.json
```

Name the gap interval and the requests that remain. Which rule no longer matches? Write a finding that holds despite the missing records. A lower count might not mean less suspicious activity. What should you request before making that claim? Gaps in event IDs alone do not always prove missing logs. Use the supplied coverage record in this case.

## 5. Challenge a noisy rule

```sh
python lab.py generate --seed 102 --scenario crawler-only
python lab.py triage --case runs/seed-102-crawler-only --output runs/attempt-102.json
python lab.py triage --case runs/seed-102-crawler-only --volume-threshold 13 --output runs/attempt-102-threshold13.json
```

Explain why the default volume rule matches. Why does a higher threshold remove the prompt? The records did not change. Does a quieter report prove the new threshold is better? Describe the real baseline and missed-case evidence you would need to decide.

## 6. Explain an unfamiliar case

Ask a study partner to choose a fresh seed and one of the four scenarios. They should give you the case folder, not their answer. If working alone, take a break. Then choose a different scenario and keep the reference answer closed.

Produce a short handover containing:

- The collection scope, coverage and exact settings.
- A finding tied to event IDs. Include the methods, paths and statuses seen.
- Another possible explanation. State a limit on what you can conclude.
- The next evidence request that could change your decision.
- One false positive or a case the simple rules could miss.

Then use `check --case YOUR-CASE --report YOUR-REPORT` to check files and calculations. Compare your reasoning with the scenario discussion in the worked example. Record fixes honestly. A passing software check does not prove understanding. Explaining a fresh variant without the answer is stronger evidence.
