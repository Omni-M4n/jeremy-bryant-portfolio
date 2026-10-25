# Practice stages

1. **Guided.** Prepare `run/guided-01`, predict four counts, run installed Snort
   with the README command and locate the actual rule identifier in stdout.
2. **Prompts only.** Use a fresh attempt and result folder. Keep this checklist:
   header; exact marker; positive and negative controls; rule version; engine
   exit; stderr; observed counts; limitation. Keep the worked example closed.
3. **Independent.** Prepare `run/independent-01`. Explain all four inputs,
   inspect frame 4 in Wireshark if available, operate Snort and produce a short
   finding from actual outputs. Name any help used.
4. **Changed input to the detector.** Prepare `run/changed-01`; make the README's
   nocase/revision edit; predict and test the new outcomes. Explain why the
   wrong-port control is unaffected. In a separate fresh attempt, changing the
   rule destination port from 18080 to 18081 tests a different condition:
   predict wrong-port one and the other three zero. The wrapper's two built-in
   expectation sets do not describe this optional variant, so its
   `needs_review` result is expected; compare saved actual counts with your own
   written prediction and explain the mismatch.
5. **Teach-back.** Explain why an alert on a harmless marker is not an attack
   finding. Explain how the negative controls challenge the rule. Show the
   difference between an expected count and a recorded engine result.
6. **Later recall.** After two days, describe `-r`, `-R`, SID and nocase without
   the guide. After a week, repeat a fresh run and explain why the same marker
   in the loopback capture would require different rule-header conditions.

Do not edit the shipped fixtures or their hashes to make a check pass. If the
engine is unavailable, complete the prediction work and label practical
execution pending. A reviewer should assess the explanation and operation,
not merely whether an output file exists.
