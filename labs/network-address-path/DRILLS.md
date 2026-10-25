# Practice with fewer prompts

Use a new `run/attempt-NN` folder each time. Record date, Python version, case identity, first prediction and help used. Preserve the initial worksheet before `check` or `analyse`, because either command can reveal reference labels. Mark a stage such as "guided with help", "independent attempt awaiting review" or "corrected after review"; do not turn a passing script into a mastery claim.

## Guided pass: 30-40 minutes

Prepare `guided` as shown in the README. Draw the supplied topology. For every request, record the destination IP, all matching prefixes, selected route, next hop and limit. Save your first answer, then use the worked example and check output. Keep any corrections beside the first prediction.

## Prompts only: 15 minutes

Prepare `guided` again in a new folder with the worked example closed. Ask yourself: Do I have an address yet? Is this the host itself? Which prefixes contain the address? Which has the most prefix bits? Is metric comparison needed? Does the winner name a gateway? Which address would ARP resolve? Avoid looking at your first result until the new answer is saved.

## Independent case: 20-30 minutes

Prepare `challenge` and use only its case, snapshot, the README's model rules and a blank worksheet. Close `WORKED-EXAMPLE.md`, `reference/`, tests and previous answers. Produce an annotated diagram and one evidence-supported sentence per request. State uncertainty explicitly and propose a narrow next check. Save your first attempt before using `check`; ask a reviewer to assess it. This section deliberately provides no case answers.

## Changed subnet: 15-25 minutes

Prepare `changed`. Before analysing, compare the interface prefix and each route with the guided case. Identify which earlier assumptions need reconsideration. Work out the address ranges on paper and complete a fresh worksheet. Explain why a changed mask can change delivery even when the destination's dotted address is identical. Do not alter a real adapter or route table. Keep the changed-case decisions unrevealed until the prediction is saved.

## Teach-back: 5 minutes

Explain a name-to-IP step, an on-link step and a gateway step to a reviewer. Have them ask why a lower metric might still lose, why the IP destination does not become the gateway, and what a first-hop prediction cannot prove. Point to the fields rather than reciting labels. Save the questions, any correction and help used.

## Later recall

On another day, reconstruct the selection order without opening the notes. About a week later, have a reviewer choose one unfamiliar destination within an existing supplied route and ask for a prediction from the snapshot alone. They should check the prefix arithmetic independently. If using a new JSON case, keep all mirrored text consistent and the original files untouched; a custom case has no shipped reference receipt. Retain the first answer, then review it.
