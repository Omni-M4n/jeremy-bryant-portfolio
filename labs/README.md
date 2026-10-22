# Security foundations: original guided labs

Six small offline exercises prepared for Jeremy Bryant's learning portfolio.
The datasets and scenarios are fictional. They are separate practice materials,
not published university submissions or examples from a live incident.

| Lab | Question | Skill |
| --- | --- | --- |
| [DNS triage](dns-triage/README.md) | What happened to each name lookup? | Packet evidence and careful network diagnosis |
| [Login triage](login-triage/README.md) | Which events deserve further investigation? | Timelines, thresholds, context and escalation |
| [Access review](access-review/README.md) | Who needs which actions on which resources? | Least privilege and preserving necessary access |
| [HTTP log triage](http-triage/README.md) | What do web requests and responses actually show? | Web-log evidence, context and cautious escalation |
| [File integrity](file-integrity/README.md) | What changed, and was the change expected? | Hashes, baselines and change review |
| [Firewall review](firewall-review/README.md) | Which rule decides this packet? | Rule order, network boundaries and necessary traffic |

Follow the [practice guide](PRACTICE-GUIDE.md) for short sessions, recall questions,
changed scenarios and a blank progress record. Start with one topic; there is no
need to complete all six in one sitting.

## Status and contribution

These are guided learning materials. Their automated reference checks validate
the exercise fixtures and utilities. Jeremy's independent completion and
explanation of unfamiliar variants have not yet been assessed. The materials do
not claim professional security experience or independent authorship of every
utility. Future personal evidence should describe what was actually performed.

## Start with one lab

Each folder has its own README and a single `lab.py` entry point. Start with that
README, run `python lab.py --help`, and work inside that lab's folder. Python 3.10+
is required; only the standard library is used. The DNS packet file can also be
opened in Wireshark. The exercises can run on Windows or in an existing Linux VM.
They do not require a cloud account, a live target or a public service.

Keep generated practice runs separate from reference fixtures. Use the documented
seed option for a new variant. Check whether a command expects an empty output
folder before rerunning it; preserve your notes when changing exercises.

## Learning sequence

1. **Walk through:** read each observation and explain it in your own words.
2. **Use prompts:** repeat with a short checklist, keeping the full answer closed.
3. **Work independently:** reset to fresh inputs, make a finding and then check it.
4. **Change the inputs:** use a different seed or scenario, not memorised answers.
5. **Teach it back:** explain the evidence, limits, next action and a false positive.

No pass or mastery is recorded automatically from running a script. A successful
independent attempt includes the explanation and an unfamiliar variant. Taking
notes is normal; the goal is understanding, not speed or memorising every flag.

## Originality and evidence

- Scenarios, fixtures and utilities were created as standalone exercises in
  October 2026. No assessment questions, answer sheets, course recordings or
  student identifiers are included.
- Each lab records synthetic provenance and reference-file hashes. Hashes verify
  file identity and reproducibility; they do not prove global novelty or learner
  competence.
- Familiar security principles and public protocol documentation are shared
  knowledge. The project distinction comes from the new questions, data,
  implementations and analyses, not simply renamed coursework.
- The access model is intentionally smaller than real cloud IAM. The login
  detector is a teaching heuristic. Packet fixtures describe generated events,
  not a real network capture.
- Web logs do not establish an application's internal outcome. File hashes show
  byte differences, not malicious intent. The firewall simulator is a small
  ordered-rule model, not a configuration for a real host or cloud platform.

Read each lab's limitations before interpreting its output. Publish only new,
checked practice evidence that accurately states who performed the work.
