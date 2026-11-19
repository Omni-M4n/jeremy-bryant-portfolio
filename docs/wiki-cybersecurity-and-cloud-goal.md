# Cybersecurity and cloud learning goal

My public goal is a **planned** route through 25 existing labs. I am publishing the sequence and the evidence I intend to produce; I am not claiming completion, mastery, a credential or professional experience.

The three stages describe exercise complexity, not my current ability:

1. **Beginner — make bounded decisions:** rules-of-engagement (scope sheet); access-review (permission matrix); login-triage (sign-in timeline); timeline-analysis (UTC timeline); network-address-path (packet-path diagram); firewall-review (first-match trace); http-triage (observation/interpretation note); file-integrity (baseline comparison); backup-verification (copy-selection worksheet); cloud-storage-review (exposure-path worksheet); identity-lifecycle (joiner/mover/leaver worksheet).
2. **Intermediate — connect controls and evidence:** cloud-audit-triage (audit timeline); shared-responsibility (service/task ownership table); iam-explicit-deny (policy decision table); temporary-credentials (session timeline); cloud-network-path (two-leg reachability diagram); log-ingestion (import and rejection reconciliation); logging-health (coverage timeline); restore-drill (dummy-data restore receipt).
3. **Advanced — build and communicate a case:** endpoint-triage (process tree); alert-correlation (deduplicated and correlated set); soc-query-workbook (saved SQL and result tables); incident-case (timeline, hypotheses, evidence needs and handover); containment-tabletop (authority and containment decision table); incident-communications (staff, technical and manager messages).

## Dependencies and review gate

I will keep the order dependency-closed. The named lab dependencies are:

- timeline-analysis → login-triage
- shared-responsibility → cloud-storage-review, backup-verification
- iam-explicit-deny → access-review, identity-lifecycle
- temporary-credentials → access-review, identity-lifecycle, cloud-audit-triage
- cloud-network-path → firewall-review, network-address-path
- log-ingestion → login-triage, timeline-analysis
- logging-health → log-ingestion, timeline-analysis
- restore-drill → backup-verification, file-integrity
- soc-query-workbook → log-ingestion, login-triage, alert-correlation
- incident-case → soc-query-workbook, logging-health, login-triage, endpoint-triage, http-triage, alert-correlation, timeline-analysis
- containment-tabletop → incident-case, access-review, backup-verification
- incident-communications → login-triage, timeline-analysis

Labs not listed above have no earlier lab dependency declared on this route. Before I begin a dependent lab, I will retain reviewed or equivalent evidence for each named dependency.

I will use five progress labels: **planned**, **guided**, **solo**, **reviewed** and **recall**. Every lab currently remains **planned**. A matching helper result does not advance a status by itself. My evidence set will preserve the case, first answer, method, exact references, conclusion, uncertainty, help, correction and next check. If review is unavailable, I will say that it is awaiting review.

I will use only fictional or dummy evidence within each lab's safety boundary. The route authorises no work on real systems, accounts or data.

Links: [goal page](https://jeremy-bryant.pages.dev/goal/) · [route manifest](https://jeremy-bryant.pages.dev/goal/manifest.json) · [full lab library](https://jeremy-bryant.pages.dev/security-labs/library/) · [study plan](https://jeremy-bryant.pages.dev/security-labs/study-plan/) · [source and downloads](https://jeremy-bryant.pages.dev/source/)
