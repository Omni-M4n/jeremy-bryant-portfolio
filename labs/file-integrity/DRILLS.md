# Practice: make and explain your own finding

Use a fresh folder for each attempt. These are optional practice stages, not
recorded passes or evidence of professional work. Before opening the supplied
`expected-findings.json`, write a short note with: observation, approval match,
baseline confidence, uncertainty, and next action.

## Guided: a routine approved change

```console
python lab.py generate --variant approved --seed 41 --run run-approved
python lab.py baseline --run run-approved
python lab.py check --run run-approved
```

Explain why a hash difference alone is not an incident. Identify the exact
evidence that permits the notice update. What would happen if the notice
contained `11:00` instead of the approved `10:00`? The same path and ticket
would no longer explain those different bytes.

Expected self-check: one approved edit, no unexpected differences, and a
matching exercise anchor; exit `0`. That result says nothing about your
understanding until you can explain the evidence and limits.

## Hints: an addition and a deletion

```console
python lab.py generate --variant replacement --seed 71 --run run-replacement
python lab.py baseline --run run-replacement
python lab.py check --run run-replacement
```

Read the change list before predicting the result. Do additions always need an
alert? Does a deletion always mean lost data? Explain how `null` represents the
missing side of each approved transition. Why would an exact byte check be more
useful than trusting the replacement report's name?

Expected self-check: the notice, archive deletion, and exact replacement report
are approved; no unexplained changes; exit `0`. This is a different conclusion
from the mixed case, even though both contain an addition and deletion.

## Independent: apparently unchanged, but uncertain

```console
python lab.py generate --variant suspect-baseline --seed 83 --run run-suspect
python lab.py baseline --run run-suspect
python lab.py check --run run-suspect
```

Keep the worked answer closed until you have a finding. Read the scenario's
baseline history and inspect `reference/config/service.txt` and
`current/config/service.txt` with a text editor.

- Does the baseline describe a verified earlier state?
- What does the written requirement say about remote access?
- Can matching hashes resolve the conflict with that requirement?
- What independent evidence would you request before calling the state clean?
- Why could simply accepting a new baseline conceal a problem?

Expected self-check: the notice is approved and the config is reported unchanged,
but the baseline has no anchor; exit `1`. Both copies already contain `enabled`,
which conflicts with the written `disabled` requirement. The comparison alone
cannot reveal when that change happened or who made it.

## Teach it back

Use a fresh mixed case with another seed. Explain one approved change, one
unexpected change, and the baseline's limits without reading the answer key.
Describe a plausible benign explanation for an unexpected change, the evidence
needed to test it, and why you would preserve the observation before repair.
Do not infer an attack from a hash mismatch alone.

An honest portfolio note could say: "I practised comparing synthetic file
inventories with an approved change list using a supplied offline utility."
Add your own specific reasoning and difficulties only after doing the exercise.
Do not claim the supplied utility or example findings as independent work.
