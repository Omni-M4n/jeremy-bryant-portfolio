# Choose containment and keep work going

A booking desk loses sign-in while an account is under review. Having a
backup of the booking files will not let staff take bookings on its own. What
should happen next, who owns it, and what evidence would support normal work?



This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise incident-case, access-review and backup-verification first.
You do not need admin rights or an account. You do not need to install tools,
scan a live system or change security settings.

**Words:** Containment limits an ongoing problem. Isolation cuts a host off
from other systems. Authority means the right person has allowed an action.
A dependency is another service needed for work. A fallback is a way to keep
work moving for a short time. Resumption means a service can return to normal use.
Reconciliation means matching each temporary record to the main records once.

## Question and exact rules

The case has incident, service, dependencies, fallback, roles, checks and
evidence. Read each linked note as well as the true/false fields. Each incident,
service, dependency, fallback and check must cite an evidence ID that exists.
Names are made-up role or service labels. Capacity is how much work can be done.
Demand is how much work is needed. Both use whole tasks/hour.

For action-card, use the first rule that fits in this order:

1. Choose **monitor-and-check** if active is false.
2. Choose **emergency-escalation** if active and urgent are both true.
3. Choose **request-authority** if authority is pending.
4. Choose **clarify-scope** if scope is uncertain.
5. Choose **preserve-evidence** if preserved is false in this non-emergency case.
6. Otherwise, choose **account-card** for account scope or **host-card** for host scope.

Urgent requires active=true. These rules teach a sequence. Do not let them delay
urgent steps to prevent harm.

For continuity, use **keep-service-under-review** when the service is available.
If the service is down, check the fallback. Use **prepare-fallback** if it is not
ready. If it is ready, use **escalate-capacity** when its capacity is below demand.
Use **use-manual-fallback** when it meets demand.
Uncovered demand is demand minus ready capacity, with a minimum of zero. If the
fallback is not ready, all demand is uncovered. This hourly sum does not predict
how a queue will grow.

Use **resume-with-owner-release** only when all these gates pass. The service must
be available and bytes_restored must be true. All dependencies must be available.
There must be no active issue. All four checks must pass: security, workflow,
queue and owner_release. Otherwise, use **hold-service-resumption**.
Restored bytes are just one gate. The model trusts the supplied status fields.
In your written review, check whether the notes support those fields.

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

Read these written action cards. Choose a next card and explain its cost.
Do not execute the actions on your computer or any account.

| Card | Intended effect | Cost and ownership | Evidence and way back |
| --- | --- | --- | --- |
| account-card | Restrict the named account and review its sessions | The identity operator acts under the response lead; the user may lose access to several services | Save approved scope and session evidence; owner tests revised access before release |
| host-card | Isolate the named workstation | The endpoint operator acts under the response lead; local apps and remote support may stop | Preserve scoped evidence where safe; test clean access and dependent work before reconnecting |
| preserve-evidence | Save the approved, narrow case records | The response lead sets urgency and privacy scope | Record times, IDs and custody; never delay an urgent safety response |
| request-authority / clarify-scope | Obtain the missing decision or scope | The response lead owns the escalation | State evidence, impact, time limit and the exact proposed action |
| emergency-escalation | Use the authorised emergency path | The response lead follows the emergency plan | Record the reason, actions and evidence as soon as safe |
| monitor-and-check | Review follow-up evidence | The response lead owns the review | Use named checks and a return-to-escalation trigger |

Draw arrows to show that booking-desk needs identity and booking-store. Name each
owner. Write a note for one hour of work. State which work is blocked. List the
fallback capacity, demand and uncovered work. Explain how to track the paper
queue and who must act if it cannot cope. Then list the four test records needed
before normal work resumes. A file hash does not test the booking workflow.
The helper checks this written exercise only. It runs no restriction or restore.

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

This is a written non-emergency exercise. It does not restrict an account, isolate a host, restore a backup or change a service.

The emergency card means use an approved emergency path. Do not delay urgent action to collect evidence.

Restored bytes alone do not prove that the service is ready. Check its dependencies, safe access, normal work and queued tasks too.

The small gate model checks supplied claims and links to evidence. People must check that evidence and approve any real action.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [NIST SP 800-61 Rev. 3: incident response](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [NIST SP 800-34 Rev. 1: contingency planning](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
