# Worked example: Reconcile joiner, mover and leaver access

Save a prediction for the guided case before you read this page. These are made-up records. The answer does not assess your skill at doing this alone.

1. `as_of` is `2026-10-23`. Compare it with each `effective_on` date before you work out the sets. All three guided events are due.
2. `new-starter` has no access. They need `mail` and `casework`. The target is `{casework, mail}`. Use `add:casework,mail;remove:none;retain:none`.
3. `team-move` took effect on `2026-10-22`. The required set is `{mail, new-queue}`. An approved exception keeps `old-reports` through `2026-10-23`. Today's target is `{mail, new-queue, old-reports}`. There is no exception for `old-queue`. Use `add:new-queue;remove:old-queue;retain:mail,old-reports`. Removing all old access would wrongly remove mail and the handover access. Adding only the new queue would leave old access that is no longer needed.
4. `departed` leaves today, so the target is empty. Use `add:none;remove:casework,mail;retain:none`. This is a proposal to change access. It does not prove that sign-in sessions have ended or credentials have stopped working.

In your handover, cite `team-move.exceptions[0].expires_on`. A review on the next day must remove `old-reports` unless new, approved evidence permits it.

Keep your first prediction. Add a correction in `notes.txt` after you compare it with the answer. State which evidence changed your view. Work through the evidence yourself. Copying an answer does not show that you understand it.
