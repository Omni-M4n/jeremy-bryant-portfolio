# Worked example: Trace dummy secret exposure through config, diffs and logs

Save a prediction for the guided case before you read this page. These are made-up records. The answer does not assess your skill at doing this alone.

1. Read `app-config.txt`, `change-diff.txt` and `debug-log.txt`. Check each audience field. The current settings use a store reference for the export value. That does not rule out other copies.
2. `export-token` appears in a removed line at `change-diff.txt:L1`. It also appears at `debug-log.txt:L2`. Those files are shared and public. The state is active. Use `contain;revoke-and-replace;clean-copies;review-use`. Deleting the settings line did not stop the value from working. It did not erase the saved copies.
3. `local-token` appears only at `app-config.txt:L2`. The audience is local. Use `relocate-before-sharing`. Do not paste the value into a real report.
4. `unused-token` has no exact listed match. Use `not-seen-in-supplied-artifacts`. This does not prove that it was never exposed. It does not prove that these files have no other secrets.

Cite IDs and locations in your handover without copying secret text. Restricting access and revoking or rotating a value can stop ongoing misuse. Cleaning history and logs deals with saved copies. Review use for signs of past access. These are proposed steps for fake evidence. The command does not carry them out.

Keep your first prediction. Add a correction in `notes.txt` after you compare it with the answer. State which evidence changed your view. Work through the evidence yourself. Copying an answer does not show that you understand it.
