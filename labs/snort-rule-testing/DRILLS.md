# Practice stages

1. **Guided.** Prepare `run/guided-01` and predict four counts. Use the README command to run installed Snort. Find the rule ID in its real stdout output.
2. **Prompts only.** Use fresh attempt and result folders. Check the header and exact marker. Check the positive and negative controls. Record the rule version, engine exit, stderr and counts. State a limit. Keep the worked example closed.
3. **Independent.** Prepare `run/independent-01`. Explain all four inputs. Inspect frame 4 in Wireshark if it is available. Run Snort and write a short finding from its actual output. Name any help used.
4. **Changed input to the detector.** Prepare `run/changed-01`. Make the README's nocase and revision edit. Predict all four outcomes before you test them. Explain any difference. In a separate fresh attempt, change the rule's port from 18080 to 18081. Save your own prediction for each file before running it. The wrapper's two built-in expectation sets do not cover this optional test. Review its `needs_review` result against your own predictions and the saved counts. Explain any mismatch and check the engine status.
5. **Teach-back.** Explain why an alert on a harmless marker does not prove an attack. Show how negative controls test the rule. Explain how an expected count differs from a saved engine result.
6. **Later recall.** After two days, describe `-r`, `-R`, SID and nocase without the guide. After a week, try a fresh run. Explain why the same marker in loopback traffic needs different header conditions.

Do not edit supplied files or their hashes to make a check pass. If Snort is absent, finish your predictions and mark practical execution pending. Ask a reviewer to check your reasons and tool use. An output file alone does not prove the task is done.
