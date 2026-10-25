# Practice progression: Trace dummy secret exposure through config, diffs and logs

Use the exact prepare/show/check commands in [README.md](README.md). Save a
prediction before running `analyse`. Fresh folders preserve earlier attempts.

1. **Guided (10 minutes):** read all three artifacts, record audience and line
   number, then save a proposed remediation sequence before viewing the example.
2. **With prompts (5 minutes):** Does a removed diff line remain readable? Does
   redacting one log revoke a credential? Can you report locations without values?
3. **Independent (10 minutes):** prepare `challenge` in a fresh folder.
   Inspect the supplied configuration, differences and logs. Record exposures, scope limits and an ordered response, including anything the configured analyser might not cover.
   Save decisions, evidence references and a short handover before opening
   `analyse`, reference answers or the worked example. Record any help used.
4. **Changed evidence (5 minutes):** use `changed`. Why does a revoked value
   still need attention in a retained diff? In a practice copy change only its
   state back to active, predict the sequence, and check it. Do not edit originals.
5. **Teach back (5 minutes):** explain deletion, redaction, revocation and
   rotation using the dummy case. State which action actually invalidates access.
6. **Later recall (next day, 5 minutes):** name three exposure paths beyond the
   current config and two things an exact-marker scan cannot establish.

For each pass record: evidence references, decision, reason, uncertainty, help
used and one next check. Have another person review the explanation and one
unfamiliar case if possible. Until that occurs, independent completion is
unassessed even if every decision matches. Keep all attempts below `run/`.
