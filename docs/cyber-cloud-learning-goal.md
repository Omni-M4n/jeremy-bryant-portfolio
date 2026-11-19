# My cybersecurity and cloud learning goal

**Current status: planned.** I have selected this 36-lab route; I am not claiming that I have completed it, mastered its topics or used these methods in a professional role.

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
| 10 | [Dependency review](/lab-files/dependency-review/) | I will retain a fictional component/advisory worksheet citing component IDs, package names, versions, scope, path evidence, advisory IDs, affected-range comparisons, uncertainty and the next check. I will compare each supplied stable three-part version numerically with every supplied exact-package `[introduced,fixed)` range; distinguish no supplied advisory from outside supplied ranges; and separate build exposure from reachable, not-demonstrated and unknown runtime paths. I will state that this offline exercise trusts the supplied inventory and path evidence and does not install packages, fetch live notices, resolve a full dependency chain, model ecosystem-specific version rules or test an exploit. Version, range and helper results do not prove exploitability, safety, professional use, completion or mastery. | Vulnerability prioritisation |
| 11 | [Firewall review](/lab-files/firewall-review/) | First-match trace with required and excess traffic decisions. | None |
| 12 | [HTTP triage](/lab-files/http-triage/) | Triage report separating observations, explanations and next check. | None |
| 13 | [File integrity](/lab-files/file-integrity/) | Baseline comparison classifying exact changes and baseline limits. | None |
| 14 | [Backup verification](/lab-files/backup-verification/) | Copy-selection worksheet using retention, scope, hashes and RPO. | None |
| 15 | [Cloud storage review](/lab-files/cloud-storage-review/) | Exposure-path worksheet with record IDs and unanswered check. | None |
| 16 | [Identity lifecycle](/lab-files/identity-lifecycle/) | Joiner/mover/leaver worksheet explaining keep, remove or review decisions. | None |

### Intermediate — connect controls and evidence

| # | Lab | Evidence I plan to retain | Earlier dependency |
| ---: | --- | --- | --- |
| 17 | [MFA and account recovery review](/lab-files/mfa-review/) | I will retain a synthetic account-control worksheet comparing supplied MFA and recovery records by account type, with exact evidence references and limits stating that I did not test a real sign-in or control effectiveness. | Identity lifecycle |
| 18 | [Cloud audit triage](/lab-files/cloud-audit-triage/) | Audit timeline separating actions, denials, gaps and attribution limits. | None |
| 19 | [Shared responsibility](/lab-files/shared-responsibility/) | Service/task table with owner, agreement, control evidence and gap. | Cloud storage review; backup verification |
| 20 | [Cloud resource lifecycle](/lab-files/cloud-resource-lifecycle/) | I will retain a synthetic cloud-resource lifecycle worksheet citing exact resource IDs, owners, expiry and review flags, dependency arrows, retention holds, proposed teardown order, made-up residual daily cost units, budget-alert state, the approver needed for each proposed step and a later bill check. I will use only supplied offline records; identify missing ownership or expiry data; block proposed removal when a retention hold or remaining dependency applies; and distinguish review or expiry from deletion approval, a budget alert from a spending cap, and a model-valid order or zero model cost from real deletion or stopped charges. I will run no cloud deletion commands and will not treat the exercise as proof of complete inventory, real removal, stopped spending, professional use, completion or mastery. | Asset discovery and inventory; shared responsibility |
| 21 | [IAM explicit deny](/lab-files/iam-explicit-deny/) | Request/statement table and one changed-policy comparison. | Access review; identity lifecycle |
| 22 | [Temporary credentials](/lab-files/temporary-credentials/) | Human-to-role-to-session issue, expiry and revocation timeline. | Access review; identity lifecycle; cloud audit triage |
| 23 | [Cloud network path](/lab-files/cloud-network-path/) | Two-leg path diagram and reachability table. | Firewall review; network address path |
| 24 | [Log ingestion](/lab-files/log-ingestion/) | Import report, rejected rows and source reconciliation. | Login triage; timeline analysis |
| 25 | [Logging health](/lab-files/logging-health/) | Coverage timeline with arrivals, heartbeats, gaps and next check. | Log ingestion; timeline analysis |
| 26 | [Restore drill](/lab-files/restore-drill/) | Dummy-data restore receipt with hashes, version and measured durations. | Backup verification; file integrity |
| 27 | [Evidence custody](/lab-files/evidence-custody/) | Dummy-file evidence register and copy receipt linking each copy to its recorded source, UTC handling records, hash checks and stated limits. | File integrity |
| 28 | [Secret handling](/lab-files/secret-handling/) | I will retain a DEMO-only secret exposure worksheet and evidence note tracing exact listed markers through configuration, saved changes and logs, separating observed exposure from proposed response and stating what the supplied files cannot prove. | File integrity |
| 29 | [Data classification](/lab-files/data-classification/) | I will retain a fictional data-handling register citing exact record and field references, owner and purpose, fields to keep or leave out, handling label, storage and reader rules, retention and hold state, sharing decision, one proposed exception, and the stated scope of each disposal receipt. I will apply only supplied synthetic records and invented local rules; treat a hold as overriding age; distinguish disposal due from authorised and verified deletion, and listed-copy coverage from erasure; mark absent authority, date, method and checks as not supplied; and label exceptions proposed, not approved. I will state that the helper trusts the structured disposal field rather than verifying receipt prose. I will perform no deletion, sharing or live test and will not treat results as legal advice or proof of real deletion, control effectiveness, professional use, completion or mastery. | Access review; secret handling |

### Advanced — build and communicate a case

| # | Lab | Evidence I plan to retain | Earlier dependency |
| ---: | --- | --- | --- |
| 30 | [Risk register](/lab-files/risk-register/) | I will retain a fictional GRC decision pack containing written scope, a risk register with exact evidence IDs, a control-evidence matrix, a pending exception record, a challenge log and a sanitized decision report. I will apply only the lab’s local 1–3 teaching rubric to the supplied fictional case; separate events and plausible harms from confirmed facts; distinguish proposed controls and projected residual risk from checked operation; keep acceptance pending when authority, threshold, obligation or approval is not supplied; and record the owner, review date, uncertainty and bounded next check. I will perform no live action and will not treat helper matches, a worked reference or framework mapping as proof of a real incident, control effectiveness, legal compliance, professional use, completion, mastery or independent assessment. | Vulnerability prioritisation; data classification |
| 31 | [Endpoint triage](/lab-files/endpoint-triage/) | Process tree and handover that does not assert malware. | None |
| 32 | [Alert correlation](/lab-files/alert-correlation/) | Deduplicated alerts, stated correlation rule and bounded grouping. | None |
| 33 | [SOC query workbook](/lab-files/soc-query-workbook/) | Saved SQL, result tables, distinct counts and join explanation. | Log ingestion; login triage; alert correlation |
| 34 | [Incident case](/lab-files/incident-case/) | Notebook with timeline, two hypotheses, evidence needs and handover. | SOC query workbook; logging health; login triage; endpoint triage; HTTP triage; alert correlation; timeline analysis |
| 35 | [Containment tabletop](/lab-files/containment-tabletop/) | Decision table with authority, effect, evidence, owner and release check. | Incident case; access review; backup verification |
| 36 | [Incident communications](/lab-files/incident-communications/) | Staff message, technical handover and manager update. | Login triage; timeline analysis |

## Scope and limits

I will use fictional or dummy evidence within each lab's written safety boundary. This route authorises no work on real systems, accounts or data. A helper match can check a format or expected decision, but it cannot judge my reasoning, establish mastery, confer a credential or prove professional experience.

On 19 November 2026, I verified that this prepared route was live at [`/goal/`](https://jeremy-bryant.pages.dev/goal/) and that its [manifest](https://jeremy-bryant.pages.dev/goal/manifest.json) was available for commit `ef6e73f4b9565dcdec82831ca88dc151cc7969dc`. This confirms site availability at that check only; I am keeping every lab **Planned**, and I am not claiming completion or mastery. I will use the [full lab library](https://jeremy-bryant.pages.dev/security-labs/library/), [study plan](https://jeremy-bryant.pages.dev/security-labs/study-plan/) and [source page](https://jeremy-bryant.pages.dev/source/) for the underlying materials and method.
