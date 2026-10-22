# Security foundations: practice guide

Prepared 23 October 2026. Six original exercises using fictional data.

Website: https://deadgoodreviews.com/portfolio/security-labs/
Source: https://github.com/Omni-M4n/jeremy-bryant-portfolio/tree/main/labs

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

## The six topics

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
