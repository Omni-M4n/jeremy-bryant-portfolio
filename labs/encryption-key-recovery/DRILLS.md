# Practice sequence

1. **Guided, 30 minutes.** Prepare `guided`. Find the exact source bytes and
   predict each decision. Save before opening the worked example. Which values
   does the helper work out? Which does it just read from a made-up receipt?
   Keep the first attempt and corrections.
2. **Prompted.** What is each sample's goal: changing its form, keeping it
   secret or comparing it? For each backup, draw the things needed to recover it.
   Start with the stored object. Add the exact key, access rights and checked
   output. Give a ledger reference for each claim.
3. **Independent, 20-30 minutes.** Prepare `challenge` in `run/independent-01`.
   Close references, the worked example and `analyse`. Explain every decision.
   Choose one next check for each open question. Save before running `check`.
   Keep claims within what each receipt shows.
4. **Changed case, 20 minutes.** Prepare `changed` in `run/changed-01`. Track
   the exact bytes and which key each object needs. Write a dummy recovery plan.
   State which parts have evidence and which still need checks. Use no real key
   or account.
5. **Boundary experiment.** In a fresh attempt copy, compare no restored text
   (`null`) with an actual empty string (`""`). Then edit one source newline.
   Predict before analysis. Try a badly formed Base64 string. How does rejection
   differ from a valid encoding of different bytes? Keep fixtures unchanged.
   If you edit a copy, update its readable notes too.
6. **Teach-back.** Explain why a correct digest, a ciphertext copy, a key ID
   and a success receipt answer different questions. Ask a reviewer to challenge
   a claim that goes too far. Keep the correction.
7. **Recall.** Tomorrow, write the comparison and recovery rules without notes.
   In about a week, ask a reviewer to change one access right, key state or text
   in a fresh valid case. Repeat with solutions closed.

Record stage, date, input, evidence, help and corrections. Passing helper checks
does not show that you used an encryption tool yourself. That needs a separate
approved task. It also does not replace a reviewed explanation of a new case.
