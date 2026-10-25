# Guided worked example

Read this after saving your first attempt. This is a fictional example, not a
claim that a learner or an author ran a real engagement.

Read `risk-notes.txt` G1 for item-1. It describes one handover beside a public
waiting area. That gives a plausible chance of loss: likelihood 2.
It does not show repeated chances. G2 lists home addresses and private support
needs in the offline file. Exposure could reveal sensitive data: impact 3.
The score is 2 x 3 = 6, high. The actual lock state is unknown.
No access to the file is confirmed.

G3 proposes locked storage and named checkout. These could reduce the chance
of loss. Prompt reporting could start a response sooner. Encryption scrambles
stored data; a lock limits use of an unattended device. The plan also removes
sensitive support fields from the offline cache, a stored local copy.
It would leave only a small team's work numbers. That could limit harm.
These facts explain the proposed 1 x 2 score. No control check is supplied.
The lower score remains a projection: an estimate of a future state.

For item-2, G4 places a visitor outside a closed badge door. Entry would need
an unusual access mistake: likelihood 1. G5 names the sole work rota.
Its loss could stop the booking team's work: impact 2.
The score is 1 x 2 = 2, low. The owner has not agreed to accept the risk.
Ask for that decision and keep the supplied review date.

These are reasons from the lab's rubric, not measured chances of harm.
A different score needs sound reasons from the same facts.
The helper still checks the values supplied in JSON. Put any alternative
score or treatment in the register for human review.

Expected guided decision strings:

```json
{
  "item-1": "high;reduce;review-planned;projection-only",
  "item-2": "low;accept;owner-acceptance-needed;projection-only"
}
```

Keep the first attempt. Write corrections in a separate file, explaining which
fact changed your answer. A useful explanation names the evidence and its limit.
