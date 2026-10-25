# Security foundations: original guided labs

<!-- LAB_COUNTS_START -->
This release has **36 core labs** and **0 extensions**.
<!-- LAB_COUNTS_END -->

These are guided exercises prepared for Jeremy Bryant's learning portfolio.
The original set has 26 offline foundations and four hands-on tool workflows.
The datasets and scenarios are fictional. They are separate practice materials,
not published university submissions or examples from a live incident.

## The first six

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
need to complete a whole track in one sitting.

## Twenty additional foundation labs

Every new lab has guided, changed and challenge cases. Start with its README;
the catalog describes practice scope, not completed professional experience.

### Network investigation and testing

| Lab | Purpose |
| --- | --- |
| [Asset discovery and inventory](asset-discovery/README.md) | Compare a saved scan with the authorised asset inventory. |
| [TCP handshake investigation](tcp-handshake/README.md) | Distinguish a completed handshake, a reset and incomplete evidence. |
| [TLS certificate review](tls-review/README.md) | Check certificate evidence against the intended hostname and observation time. |
| [HTTP headers and cookies](http-header-review/README.md) | Review web response settings against the needs of a fictional application. |
| [Vulnerability prioritisation](vulnerability-prioritisation/README.md) | Explain which fictional findings need attention first using an explicit local rubric. |
| [Remediation and retesting](vulnerability-retest/README.md) | Decide whether a claimed fix is demonstrated, incomplete or cannot yet be tested. |
| [Email identity and message triage](email-triage/README.md) | Compare message identities and destinations with trusted receiving evidence. |

### Defensive operations and recovery

| Lab | Purpose |
| --- | --- |
| [Endpoint process investigation](endpoint-triage/README.md) | Use process relationships and approved activity to decide what deserves review. |
| [Scheduled task review](scheduled-task-review/README.md) | Compare recurring task settings and changes with authorised maintenance. |
| [Evidence timeline reconstruction](timeline-analysis/README.md) | Normalise event times and show where clock uncertainty limits ordering. |
| [Alert correlation and duplicate handling](alert-correlation/README.md) | Group related records without confusing duplicate alerts with separate incidents. |
| [Backup and recovery verification](backup-verification/README.md) | Check backup scope, freshness and restore evidence against stated recovery needs. |
| [Linux file permission review](linux-permissions/README.md) | Work out access from owner, group and other permission bits. |
| [SSH configuration review](ssh-config-review/README.md) | Evaluate a small supported configuration against stated administration requirements. |

### Cloud, identity and configuration

| Lab | Purpose |
| --- | --- |
| [Cloud storage exposure review](cloud-storage-review/README.md) | Reason about public exposure in a deliberately small fictional storage model. |
| [Joiner, mover and leaver access](identity-lifecycle/README.md) | Update access decisions when a person starts, changes duties or leaves. |
| [MFA and account recovery review](mfa-review/README.md) | Check enrolment and recovery evidence against explicit account requirements. |
| [Cloud audit-event investigation](cloud-audit-triage/README.md) | Reconstruct identity and configuration activity from saved audit events. |
| [Secret handling and exposure review](secret-handling/README.md) | Find fictional sensitive values in the wrong places and plan an appropriate response. |
| [Dependency inventory and advisory review](dependency-review/README.md) | Match a small inventory to fictional version-range advisories without assuming exploitability. |

## Four hands-on tool labs

| Lab | Practical question | Separate tool |
| --- | --- | --- |
| [Traffic capture](traffic-capture/README.md) | Can I collect and explain the traffic from my own controlled requests? | Wireshark |
| [Web access control](burp-access-control/README.md) | Does the server check who may read each fictional record, before and after a fix? | Burp Suite Community |
| [Offline detection rule](snort-rule-testing/README.md) | Does one simple rule detect the chosen marker and reject near-misses? | Snort 3 |
| [Windows event investigation](windows-event-investigation/README.md) | Can I trace a harmless process chain from collected events without confusing reused process IDs? | Sysmon in a disposable Windows VM |

These four use their own documented command interfaces. They include software
checks and fictional training inputs, but full practice requires operating the
named tools. A synthetic PCAP or XML sample is not a personal capture. An
application integration test is not evidence of a manual Burp session. Read each
README before setup; no installation or host monitoring is performed by the
website build. Independent hands-on completion remains unassessed.

## Further core labs and extensions

The list below contains only checked packages included in this release. Extensions
build on a named core lab. Use each README to check the setup and skills it needs.

<!-- ADDITIONS_START -->
### Network and DNS

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Map addresses, subnets and a packet's route](network-address-path/README.md) | Distinguish local-subnet delivery, gateway routing and name resolution; predict the next hop. |
| Core | [Read ARP and DHCP exchanges](arp-dhcp-evidence/README.md) | Explain address resolution and lease negotiation, and separate normal renewal from a missing step. |

### Windows, Linux and endpoint

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Build and verify a disposable lab workbench](isolated-lab-workbench/README.md) | Explain host/guest boundaries and prove that a harmless change can be rolled back. |
| Core | [Use shell commands for read-only troubleshooting](shell-troubleshooting/README.md) | Choose a relevant command, interpret its fields and explain why its output cannot establish malicious intent. |

### Identity and cloud

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Map cloud shared responsibility and controls](shared-responsibility/README.md) | Allocate security and recovery tasks to the customer/provider and name what the service description does not settle. |
| Core | [Compare encryption, encoding, hashing and key recovery](encryption-key-recovery/README.md) | Choose the appropriate concept for integrity or confidentiality and demonstrate why missing a required key changes recoverability. |
<!-- ADDITIONS_END -->

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
The offline exercises do not require a cloud account, live target or public
service. The hands-on exercises use owned loopback applications, offline packets
or a disposable lab VM, with separate tool prerequisites documented in each lab.

The twenty additional labs use consistent `cases`, `prepare`, `show`, `analyse`,
`check` and `verify` commands. See the [maintained contract](FOUNDATION-CONTRACT.md)
and each README. The first six retain their original command interfaces.

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
