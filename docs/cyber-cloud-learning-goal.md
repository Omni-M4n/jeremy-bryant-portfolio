# My cybersecurity and cloud learning goal

**Current status: planned.** I have selected this 27-lab route; I am not claiming that I have completed it, mastered its topics or used these methods in a professional role.

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
| 2 | [Access review](/lab-files/access-review/) | Role/resource/action matrix and least-privilege policy decision. | None |
| 3 | [Login triage](/lab-files/login-triage/) | Sorted sign-in timeline and bounded handover. | None |
| 4 | [Timeline analysis](/lab-files/timeline-analysis/) | UTC timeline with exact event references and uncertainty. | Login triage |
| 5 | [Network address path](/lab-files/network-address-path/) | Labelled packet-path diagram and route-choice worksheet. | None |
| 6 | [Firewall review](/lab-files/firewall-review/) | First-match trace with required and excess traffic decisions. | None |
| 7 | [HTTP triage](/lab-files/http-triage/) | Triage report separating observations, explanations and next check. | None |
| 8 | [File integrity](/lab-files/file-integrity/) | Baseline comparison classifying exact changes and baseline limits. | None |
| 9 | [Backup verification](/lab-files/backup-verification/) | Copy-selection worksheet using retention, scope, hashes and RPO. | None |
| 10 | [Cloud storage review](/lab-files/cloud-storage-review/) | Exposure-path worksheet with record IDs and unanswered check. | None |
| 11 | [Identity lifecycle](/lab-files/identity-lifecycle/) | Joiner/mover/leaver worksheet explaining keep, remove or review decisions. | None |

### Intermediate — connect controls and evidence

| # | Lab | Evidence I plan to retain | Earlier dependency |
| ---: | --- | --- | --- |
| 12 | [Cloud audit triage](/lab-files/cloud-audit-triage/) | Audit timeline separating actions, denials, gaps and attribution limits. | None |
| 13 | [Shared responsibility](/lab-files/shared-responsibility/) | Service/task table with owner, agreement, control evidence and gap. | Cloud storage review; backup verification |
| 14 | [IAM explicit deny](/lab-files/iam-explicit-deny/) | Request/statement table and one changed-policy comparison. | Access review; identity lifecycle |
| 15 | [Temporary credentials](/lab-files/temporary-credentials/) | Human-to-role-to-session issue, expiry and revocation timeline. | Access review; identity lifecycle; cloud audit triage |
| 16 | [Cloud network path](/lab-files/cloud-network-path/) | Two-leg path diagram and reachability table. | Firewall review; network address path |
| 17 | [Log ingestion](/lab-files/log-ingestion/) | Import report, rejected rows and source reconciliation. | Login triage; timeline analysis |
| 18 | [Logging health](/lab-files/logging-health/) | Coverage timeline with arrivals, heartbeats, gaps and next check. | Log ingestion; timeline analysis |
| 19 | [Restore drill](/lab-files/restore-drill/) | Dummy-data restore receipt with hashes, version and measured durations. | Backup verification; file integrity |
| 20 | [Evidence custody](/lab-files/evidence-custody/) | Dummy-file evidence register and copy receipt linking each copy to its recorded source, UTC handling records, hash checks and stated limits. | File integrity |
| 21 | [Secret handling](/lab-files/secret-handling/) | I will retain a DEMO-only secret exposure worksheet and evidence note tracing exact listed markers through configuration, saved changes and logs, separating observed exposure from proposed response and stating what the supplied files cannot prove. | File integrity |

### Advanced — build and communicate a case

| # | Lab | Evidence I plan to retain | Earlier dependency |
| ---: | --- | --- | --- |
| 22 | [Endpoint triage](/lab-files/endpoint-triage/) | Process tree and handover that does not assert malware. | None |
| 23 | [Alert correlation](/lab-files/alert-correlation/) | Deduplicated alerts, stated correlation rule and bounded grouping. | None |
| 24 | [SOC query workbook](/lab-files/soc-query-workbook/) | Saved SQL, result tables, distinct counts and join explanation. | Log ingestion; login triage; alert correlation |
| 25 | [Incident case](/lab-files/incident-case/) | Notebook with timeline, two hypotheses, evidence needs and handover. | SOC query workbook; logging health; login triage; endpoint triage; HTTP triage; alert correlation; timeline analysis |
| 26 | [Containment tabletop](/lab-files/containment-tabletop/) | Decision table with authority, effect, evidence, owner and release check. | Incident case; access review; backup verification |
| 27 | [Incident communications](/lab-files/incident-communications/) | Staff message, technical handover and manager update. | Login triage; timeline analysis |

## Scope and limits

I will use fictional or dummy evidence within each lab's written safety boundary. This route authorises no work on real systems, accounts or data. A helper match can check a format or expected decision, but it cannot judge my reasoning, establish mastery, confer a credential or prove professional experience.

I intend to publish this prepared route at [`/goal/`](https://jeremy-bryant.pages.dev/goal/). I will treat that route and its [manifest](https://jeremy-bryant.pages.dev/goal/manifest.json) as pending until I separately verify their deployment. I will use the [full lab library](https://jeremy-bryant.pages.dev/security-labs/library/), [study plan](https://jeremy-bryant.pages.dev/security-labs/study-plan/) and [source page](https://jeremy-bryant.pages.dev/source/) for the underlying materials and method.
