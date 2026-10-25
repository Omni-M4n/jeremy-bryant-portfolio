# Practice stages

1. **Guided.** Follow the README and record real frame numbers. Explain L2 before opening the worked example. Save your capture and worksheet.
2. **Prompts only.** Use a new run, `run/prompts-01`. Check the loopback interface and current ports. Start capture before Enter. Decode HTTP if needed. Pair each request with its response. Inspect L4 without an HTTP filter.
3. **Independent.** Run `python lab.py run --scenario independent --out
   run/independent-01` on one line. Keep the full guide closed. Explain the three types of result and cite the frames. State what help you used.
4. **Changed input.** Run `python lab.py run --scenario changed --out
   run/changed-01` on one line. Predict whether the query words change the HTTP results. Compare L3's exact header bytes with the guided capture. Save your prediction before checking the results.
5. **Teach-back.** Explain to a beginner why "404 means the server is down" lacks support. Show how `http` hides L4. Explain why you chose loopback in place of a physical network interface.
6. **Later recall.** After two days, explain capture and display filters from memory. Then check your answer. After a week, make a fresh capture. Explain one result you did not expect. Use new frame numbers from that run.

You should be able to operate the tool and link each claim to evidence. Explain the limits in a new run. Finishing a command does not prove skill. If capture is not available, label the work "traffic generation only; capture pending". Keep that limit clear in any portfolio text.
