# Practice with fewer prompts

Use a new `run/attempt-NN` folder each time. Record the date, Python version, case ID, first prediction and help used. Save the first worksheet before `check` or `analyse`. Both commands can reveal answer labels. Mark the stage: "guided with help", "independent attempt awaiting review" or "corrected after review". A passing script does not prove skill.

## Guided pass: 30-40 minutes

Prepare `guided` as shown in the README. Draw the supplied topology. For every request, record the destination IP, all matching prefixes, selected route, next hop and limit. Save your first answer, then use the worked example and check output. Keep any corrections beside the first prediction.

## Prompts only: 15 minutes

Prepare `guided` again in a new folder with the worked example closed. Ask yourself: Do I have an address yet? Is this the host itself? Which prefixes contain the address? Which has the most prefix bits? Is metric comparison needed? Does the winner name a gateway? Which address would ARP resolve? Avoid looking at your first result until the new answer is saved.

## Independent case: 20-30 minutes

Prepare `challenge`. Use only its case, snapshot, the README's model rules and a blank worksheet. Close `WORKED-EXAMPLE.md`, `reference/`, tests and past answers. Draw and label the network. Write one sentence per request and name the evidence for it. State what is still unknown and choose a small next check. Save your first attempt before using `check`. Ask a reviewer to assess it. This section gives no case answers.

## Changed subnet: 15-25 minutes

Prepare `changed`. Before analysis, compare its interface prefix and each route with the guided case. Which earlier assumptions still hold? Work out the address ranges on paper and fill in a new worksheet. Explain why changing the mask can change the path even if the dotted address stays the same. Do not change a real adapter or route table. Save your prediction before revealing the changed-case decisions.

## Teach-back: 5 minutes

Explain a name-to-IP step, an on-link step and a gateway step to a reviewer. Ask them to question each step. Why might a lower metric still lose? Why does the IP destination not become the gateway? What can a first-hop prediction not prove? Point to the fields, not just the labels. Save the questions, corrections and help used.

## Later recall

On another day, write the route choice steps without your notes. About a week later, ask a reviewer to choose a new destination within one of the given routes. Predict its path from the snapshot alone. The reviewer should check the prefix maths on their own. If you use a new JSON case, keep all matching text in sync. Keep the original files untouched. A custom case has no answer receipt in this package. Save the first answer, then review it.
