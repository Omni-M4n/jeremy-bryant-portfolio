# Worked example: Build a cloud audit evidence timeline

Save a prediction for the guided case before you read this page. These are made-up records. The answer does not assess your skill at doing this alone.

1. Sort the time line. At 10:00, `e01` is a successful sign-in for `operator` and `session-a`. Use `authentication-only`.
2. At 10:02, `e02` has the same identity and session. But `result=denied`. Use `denied-no-success-evidence`. A sign-in link does not turn failure into success.
3. At 10:03, `e03` changes `poster-bucket`. It is three minutes after `e01`. It matches the approval's identity, action and resource. It also falls within the approved time of 10:00-10:10. Use `approved-change-correlated`.
4. At 10:04, `e04` reads `rota-object` and links to `e01`. Use `successful-read-correlated`. This does not prove that a data-access approval allowed the read. This model has no such approvals.
5. `e05` has a different identity and session. No supplied sign-in matches it. The action worked, so use `successful-action-unattributed`. Do not invent a person behind it.
6. `e06` turns logging off. It links to `e01` but has no approval. Use `unapproved-change-correlated`. The `logging` answer is `coverage-gap:data;interruption-observed`. Data logging was off at the start. The later successful disable event adds evidence of an interruption.

The `e04` record does not fill the data gap. In your handover, ask for the missing logs and change approvals. Keep known successes separate from denied attempts. State what you cannot know about activity that was not logged.

Keep your first prediction. Add a correction in `notes.txt` after you compare it with the answer. State which evidence changed your view. Work through the evidence yourself. Copying an answer does not show that you understand it.
