# Cybersecurity and cloud learning goal

I will use this prepared, **planned** route through 32 existing labs to record the sequence and evidence I intend to produce. I will not claim completion, mastery, a credential or professional experience from the plan.

The three stages describe exercise complexity, not my current ability:

1. **Beginner — make bounded decisions:** rules-of-engagement (scope sheet); dns-triage (I will use a synthetic packet worksheet to match questions and visible replies by endpoints, ports, DNS ID, name and type, distinguish an A answer, NXDOMAIN and no visible reply, use only the supplied evidence rather than claim a live capture, and not treat the exercise as proof of packet loss, application success, answer truth, professional use, completion or mastery); access-review (permission matrix); login-triage (sign-in timeline); timeline-analysis (UTC timeline); network-address-path (packet-path diagram); tcp-handshake (I will retain a TCP flow table with exact frame references and sequence/acknowledgement calculations, use the supplied synthetic packet summaries to distinguish an observed handshake, reset, no visible response, missing final ACK, missing initial SYN and acknowledgement mismatch, and state that the excerpt cannot establish full connection state or root cause, that missing packets do not prove packet loss, firewall failure or server fault, that an observed handshake does not prove application success, and that matching helper results do not prove professional use, completion or mastery); asset-discovery (I will compare a supplied synthetic scan snapshot with the approved inventory, cite exact host and TCP-port evidence, and not treat the snapshot or a helper match as proof of ownership, vulnerability, current state, complete coverage, professional use, completion or mastery); vulnerability-prioritisation (I will retain a fictional finding-priority queue with exact record and field references, impact, exposure, evidence-of-use, service-importance and confidence inputs, each four-part score, any override, uncertainty and the next owner check; apply only the supplied local rubric to supplied fictional findings so unverified evidence becomes investigate, supplied fictional observed-exploitation records become urgent, and the rest become urgent, planned or routine by score; and state that the rubric is not CVSS, queue labels do not set deadlines, proof of concept does not prove exploitation, and helper matches do not prove a real vulnerability, real exploitation or current risk, professional use, completion or mastery); firewall-review (first-match trace); http-triage (observation/interpretation note); file-integrity (baseline comparison); backup-verification (copy-selection worksheet); cloud-storage-review (exposure-path worksheet); identity-lifecycle (joiner/mover/leaver worksheet).
2. **Intermediate — connect controls and evidence:** mfa-review (I will compare synthetic account-control records without claiming a real sign-in test or control effectiveness); cloud-audit-triage (audit timeline); shared-responsibility (service/task ownership table); iam-explicit-deny (policy decision table); temporary-credentials (session timeline); cloud-network-path (two-leg reachability diagram); log-ingestion (import and rejection reconciliation); logging-health (coverage timeline); restore-drill (dummy-data restore receipt); evidence-custody (dummy-file evidence register and copy receipt); secret-handling (I will trace exact listed DEMO-only markers and keep response proposals bounded).
3. **Advanced — build and communicate a case:** endpoint-triage (process tree); alert-correlation (deduplicated and correlated set); soc-query-workbook (saved SQL and result tables); incident-case (timeline, hypotheses, evidence needs and handover); containment-tabletop (authority and containment decision table); incident-communications (staff, technical and manager messages).

## Dependencies and review gate

I will keep the order dependency-closed. The named lab dependencies are:

- timeline-analysis → login-triage
- tcp-handshake → dns-triage
- asset-discovery → dns-triage
- vulnerability-prioritisation → asset-discovery, access-review
- mfa-review → identity-lifecycle
- shared-responsibility → cloud-storage-review, backup-verification
- iam-explicit-deny → access-review, identity-lifecycle
- temporary-credentials → access-review, identity-lifecycle, cloud-audit-triage
- cloud-network-path → firewall-review, network-address-path
- log-ingestion → login-triage, timeline-analysis
- logging-health → log-ingestion, timeline-analysis
- restore-drill → backup-verification, file-integrity
- evidence-custody → file-integrity
- secret-handling → file-integrity
- soc-query-workbook → log-ingestion, login-triage, alert-correlation
- incident-case → soc-query-workbook, logging-health, login-triage, endpoint-triage, http-triage, alert-correlation, timeline-analysis
- containment-tabletop → incident-case, access-review, backup-verification
- incident-communications → login-triage, timeline-analysis

Labs not listed above have no earlier lab dependency declared on this route. Before I begin a dependent lab, I will retain reviewed or equivalent evidence for each named dependency.

I will use five progress labels: **planned**, **guided**, **solo**, **reviewed** and **recall**. Every lab currently remains **planned**. A matching helper result does not advance a status by itself. My evidence set will preserve the case, first answer, method, exact references, conclusion, uncertainty, help, correction and next check. If review is unavailable, I will say that it is awaiting review.

I will use only fictional or dummy evidence within each lab's safety boundary. The route authorises no work on real systems, accounts or data.

On 19 November 2026, I verified that the [portfolio goal route](https://jeremy-bryant.pages.dev/goal/) and [route manifest](https://jeremy-bryant.pages.dev/goal/manifest.json) were live for commit `267a2e96eb0b1862f2292b9ca796c9acddab66d6`. This confirms site availability at that check only; I am keeping every lab **Planned**, and I am not claiming completion or mastery. I will use the [full lab library](https://jeremy-bryant.pages.dev/security-labs/library/), [study plan](https://jeremy-bryant.pages.dev/security-labs/study-plan/) and [source and downloads](https://jeremy-bryant.pages.dev/source/) for the supporting materials.
