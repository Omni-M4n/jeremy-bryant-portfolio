# Build a small incident case notebook

A computer signs in, starts a program, looks up a name, and requests a web
address. That could be a planned update. Can you link the records while keeping
an innocent explanation and an unresolved concern in view?

This extends **login-triage**, **endpoint-triage**, **http-triage**, **alert-correlation** and **timeline-analysis**. It brings the records into one notebook. You then hand over a finding with clear limits.

This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise soc-query-workbook and logging-health first.
You do not need admin rights or an account. You do not need to install tools,
scan a live system or change security settings.

**Words:** An incident case records the facts you are checking and what they mean.
A hypothesis is a possible cause or explanation you can check. A change record says what work was approved.
Scope means the people, systems, times and actions covered. DNS looks up a name.
HTTP records a web request. A handover lets another person continue your work.

## Question and exact rules

data.change has id, host, account, start, end, process, destination and approved.
Its time window includes start but leaves out end. data.events has 1-30 unique
records with id,time,kind,host,account,value. Kinds are login, process, dns and http.
The login value must be success. A process value is a simple program label.
The dns/http values are made-up destination names. These records are summaries.

For working-hypothesis, use the first rule that fits in this order:

1. Use **review-outside-change** if any event differs from the change record's scope fields.
2. Otherwise, use **request-owner-check** if approved is false.
3. Otherwise, use **request-missing-source** if a kind is absent.
4. Otherwise, use **consistent-with-change**.

For a login, compare host, account and time. For a process, compare its program
label too. For DNS/HTTP, also compare destination. Check scope even when approval
is false. A scope match does not mean the work was approved.
Answer coverage with **four-kinds-present** or **kinds-missing**. For timeline,
write IDs in time order, with commas and no spaces. Sort tied times by ID.
That tie-break only sets the display order. It does not prove which event came first.

The case JSON is the input record. Its artifacts are readable copies of raw
evidence when prepared. Change only a run copy. For a repeated model check,
edit the evidence inside case.json; editing an extracted artifact alone does
not change case.json. Each program rejects unsupported structure. Record-level
rejections are named below where that is part of the lesson.

## Practice commands

Open a terminal in this lab folder. Replace `python` with `py -3` if needed.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. Save a prediction in notes.txt before seeing an answer.
Fill the decisions in answers.json with the exact vocabulary above. Add an
explanation and evidence IDs. Keep the first attempt; write corrections below it.

Build a notebook with four parts. Make a timeline with record IDs. Write two
hypotheses. List the evidence you need, then write a handover. For each hypothesis,
list facts that support it and facts that go against it. Start with "planned
update" and "activity outside approved work" as two possible explanations.
Record how missing logs weaken each claim. No real response action is taken.
The local model only checks the stated rules.

After your prediction and practical work, compare the model:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

Use the matching attempt path for the later cases. Prepare refuses to replace
an existing folder. Its output must be below run/. Other explicit paths are
relative to the terminal directory. Exit 0 means success or an answer match;
1 means a mismatch or missing writing; 2 means invalid input or a file error.
A match checks labels and the presence of writing. A person must review whether
the explanation is sound. Tests and verify check the package, not learner skill.

## Save evidence and hand over

Keep case.json, answers.json and notes.txt. Record the commands, outputs, first
prediction, observed facts, interpretation, unknowns, next check, and help used.
Give each fact a record ID. End with a short handover: question, scoped finding,
two evidence references, a competing explanation, and the next evidence needed.
Mark your stage as attempted, checked with help, or attempted again unaided.
Do not call a script match mastery.

Cleanup is optional. After saving your work elsewhere, remove only the chosen
run/attempt folder using your file manager. Check its full path first. No system
setting needs rollback. Keep supplied fixtures and first attempts.

## Limits

A matching change record may explain the events as planned work. It does not prove who acted or whether the code was safe.

The four event kinds are brief summaries. A DNS lookup and HTTP destination do not prove what content was sent or received.

Exact time order assumes the UTC clocks are right. A missing kind may mean its logs were not collected. It need not mean no such event took place.

No real incident, endpoint, account, DNS server or website was contacted. A person must review the case and choose the response.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [NIST SP 800-61 Rev. 3: incident response](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [NIST SP 800-86: forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [NIST SP 800-92: log management](https://csrc.nist.gov/pubs/sp/800/92/final)
