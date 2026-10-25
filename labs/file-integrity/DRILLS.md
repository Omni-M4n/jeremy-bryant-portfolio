# Practice: make and explain your own finding

Use a fresh folder for each attempt. These practice stages are optional. They are not recorded passes or proof of professional work. Keep the supplied `expected-findings.json` closed at first. Write a short note with five parts: observation, approval match, baseline confidence, uncertainty and next action. In plain words, say what changed, what permits it and why you trust the baseline. Add what is still unknown and what you would do next.

## Guided: a routine approved change

```console
python lab.py generate --variant approved --seed 41 --run run-approved
python lab.py baseline --run run-approved
python lab.py check --run run-approved
```

Explain why a hash difference alone is not an incident. Find the exact evidence that permits the notice update. What if the notice had `11:00` instead of the approved `10:00`? The path and ticket would still be the same. They would not explain those different bytes.

Expected self-check: one approved edit and no unexpected differences. The exercise anchor matches; exit `0`. This does not show understanding on its own. You must explain the evidence and limits.

## Hints: an addition and a deletion

```console
python lab.py generate --variant replacement --seed 71 --run run-replacement
python lab.py baseline --run run-replacement
python lab.py check --run run-replacement
```

Read the change list before predicting the result. Do additions always need an alert? Does a deletion always mean lost data? Explain how `null` marks the missing side of each approved change. Why is an exact byte check more useful than trusting the replacement report's name?

Expected self-check: the notice, archive deletion and exact replacement report are approved. There are no unexplained changes; exit `0`. This differs from the mixed case. Both have an addition and deletion, but the approvals differ.

## Independent: apparently unchanged, but uncertain

```console
python lab.py generate --variant suspect-baseline --seed 83 --run run-suspect
python lab.py baseline --run run-suspect
python lab.py check --run run-suspect
```

Keep the worked answer closed until you have a finding. Read the scenario's baseline history. Open `reference/config/service.txt` and `current/config/service.txt` in a text editor.

- Does the baseline describe a checked earlier state?
- What does the written requirement say about remote access?
- Can matching hashes resolve the conflict with that requirement?
- What independent evidence would you seek before calling the state clean?
- Why could simply accepting a new baseline conceal a problem?

Expected self-check: the notice is approved. The config is reported unchanged. But the baseline has no anchor; exit `1`. Both copies already contain `enabled`. The written requirement says `disabled`. The comparison alone cannot show when the change happened or who made it.

## Teach it back

Use a fresh mixed case with another seed. Keep the answer key closed. Explain one approved change, one unexpected change and the baseline's limits. Give a possible harmless reason for an unexpected change. What evidence would test that reason? Why would you preserve what you found before repair? Do not infer an attack from a hash mismatch alone.

An honest portfolio note could say: "I used a supplied offline tool to compare made-up file inventories with an approved change list." Add your own reasoning and difficulties only after doing the exercise. Do not claim the supplied tool or example findings as independent work.
