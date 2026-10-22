# Worked example: Trace dummy secret exposure through config, diffs and logs

Open this after saving a prediction for the guided case. The reference explains
these fictional records; it does not assess your independent performance.

1. Read `app-config.txt`, `change-diff.txt` and `debug-log.txt` with their
   audience fields. Current config uses a store reference for the export value,
   but this is only one possible copy.
2. `export-token` occurs at `change-diff.txt:L1` in a removed line and at
   `debug-log.txt:L2`. Their audiences are shared and public. The supplied state
   is active. Use `contain;revoke-and-replace;clean-copies;review-use`.
   Deleting the config line did not invalidate the value or erase retained copies.
3. `local-token` occurs only at `app-config.txt:L2` with audience local. Use
   `relocate-before-sharing`. Do not paste the value into a real report.
4. `unused-token` has no exact listed occurrence: `not-seen-in-supplied-artifacts`.
   This does not establish it was never exposed or that these files are secret-free.

A handover can cite IDs and locations without reproducing credential text.
Explain that access restriction and revocation/rotation address ongoing misuse;
cleaning history and logs then addresses retained copies. Review use for evidence
of earlier access. All these are proposed steps for dummy evidence, not actions
performed by the command.

After comparison, keep your original prediction and add a correction in
`notes.txt`. State the evidence that changed your judgment. Copying the answer
without reconstructing the evidence leaves independent understanding unassessed.
