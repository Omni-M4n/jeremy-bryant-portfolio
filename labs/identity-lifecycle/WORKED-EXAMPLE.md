# Worked example: Reconcile joiner, mover and leaver access

Open this after saving a prediction for the guided case. The reference explains
these fictional records; it does not assess your independent performance.

1. `as_of` is `2026-10-23`. Compare this date with each `effective_on` before
   doing any set arithmetic. All three guided events are due.
2. `new-starter` currently has nothing and requires `mail` and `casework`.
   Target is `{casework, mail}`: use
   `add:casework,mail;remove:none;retain:none`.
3. `team-move` took effect on `2026-10-22`. Required access is `{mail,
   new-queue}`. `old-reports` has an approved exception through `2026-10-23`,
   so today's target is `{mail, new-queue, old-reports}`. `old-queue` has no
   exception. Use `add:new-queue;remove:old-queue;retain:mail,old-reports`.
   Removing everything from the old role would incorrectly remove mail and
   the authorised handover; adding only the new queue would leave stale access.
4. `departed` leaves today, so target is empty. Use
   `add:none;remove:casework,mail;retain:none`. The result is an access proposal,
   not confirmation that sessions or credentials have been revoked.

In a handover, cite `team-move.exceptions[0].expires_on` and state that a review
on the next day must remove `old-reports` unless new authorised evidence exists.

After comparison, keep your original prediction and add a correction in
`notes.txt`. State the evidence that changed your judgment. Copying the answer
without reconstructing the evidence leaves independent understanding unassessed.
