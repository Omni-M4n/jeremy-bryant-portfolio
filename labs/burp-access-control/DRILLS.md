# Practice sequence

Use only this lab's printed loopback URL. Each attempt needs a new `run/` child. Keep the worksheet and request/response evidence. No script proves mastery. You do not need to write code at any stage.

## 1. Guided: follow and explain

Follow the README with `guided` data. Before changing an ID, state what will stay the same and what will change. Explain why the stored owner matters. Finish the vulnerable and fixed comparisons. Then read the worked example. Note any gap between your prediction and real evidence.

Show one intercepted baseline and manual Repeater checks for both accounts. Show the fixed-mode denial and retained access to each account's own records. Explain the scope of the result. An automated test cannot satisfy this check.

## 2. Prompted: use a small checklist

Close the worked example. Start fresh runs, for example:

```text
python -B lab.py serve --mode vulnerable --scenario guided --out run/prompted-vulnerable-01
```

After your checks, stop the server and start:

```text
python -B lab.py serve --mode fixed --scenario guided --out run/prompted-fixed-01
```

Check the exact scope and selected account. Save an unchanged baseline. Change one object ID. Read both status and content. Use fresh sessions after restart. Check other-user denial and own-user access. State one limit. If you need the full guide, note where and keep going. That reminder shows what you can practise next.

## 3. Independent: write the plan first

Use new names such as `run/independent-vulnerable-01` and `run/independent-fixed-01`. Reproduce the finding and retest without the worked example. Before sending anything, make a small table of planned requests. Include both accounts and each existing order. Add one unknown ID, one invalid ID and one request with no session. Predict the status and content for each request separately.

Write a short handover from your evidence. Ask someone to check that the account stayed the same within each ID comparison. Then compare with the model reasoning. Record any correction in the worksheet.

## 4. Changed scenario: inspect the owner list

The IDs and titles are familiar, but the owners change. Inspect the new evidence before you predict results. Do not reuse an answer based only on an ID.

```text
python -B lab.py serve --mode vulnerable --scenario changed --out run/changed-vulnerable-01
```

Read that run's `roster.json`. Build a new table of expected results for both accounts. Capture an unchanged request for each account's own order. Keep its session while changing only the ID to another user's order. Save your predictions, actual responses and reasons. Stop the server, then start:

```text
python -B lab.py serve --mode fixed --scenario changed --out run/changed-fixed-01
```

Select fresh sessions and retest the full table. Check access to each account's own records as well as requests across accounts. Read both status and content. A 401 from an old cookie cannot prove the owner fix worked. Explain how the new evidence affects your predictions and which rule you used.

## 5. Teach it back

In three minutes, explain these points to a beginner:

- What do the proxy, request path, session and stored owner each do?
- Why do you change only one ID in a comparison? Why is selecting Ben in the account picker a separate step?
- Why do hidden links fail to enforce access rules?
- Why do you need both a denied request and a valid request after a fix?
- How do these results differ: 401 from an old session, 404 for an absent record, and 403 for another user's known record?
- What is still untested? Include real authentication, writes, sharing, roles and a live deployment.

Ask the listener to pose a new question. For example: "What if you changed the cookie and ID together?" Save the question and your corrected answer.

## 6. Later recall

After at least a day, close these files. Explain the owner rule from memory. Sketch four checks: own access before, cross-user access before, own access after, and cross-user access after. Add a control with no session. Explain what would make a retest fail to support a clear result. Then compare with your saved evidence and correct your reasons.

You may try changed data later without this guide. A later independent attempt on a less familiar case gives stronger evidence of skill. It still needs a sound explanation. Label practice as guided, prompted, independent or needing review. Time spent, a status code or passing software tests cannot prove competence.
