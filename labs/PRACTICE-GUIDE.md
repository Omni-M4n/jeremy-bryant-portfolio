# Security foundations: practice guide

Updated 25 October 2026. Thirty original exercises using fictional data: twenty-six offline foundations and four hands-on tool workflows.

Website: https://jeremy-bryant.pages.dev/security-labs/
Source and downloads: https://jeremy-bryant.pages.dev/source/
Download: https://jeremy-bryant.pages.dev/downloads/jeremy-bryant-portfolio.zip

## The goal

Understand each task well enough to perform it, explain your decisions, spot a
mistake and handle a changed example. A successful reference check tests the
materials; it does not assess the learner. Independent practice is pending.

You can use command help and your own notes. Understanding the evidence matters
more than memorising flags or typing quickly. These are beginner exercises;
writing the supporting Python utilities is not part of the learner's task.

## One short session

Allow roughly 15 to 25 minutes, or stop after one concept if that suits you.

1. Recall: explain one idea from the last session before opening your notes.
2. Predict: write what you expect a check to show and why.
3. Do: perform one small task and keep the evidence visible.
4. Explain: say what the result means, and what it cannot establish.
5. Record: save the attempt, help used and one thing to revisit.

If a step is unclear, reduce it to one question. Repeat that part with a new
example before adding the next concept. Keep earlier attempts; a correction is
useful evidence of learning, not a reason to erase the first answer.

## Start with these six topics

Before presenting an exercise as completed work, save a short evidence record:
the scoped question, original inputs, commands or actions, result, explanation,
limitations and any help used. For a repair, include a legitimate case that must
still work as well as the case that should now be blocked.

Use these readiness stages for each topic:

- **Prepared:** the materials are available; no learner attempt is implied.
- **Guided:** you completed a case with prompts and can locate the evidence.
- **Independent:** you saved your reasoning before revealing the answer, and a
  reviewer checked both the conclusion and its explanation.
- **Transfer:** you solved an unfamiliar variation, explained an alternative
  interpretation and identified the evidence that would distinguish it.
- **Retained:** after a delay, you repeated the essential reasoning on a new
  case and corrected any mistake without copying the earlier answer.

A reference pass, remembered command or captured flag does not by itself move
an exercise to the next stage. Looking up command syntax is normal; record the
help used and distinguish it from help with the reasoning. A later CTF or
hackathon exercise should use the organiser's authorised scope and end with
an explanation of why the result works and what its limits are.

### 1. DNS investigation: questions and replies

Start in `dns-triage/README.md`. Use the generated packet file in Wireshark.

- Identify a client's question and its matching reply.
- Separate an address answer, a name-not-found reply and no visible reply.
- Match the whole flow, not just a reused transaction number.
- Check retries and calculate time from the first request.

Explain without notes: Why is a name-not-found reply different from silence?
Why could two different requests have the same transaction number?

Changed case: use a new seed, find the late answer, and identify the reused
transaction number without copying the earlier frame numbers.

Save: a small table of findings, packet references, timing and two limitations.
Common trap: calling an absent reply proof that the DNS server is broken.

### 2. Login triage: a pattern needs context

Start in `login-triage/README.md`, then use `PRACTICE.md`.

- Sort events into a timeline and group by account and source address.
- Count failures inside the chosen window.
- Clear a failure-only filter before looking for successful logins.
- Compare the sequence with the fictional account notes.

Explain without notes: What makes a threshold useful? Why does a successful
login after failures still leave questions about who used the account?

Changed case: compare a late success with failures spread over several source
addresses. Explain what the original detector misses and why.

Save: event IDs, times, an observed fact, a possible explanation and a handover.
Common trap: treating an empty detector report as proof that nothing happened.

### 3. Access review: enough access to do the work

Start in `access-review/README.md`. Edit a practice copy of the small policy.

- Read the business requirements before changing permissions.
- Compare each role, resource and read/write/delete action.
- Remove access that is not needed.
- Check that required actions still work after the change.

Explain without notes: How does proving identity differ from deciding access?
Why would a policy that blocks everything fail this exercise?

Changed case: work through the unfamiliar roles and requirements. Do not assume
that write access must include read access, or that everyone needs delete.

Save: before/after policy copies, decisions and reasons tied to requirements.
Common trap: copying the guided answer when the business requirements change.

### 4. HTTP log triage: a response is only part of the story

Start in `http-triage/README.md` and follow its worked example and drills.

- Find the source, time, method, requested path and response status.
- Group related requests and read the surrounding context.
- Separate an ordinary crawler from a pattern that deserves investigation.
- Name the extra evidence needed to understand the application outcome.

Explain without notes: What does a 404 tell you? What does a 200 response fail
to tell you about whether an attempted action succeeded?

Changed case: compare scenarios with different context or incomplete logging.
Decide whether your confidence or next check should change.

Save: request references, a short timeline and a measured escalation decision.
Common trap: calling an unusual URL or a 200 response proof of compromise.

### 5. File integrity: changed does not mean malicious

Start in `file-integrity/README.md`. Work only with the generated dummy files.

- Explain what a baseline records and where it came from.
- Compare the current file set with that baseline.
- Distinguish added, removed, modified and unchanged files.
- Compare the changes with the approval information.

Explain without notes: What does a SHA-256 mismatch establish? Why could an
untrusted baseline make a correct comparison unhelpful?

Changed case: compare approved edits with unexpected changes. Check how your
conclusion changes when the baseline cannot be trusted.

Save: the comparison, approval evidence, unknowns and proposed next action.
Common trap: treating a changed hash as proof of malware, or a matching hash as
proof that a file is safe.

### 6. Firewall review: the first matching rule matters

Start in `firewall-review/README.md`. Use the offline model only.

- Identify source, destination, protocol and ports for a test packet.
- Walk through the rules in order and stop at the first match.
- Explain the default result when no rule matches.
- Test unwanted traffic and legitimate work after an edit.

Explain without notes: Why might a deny rule never take effect? Why does a TCP
rule not automatically allow the same port number over UDP? Why does allowing
one packet not prove that a complete connection will succeed?

Changed case: fix a broad allow, then check missing legitimate traffic and
a protocol difference. Avoid repairing one case by allowing everything.

Save: the matching rule for each test, before/after decisions and your reasons.
Common trap: checking only that suspicious traffic is blocked and overlooking
the connection someone needs for their work.

## Twenty additional topics

Catalog: https://jeremy-bryant.pages.dev/security-labs/foundations/

These extend the first six exercises. They demonstrate the scope of the practice
materials, not completed professional experience. Choose one topic using its
prerequisites. You do not need to finish a whole track before changing topics.

Network investigation and testing:

07. Asset discovery: compare a saved scan with the authorised inventory. Produce
    an evidence table of observed, expected and unobserved services.
08. TCP handshakes: trace SYN, SYN/ACK, ACK and reset evidence. Explain why missing
    packets can prevent a conclusion about the whole connection.
09. TLS review: check decoded certificate facts against hostname and time. Name
    the trust assumptions that these saved fields cannot verify.
10. HTTP headers: review response and cookie settings against a small application
    policy. Explain the limits of a header-only review.
11. Vulnerability prioritisation: order fictional findings using a stated local
    rubric. Explain the reason for each priority and what remains unknown.
12. Vulnerability retesting: compare before-and-after evidence. Separate a
    demonstrated fix from an unchanged issue or an inconclusive retest.
13. Email triage: compare message identities with trusted receiving evidence.
    Explain why a display name or one authentication result is insufficient.

Defensive operations and recovery:

14. Endpoint triage: trace a process relationship and compare it with authorised
    activity. Write a next-check request without declaring malware from a name.
15. Scheduled tasks: review timing, execution identity, paths and approvals.
    Separate an explained maintenance change from one needing investigation.
16. Timelines: convert offsets to UTC and account for clock uncertainty.
    Mark events whose order cannot be established reliably.
17. Alert correlation: distinguish duplicate records from related activity.
    Explain why a group of alerts is not automatically one proven incident.
18. Backup verification: compare scope, age and restore-check evidence with
    recovery requirements. State which recovery claims remain untested.
19. Linux permissions: select the correct owner/group/other permission class.
    Check both file permissions and the required directory traversal rights.
20. SSH configuration: review the supported directives against stated needs.
    Identify configurations outside the small parser's model instead of guessing.

Cloud, identity and configuration:

21. Storage exposure: review sharing in a simplified fictional storage model.
    Explain how its controls interact and what a real platform would still need.
22. Identity lifecycle: decide what changes when someone joins, moves or leaves.
    Account for effective dates and documented exceptions.
23. MFA review: compare account requirements, enrolment and recovery evidence.
    Explain why an enrolment flag alone does not prove complete protection.
24. Cloud audit triage: follow identities and actions across saved events.
    Separate successful actions, failed attempts and missing observations.
25. Secret handling: locate deliberately fake sensitive values in the wrong
    places. Describe an ordered response and the places that still need checking.
26. Dependency review: compare installed versions with fictional advisory ranges.
    Distinguish a version match from proof that an attack can succeed.

Each folder's README defines exact inputs and supported decisions. Its worked
example explains the evidence. DRILLS.md adds an independent case, teach-back
questions and a later recall exercise. Read those limits before using a result.

## A consistent command routine for labs 07–26

Open a terminal in the selected lab folder. Example: `labs/asset-discovery`.
Use `py` in place of `python` if that is how Python is installed on your computer.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

1. Read the README's decision labels, the case context and any readable evidence
   files in the new folder.
2. Predict the findings in `run/attempt-01/notes.txt`.
3. Fill the decision fields in `run/attempt-01/answers.json`. Add an explanation
   and specific evidence references. Keep the worked answer closed.
4. Save the worksheet, then check it:

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
```

The result compares decision fields and checks that written fields are present.
It cannot judge whether an explanation is correct. We must review that reasoning
and ask you to locate the evidence again. A matching result is not mastery.

After saving your attempt, inspect the reference analysis and note corrections:

```console
python lab.py analyse --case run/attempt-01/case.json
```

Use a new folder when repeating. The commands refuse to overwrite old attempts.
For the next two passes, prepare `changed` and then `challenge` scenarios:

```console
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Use the case path for that attempt in every later command. A new output folder
does not create a new scenario; repeating a known case is rehearsal. After all
three, change one permitted input in a practice copy and predict the consequence.
Follow that lab's drills so the change stays within its supported model.

`python lab.py verify` checks the supplied exercise and reference outputs. It
does not check a learner attempt. The first six labs retain their own documented
commands; do not substitute the new routine into them.

## A sensible starting route

Begin with DNS, then asset discovery, TCP evidence and HTTP logs. Continue with
login triage, timelines and endpoint review. Build access-review understanding
before identity lifecycle, MFA and storage exposure. Add configuration and
recovery exercises once their prerequisites make sense to you.

For each lab, create one useful deliverable: a short finding, an access table,
a retest record or a handover. Practise explaining it as if a colleague needs to
act on it. Do not measure progress by the number of folders opened.

## Five practice stages

A. Guided: follow the worked example. Explain each result in your own words.
B. Prompted: close the answer and use only a short checklist.
C. Independent: start fresh and save your answer before viewing the solution.
D. Changed scenario: solve a case whose findings differ, not just its names.
E. Teach-back: explain the evidence, uncertainty, next action and a possible
   innocent explanation to someone else.

Changing only labels is useful rehearsal but is not a new reasoning challenge.
Use the documented scenario variants, changed requirements or new packet
relationships. Record command-help use and other hints honestly.

## Readiness checks

Mark a topic ready for a later recall check only when you can:

- Choose a useful check and explain why it answers the question.
- Find the supporting records, packets, permissions or rules yourself.
- Reach the correct result and state its limits.
- Notice and correct a misleading conclusion.
- Solve an unfamiliar variant without the worked answer.
- Give a short handover someone else could follow.

Revisit the topic on another day, then roughly a week later. Start with a brief
recall question and a changed case. If part is shaky, practise that part and
check again later. This schedule is a practical plan, not a promise of perfect
retention or professional competence.

Passing one tiny lab is evidence for that task, not every real-world incident.
Any portfolio completion note should say exactly what was performed and what
help was used. Do not publish a reference answer as a personal investigation.

## Four hands-on tool sessions

Start after the related foundation topic feels familiar. Use one tool per
session. A short accurate explanation is more useful than a rushed full run.
The lab READMEs provide the commands; this guide tells you what to practise.

### Traffic capture: collect before interpreting

Folder: `traffic-capture`. Read its setup section for loopback capture support.

1. Say which interface and port should carry the test traffic, and why.
2. Start a narrow capture, make the documented harmless local requests, stop
   the capture, and check whether the expected exchanges were actually saved.
3. Explain one successful response, one application error and one failed
   connection. An HTTP error still means an HTTP response arrived.
4. Repeat with a checklist. Then change the documented request and predict
   what the packet evidence should show before you inspect it.
5. Save a small reviewed capture and a table linking your action to frames.

Recall prompts: capture filter versus display filter; loopback versus the
network adapter; missing evidence versus proof of no activity. Teach back why
capturing an unrelated interface can leave you with an empty result.

### Burp: test the server's decision

Folder: `burp-access-control`. Use only the original local training application.

1. Read the scope and name the two fictional identities and their own records.
2. Intercept a legitimate request and explain method, path and identity.
3. Change the object reference in Repeater. Predict the correct server decision.
4. Compare the insecure and repaired modes using both a forbidden request and
   a request the owner still needs. Record complete response evidence.
5. Repeat with changed records, then explain the result without the worked
   answer. The learner is operating the tool, not writing the application.

Recall prompts: authentication versus authorisation; hidden buttons versus
server checks; why a secure retest needs a successful legitimate request too.
Teach back the finding, its local scope and why this toy identity scheme is
not production authentication.

### Snort: test both sides of a rule

Folder: `snort-rule-testing`. Use the local labelled packet files.

1. Explain the protocol, direction, content and identifier in the simple rule.
2. Predict which positive, negative and near-miss fixtures should alert.
3. Run the documented Snort check and offline inspection. Keep actual command
   output separate from the supplied expected answer.
4. Change one documented rule condition, retest every case and explain the
   change in coverage. A missing alert needs investigation, not an automatic
   clean verdict.
5. Record the tool version, inputs, rule, observed alerts and limitations.

Recall prompts: rule match versus compromise; false positive versus missed
traffic; visible payload versus encryption. Teach back one condition where
this rule would fail to see the behaviour you care about.

### Windows events: follow identities through time

Folder: `windows-event-investigation`. Begin with the supplied synthetic XML.
Collect real events only in the disposable Windows lab described in its README.

1. Read one process-creation event and explain timestamp, image, ProcessGuid
   and ParentProcessGuid. Do not confuse a reused process ID with one process.
2. Build the guided chain and distinguish an unrelated near-miss.
3. Work through the missing-parent example. Describe the gap instead of
   inventing the parent activity.
4. In the prepared VM, generate the documented harmless activity, export its
   events and compare your observations with the collection settings.
5. Keep raw exports private. Review the selected evidence for usernames,
   machine names and command lines before preparing a public excerpt.

Recall prompts: an event versus an interpretation; UTC and local time;
collection coverage versus an absence of events. Teach back why Sysmon records
activity but does not independently decide whether it is malicious.

### What counts as a completed hands-on attempt

Record the question, prediction, exact environment, tool version, observed
evidence, interpretation, uncertainty and help used. Repeat with an unfamiliar
variant and explain the result. Revisit on another day and about a week later.
Keep using notes and command help when useful. A test suite checks the utility;
it does not mark you as competent, and supplied example output is not your
personal activity record.

## Handover template

Question: What was I trying to find out?
Observation: What exact records or checks support the finding?
Interpretation: What is the most reasonable explanation, and why?
Uncertainty: What does this evidence not tell me?
Next action: What would I check or change next, within the agreed scope?
Validation: How would I know that the change worked without breaking normal use?

## Keep a private practice record

Copy this block into your own notes for each attempt. Do not commit personal
notes automatically. All topics currently start as not yet assessed.

Date:
Topic and case/seed/scenario:
Stage: guided / prompted / independent / changed / teach-back / later recall
Prediction before running the check:
Evidence references and result:
Help used:
One mistake or uncertainty:
Correction and why it changes the answer:
Next small task:
Later recall date:
Review outcome: repeat / ready for changed case / ready for later recall

## Small glossary

Baseline: a recorded starting point used for comparison.
Context: surrounding information that helps interpret an observation.
Default deny: reject an action or connection unless a rule permits it.
False positive: a detection that looks concerning but does not represent the
specific problem being investigated.
Hash: a calculated fingerprint of bytes; it is not a safety certificate.
Least privilege: give only the access needed for the agreed work.
Protocol: the rules a type of network communication follows.
Source and destination: where the traffic comes from and where it is going.
Threshold: the value at which a chosen rule starts reporting a pattern.
Triage: decide what deserves attention and what to check next.

## Getting started

Open the repository's `labs` folder, choose one lab and read its README. Each
has one `lab.py` entry point: run `python lab.py --help` from that lab's folder.
Python 3.10 or later is required; the utilities use its standard library.
The DNS exercise also supports inspecting its capture with Wireshark.

Keep the supplied fixtures intact. Use the documented practice folder and a
fresh output name for each attempt. No cloud account or live target is needed.

First question, before any command: which proves that a DNS response arrived —
a name-not-found reply, or no visible reply? Explain your answer. Then find
both cases in the capture and point to the evidence.
