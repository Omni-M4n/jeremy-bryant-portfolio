# My cybersecurity and cloud learning goal

**Current status: planned.** I have selected this 32-lab route; I am not claiming that I have completed it, mastered its topics or used these methods in a professional role.

I will use three stages to describe exercise complexity, not my ability. Beginner uses smaller bounded decisions, Intermediate connects controls and evidence, and Advanced combines several evidence types and audiences. Every lab starts as **planned**.

## My status model and review gate

- **Planned:** I have selected the lab and its prerequisites but have not claimed an attempt.
- **Guided:** I have used instructions, examples or prompts and recorded that help.
- **Solo:** I have preserved a first answer to a changed case before checking a reference.
- **Reviewed:** A person has challenged my evidence and reasoning, and I have retained feedback and corrections.
- **Recall:** I have tried different facts later without reusing my earlier answer.

Before I start a dependent lab, I will keep reviewed or equivalent evidence for its named dependencies. For every lab I will retain the case, first answer, commands or method, exact evidence references, conclusion, uncertainty, help used, correction and next check. If review is unavailable, I will mark the work awaiting review rather than call it independently demonstrated.

## Planned route and evidence

### Beginner — make bounded decisions

| # | Lab | Evidence I plan to retain | Earlier dependency |
| ---: | --- | --- | --- |
| 1 | [Rules of engagement](/lab-files/rules-of-engagement/) | Scope sheet with owner, targets, actions, exclusions, time window, stops and pending approval. | None |
| 2 | [DNS triage](/lab-files/dns-triage/) | I will retain a synthetic packet worksheet that cites exact frames and matches each DNS question to any visible reply by endpoints, ports, DNS ID, name and type. I will distinguish an A answer, NXDOMAIN and no visible reply. I will use only the supplied synthetic evidence, not a live capture, and will not treat the exercise as proof of packet loss, application success, answer truth, professional use, completion or mastery. | None |
| 3 | [Access review](/lab-files/access-review/) | Role/resource/action matrix and least-privilege policy decision. | None |
| 4 | [Login triage](/lab-files/login-triage/) | Sorted sign-in timeline and bounded handover. | None |
| 5 | [Timeline analysis](/lab-files/timeline-analysis/) | UTC timeline with exact event references and uncertainty. | Login triage |
| 6 | [Network address path](/lab-files/network-address-path/) | Labelled packet-path diagram and route-choice worksheet. | None |
| 7 | [TCP handshake investigation](/lab-files/tcp-handshake/) | I will retain a TCP flow table with exact frame references and sequence/acknowledgement calculations. I will use the supplied synthetic packet summaries to distinguish an observed handshake, reset, no visible response, missing final ACK, missing initial SYN and acknowledgement mismatch. I will state that the excerpt cannot establish full connection state or root cause, that missing packets do not prove packet loss, firewall failure or server fault, that an observed handshake does not prove application success, and that matching helper results do not prove professional use, completion or mastery. | DNS triage |
| 8 | [Asset discovery and inventory](/lab-files/asset-discovery/) | I will retain a saved-scan-to-inventory table with exact IP address, TCP port and XML references. I will compare the supplied synthetic scan snapshot with the approved inventory; distinguish hosts not present, recorded down or unregistered and expected, missing or unexpected open TCP services; and state that the offline helper does not run a scan. I will not treat one saved snapshot or a matching result as proof of ownership, vulnerability, malicious activity, current state, complete coverage, professional use, completion or mastery. | DNS triage |
| 9 | [Vulnerability prioritisation](/lab-files/vulnerability-prioritisation/) | I will retain a fictional finding-priority queue with exact record and field references, impact, exposure, evidence-of-use, service-importance and confidence inputs, each four-part score, any overriding rule, uncertainty and the next owner check. I will apply only the supplied local rubric to supplied fictional findings: unverified evidence becomes investigate; supplied fictional observed-exploitation records become urgent; otherwise I will assign urgent, planned or routine by score. I will state that the rubric is not CVSS, queue labels do not set deadlines, proof of concept does not prove exploitation, and helper matches do not prove a real vulnerability, real exploitation or current risk, professional use, completion or mastery. | Asset discovery and inventory; access review |
| 10 | [Firewall review](/lab-files/firewall-review/) | First-match trace with required and excess traffic decisions. | None |
| 11 | [HTTP triage](/lab-files/http-triage/) | Triage report separating observations, explanations and next check. | None |
| 12 | [File integrity](/lab-files/file-integrity/) | Baseline comparison classifying exact changes and baseline limits. | None |
| 13 | [Backup verification](/lab-files/backup-verification/) | Copy-selection worksheet using retention, scope, hashes and RPO. | None |
| 14 | [Cloud storage review](/lab-files/cloud-storage-review/) | Exposure-path worksheet with record IDs and unanswered check. | None |
| 15 | [Identity lifecycle](/lab-files/identity-lifecycle/) | Joiner/mover/leaver worksheet explaining keep, remove or review decisions. | None |

### Intermediate — connect controls and evidence

| # | Lab | Evidence I plan to retain | Earlier dependency |
| ---: | --- | --- | --- |
| 16 | [MFA and account recovery review](/lab-files/mfa-review/) | I will retain a synthetic account-control worksheet comparing supplied MFA and recovery records by account type, with exact evidence references and limits stating that I did not test a real sign-in or control effectiveness. | Identity lifecycle |
| 17 | [Cloud audit triage](/lab-files/cloud-audit-triage/) | Audit timeline separating actions, denials, gaps and attribution limits. | None |
| 18 | [Shared responsibility](/lab-files/shared-responsibility/) | Service/task table with owner, agreement, control evidence and gap. | Cloud storage review; backup verification |
| 19 | [IAM explicit deny](/lab-files/iam-explicit-deny/) | Request/statement table and one changed-policy comparison. | Access review; identity lifecycle |
| 20 | [Temporary credentials](/lab-files/temporary-credentials/) | Human-to-role-to-session issue, expiry and revocation timeline. | Access review; identity lifecycle; cloud audit triage |
| 21 | [Cloud network path](/lab-files/cloud-network-path/) | Two-leg path diagram and reachability table. | Firewall review; network address path |
| 22 | [Log ingestion](/lab-files/log-ingestion/) | Import report, rejected rows and source reconciliation. | Login triage; timeline analysis |
| 23 | [Logging health](/lab-files/logging-health/) | Coverage timeline with arrivals, heartbeats, gaps and next check. | Log ingestion; timeline analysis |
| 24 | [Restore drill](/lab-files/restore-drill/) | Dummy-data restore receipt with hashes, version and measured durations. | Backup verification; file integrity |
| 25 | [Evidence custody](/lab-files/evidence-custody/) | Dummy-file evidence register and copy receipt linking each copy to its recorded source, UTC handling records, hash checks and stated limits. | File integrity |
| 26 | [Secret handling](/lab-files/secret-handling/) | I will retain a DEMO-only secret exposure worksheet and evidence note tracing exact listed markers through configuration, saved changes and logs, separating observed exposure from proposed response and stating what the supplied files cannot prove. | File integrity |

### Advanced — build and communicate a case

| # | Lab | Evidence I plan to retain | Earlier dependency |
| ---: | --- | --- | --- |
| 27 | [Endpoint triage](/lab-files/endpoint-triage/) | Process tree and handover that does not assert malware. | None |
| 28 | [Alert correlation](/lab-files/alert-correlation/) | Deduplicated alerts, stated correlation rule and bounded grouping. | None |
| 29 | [SOC query workbook](/lab-files/soc-query-workbook/) | Saved SQL, result tables, distinct counts and join explanation. | Log ingestion; login triage; alert correlation |
| 30 | [Incident case](/lab-files/incident-case/) | Notebook with timeline, two hypotheses, evidence needs and handover. | SOC query workbook; logging health; login triage; endpoint triage; HTTP triage; alert correlation; timeline analysis |
| 31 | [Containment tabletop](/lab-files/containment-tabletop/) | Decision table with authority, effect, evidence, owner and release check. | Incident case; access review; backup verification |
| 32 | [Incident communications](/lab-files/incident-communications/) | Staff message, technical handover and manager update. | Login triage; timeline analysis |

## Scope and limits

I will use fictional or dummy evidence within each lab's written safety boundary. This route authorises no work on real systems, accounts or data. A helper match can check a format or expected decision, but it cannot judge my reasoning, establish mastery, confer a credential or prove professional experience.

On 19 November 2026, I verified that this prepared route was live at [`/goal/`](https://jeremy-bryant.pages.dev/goal/) and that its [manifest](https://jeremy-bryant.pages.dev/goal/manifest.json) was available for commit `e01b084c2650eda197fb66d5069f1d02572a2875`. This confirms site availability at that check only; I am keeping every lab **Planned**, and I am not claiming completion or mastery. I will use the [full lab library](https://jeremy-bryant.pages.dev/security-labs/library/), [study plan](https://jeremy-bryant.pages.dev/security-labs/study-plan/) and [source page](https://jeremy-bryant.pages.dev/source/) for the underlying materials and method.
