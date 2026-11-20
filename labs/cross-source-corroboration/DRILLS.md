# Practice sequence

Keep each first answer. Add later fixes below it or use a new file. Do not replace it with the model answer. Stage labels show which practice you have done. They do not prove that you have mastered the skill.

## 1. Guided stage

Prepare Collection 01 using the README. Explain the everyday example aloud. Write what you think each decision field will say before you run the task. Save your own reasons before you read WORKED-EXAMPLE.md.

## 2. Prompts only

Close the worked example and start a fresh attempt. Ask: Which value did I observe? Which is a label? Which values support my claim? What does a missing record leave unknown? Name the source and copied file for each fact you use.

## 3. Solo stage (not independently assessed)

I will run `python lab.py prepare --scenario challenge --out run/attempt-02` and `python lab.py show --case run/attempt-02/case.json`. I will keep `reference/` and the analyse command closed while I use only the evidence I can see, give another explanation and state my next check. I will then run `python practice.py run --scenario challenge --out run/practical-02` and record what its bounded dummy-data evidence shows. I will save both answers before I run check or analyse. The shipped challenge and reference answer are supplied solo practice, not a reviewer-prepared fresh unseen assessment; unless a reviewer provides and reviews a different supported case, I will mark fresh-case review as awaiting review rather than call this attempt independent.

## 4. Changed case

Run `python lab.py prepare --scenario changed --out run/attempt-03`. Predict which facts matter in this case. Do not assume it matches Collection 01. Run `python practice.py run --scenario changed --out run/practical-03`. Explain which result changed when the input changed. State which limits still apply. Save the answer before checking it.

## 5. Teach-back

Explain this question to a younger student: Which proposed event links survive identifier, content and clock checks? Use the everyday example first. Explain two technical words. Point to one exact field or file. Name one claim you chose not to make because you lacked proof.

## 6. Later recall

After two days, close the guides. Recall the safe steps: start a fresh attempt and keep the source safe. Write what you expect to find, then inspect the copied evidence. Compare the values and state the limits. Try a case you have not seen in a new folder. Note which help you used.

## Handover

Give a reviewer your first answer and final reasons. Include the item references and the receipt from the actual task. Explain the changed case and list one open question. Ask the reviewer to check your reasoning. Correct fields or tests alone do not prove that you understand.
