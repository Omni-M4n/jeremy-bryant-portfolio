# Practice stages

1. **Guided.** Follow the README and fill in actual frame references. Explain
   L2 before opening the worked example. Save your capture and worksheet.
2. **Prompts only.** Use a new run, `run/prompts-01`. Keep only this checklist:
   loopback interface; current ports; capture before Enter; decode HTTP if
   needed; match requests to responses; inspect L4 without an HTTP filter.
3. **Independent.** Run `python lab.py run --scenario independent --out
   run/independent-01` on one line. Keep the full guide closed. Produce the three
   outcome explanations with frame references and identify help you used.
4. **Changed input.** Run `python lab.py run --scenario changed --out
   run/changed-01` on one line. Predict whether the query words change the HTTP
   outcomes. Compare L3's exact header bytes with the guided capture.
5. **Teach-back.** Explain to a beginner why "404 means the server is down" is
   unsupported. Demonstrate how `http` hides L4. Explain why you chose loopback
   rather than a physical network interface.
6. **Later recall.** After two days, write the difference between capture and
   display filters from memory, then check it. After a week, repeat a fresh
   capture and explain one unexpected observation without copying old frames.

Success means you can operate the tool, trace evidence to a claim and explain
the limits on an unfamiliar run. Finishing a command is not automatic mastery.
If capture is unavailable, label your work "traffic generation only; capture
pending" and keep that distinction in any portfolio description.
