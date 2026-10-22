# Worked example: Build a cloud audit evidence timeline

Open this after saving a prediction for the guided case. The reference explains
these fictional records; it does not assess your independent performance.

1. Sort the timeline. `e01` at 10:00 is a successful sign-in for `operator`
   and `session-a`: `authentication-only`.
2. `e02` at 10:02 has the same identity/session, but `result=denied`. Use
   `denied-no-success-evidence`; correlation does not turn failure into success.
3. `e03` changes `poster-bucket` at 10:03. It is three minutes after `e01`
   and matches the approval's identity, action, resource and 10:00-10:10 window.
   Use `approved-change-correlated`.
4. `e04` reads `rota-object` at 10:04 and links to `e01`, so use
   `successful-read-correlated`. It is not evidence that the read was authorised
   by a data-access approval: this model does not include those approvals.
5. `e05` has a different identity and session with no matching supplied sign-in.
   It succeeds, so use `successful-action-unattributed`. Do not invent a person.
6. `e06` successfully disables logging, links to `e01` and has no approval.
   Use `unapproved-change-correlated`. The `logging` decision is
   `coverage-gap:data;interruption-observed`: initial data coverage was false,
   and the later successful disable adds interruption evidence.

The existing `e04` fragment does not fill the data gap. A sound handover asks for
the missing coverage and change-authorisation evidence while distinguishing
known successes, denied attempts and uncertainty about unrecorded activity.

After comparison, keep your original prediction and add a correction in
`notes.txt`. State the evidence that changed your judgment. Copying the answer
without reconstructing the evidence leaves independent understanding unassessed.
