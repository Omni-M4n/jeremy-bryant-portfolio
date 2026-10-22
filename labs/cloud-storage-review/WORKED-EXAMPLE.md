# Worked example: Trace a storage exposure path

Open this after saving a prediction for the guided case. The reference explains
these fictional records; it does not assess your independent performance.

1. Read `handover.txt`, then the four records in `data.buckets`. There is no
   account-wide block in the guided case.
2. `poster-site` has a policy grant, no ACL grant and no blockers. Its purpose is
   `public-site`, class is `public`, and approval is `approved`, so use
   `public-read-approved`. This says nothing about content correctness.
3. `volunteer-rota` has an ACL grant even though policy read is false. With no
   blocker, the internal rota is `public-read-unapproved`. Removing a nonexistent
   policy grant would not close this route.
4. `archive` has a policy grant and `bucket_block_public=true`, so use
   `blocked-public-grant`. Cite both fields; calling it grant-free loses the
   risk that the public grant would return after the block was removed.
5. `receipts` has no public policy or ACL grant: `no-public-grant`. Restricted
   classification alone is not the control producing this result.

Before looking at the answer, write the expression `(policy OR acl) AND NOT
(account OR bucket OR deny)` for each record. A sound handover identifies the
rota exposure route and proposes checking intended access before changing a
control that might also serve the public poster. No actual cloud change occurs.

After comparison, keep your original prediction and add a correction in
`notes.txt`. State the evidence that changed your judgment. Copying the answer
without reconstructing the evidence leaves independent understanding unassessed.
