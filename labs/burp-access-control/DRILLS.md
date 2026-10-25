# Practice sequence

Use only this lab's printed loopback URL. Every attempt gets a new `run/` child.
Keep the worksheet and request/response evidence; no script records mastery.
No programming is required at any stage.

## 1. Guided: follow and explain

Follow the README with `guided` mode data. Pause before changing an ID and say
what will remain the same, what will change, and why the expected owner matters.
Complete the vulnerable and fixed comparisons. Then read the worked example
and annotate differences between your expectation and your actual evidence.

Acceptance: one intercepted baseline, manual Repeater comparisons for both
accounts, fixed-mode denial, preserved own access, and a bounded explanation.
An automated test result does not satisfy this acceptance check.

## 2. Prompted: use a small checklist

Close the worked example and start fresh runs, for example:

```text
python -B lab.py serve --mode vulnerable --scenario guided --out run/prompted-vulnerable-01
```

After your comparisons, stop it and start:

```text
python -B lab.py serve --mode fixed --scenario guided --out run/prompted-fixed-01
```

Use only these prompts: exact scope; selected identity; unchanged baseline;
one changed object ID; status plus content; fresh sessions after restart;
other-user denial; own-user access; one limitation. If you need the full guide,
mark where and continue. Needing a reminder is useful evidence for the next
practice session.

## 3. Independent: write the plan first

Using new names such as `run/independent-vulnerable-01` and
`run/independent-fixed-01`, reproduce the finding and retest without the worked
example. Before sending anything, write your smallest useful request matrix.
Include both accounts, each existing order, one unknown ID, one invalid ID and
one missing-session request. Predict statuses and response contents separately.

Produce a short handover from your evidence. Ask another person to check whether
the account actually stayed unchanged within each ID comparison. Only then
compare with the reference reasoning. Record any correction in the worksheet.

## 4. Changed scenario: ownership is reassigned

The IDs and titles remain familiar, but the owner assignments change. Ben now
owns 101 and 103; Ada owns 102. A memorised rule such as “102 must be denied”
will fail. The correct decision depends on both the selected account and the
current object's owner. ID 999 is still absent.

```text
python -B lab.py serve --mode vulnerable --scenario changed --out run/changed-vulnerable-01
```

Inspect that run's `roster.json`; build a new expected matrix. Intercept an
unchanged request for Ben's 103, keep his session, and compare his access to
102. Then repeat with Ada requesting her own 102 and Ben's 101. Stop the server:

```text
python -B lab.py serve --mode fixed --scenario changed --out run/changed-fixed-01
```

Select fresh sessions and retest the whole matrix. In fixed mode, Ben's 101 and
103 must remain available while his request for 102 is denied; Ada must retain
102 while 101 and 103 are denied. Do not relabel a 401 from an old cookie as a
successful access-control fix. Explain why the scenario changed your expected
answers without changing the underlying rule.

## 5. Teach it back

In three minutes, explain to a beginner:

- What the proxy, request path, session and stored owner each contribute.
- Why editing only an ID is a controlled comparison, and why selecting Ben in
  the account picker is a separate deliberate operation.
- Why hidden links do not enforce authorization.
- Why a denial and a successful legitimate request are both needed after a fix.
- Why 401 from a stale session, 404 for an absent object, and 403 for a known
  other user's object support different conclusions.
- What remains untested: real authentication, writes, sharing, roles and a
  production deployment.

Have the listener ask one unexpected question, for example: “What if you changed
the cookie and the ID together?” Save the question and your corrected answer.

## 6. Later recall

After at least a day, close these files and explain the owner rule from memory.
Sketch four checks: own access before, cross-user access before, own access
after, cross-user access after. Add a missing-session control. Explain what
would make a claimed successful retest inconclusive. Then compare with your
saved evidence and correct your explanation.

Optional next session: use changed data without this guide. A later independent
attempt, its unfamiliar case and an accurate explanation are stronger evidence
than repeating the same sequence immediately. Record practice honestly as
guided, prompted, independent or needing review; do not infer competence from
elapsed time, a status code or passing software tests.
