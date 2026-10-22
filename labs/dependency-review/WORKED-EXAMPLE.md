# Worked example: Triage a fictional software inventory and advisory ranges

Open this after saving a prediction for the guided case. The reference explains
these fictional records; it does not assess your independent performance.

1. Read the two supplied fictional advisory ranges. `DEMO-ADV-001` covers
   demo-parser from 1.9.0 inclusive to 1.10.0 exclusive. `DEMO-ADV-002` covers
   demo-builder from 2.0.0 inclusive to 2.0.5 exclusive.
2. `upload-parser` version 1.9.9 becomes `(1,9,9)`. It is at least `(1,9,0)`
   and below `(1,10,0)`, so it matches DEMO-ADV-001. It is runtime with a supplied
   request-map path: `affected-prioritise-runtime-path`. This supports priority,
   not a claim that an exploit has occurred or must work.
3. `asset-builder` 2.0.4 lies inside its range. Development scope does not
   erase risk to build inputs or outputs. Use `affected-review-build-exposure`.
4. `theme-helper` has no supplied advisory: `no-advisory-supplied`. Do not
   translate that into "no vulnerabilities".

A handover should identify the affected package/version and advisory ID, cite
reachability evidence, and propose checking an update's compatibility and
remaining ranges. The changed case places two components exactly at fixed
boundaries so you can test the exclusive upper-bound rule independently.

After comparison, keep your original prediction and add a correction in
`notes.txt`. State the evidence that changed your judgment. Copying the answer
without reconstructing the evidence leaves independent understanding unassessed.
