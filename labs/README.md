# Security foundations: original guided labs

Three small offline exercises prepared for Jeremy Bryant's learning portfolio.
The datasets and scenarios are fictional. They are separate practice materials,
not published university submissions or examples from a live incident.

| Lab | Question | Skill |
| --- | --- | --- |
| [DNS triage](dns-triage/README.md) | What happened to each name lookup? | Packet evidence and careful network diagnosis |
| [Login triage](login-triage/README.md) | Which events deserve further investigation? | Timelines, thresholds, context and escalation |
| [Access review](access-review/README.md) | Who needs which actions on which resources? | Least privilege and preserving necessary access |

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

Read each lab's limitations before interpreting its output. Publish only new,
checked practice evidence that accurately states who performed the work.
