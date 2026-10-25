# Worked example: Trace a storage exposure path

Save a prediction for the guided case before you read this page. These are made-up records. The answer does not assess your skill at doing this alone.

1. Read `handover.txt`, then the four records in `data.buckets`. The guided case has no account-wide block.
2. `poster-site` has a policy grant. It has no ACL grant and no blocks. Its purpose is `public-site`, class is `public`, and approval is `approved`. Use `public-read-approved`. This does not check whether the site's content is right.
3. `volunteer-rota` has an ACL grant. Policy read is false, but the ACL is a separate route. No block applies. Use `public-read-unapproved` for this internal rota. There is no policy grant to remove. Removing one would not close the ACL route.
4. `archive` has a policy grant and `bucket_block_public=true`. Use `blocked-public-grant`. Cite both fields. The grant still exists. It could work again if the block were removed.
5. `receipts` has no public policy grant and no ACL grant. Use `no-public-grant`. Its restricted data class is not what produces this result.

For each record, first write `(policy OR acl) AND NOT (account OR bucket OR deny)`. Use it to predict the answer before you compare. In your handover, name the rota's exposure route. Propose a check of intended access before changing a control. That control might also serve the public poster. No real cloud change takes place.

Keep your first prediction. Add a correction in `notes.txt` after you compare it with the answer. State which evidence changed your view. Work through the evidence yourself. Copying an answer does not show that you understand it.
