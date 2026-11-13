# Worked reference: the loan cupboard

Read this only after saving a first attempt. This is an illustrative reference
answer to a fictional packet. It does not document independent completion, a
real incident, or an approved risk decision.

## 1. Scope and authority

Permitted work is reading the supplied fictional records, making an offline
assessment, and drafting questions and proposed actions. Real-device access,
visitor contact, service-desk reporting, configuration changes and exception
approval are excluded. The fictional device owner is the action owner in the
fixture; the authority to accept organizational risk is **not supplied**.
Stop if the exercise appears to require a real system or private record.
Publish only the fictional case IDs and sanitized reasoning.

## 2. Risk register

| ID | Event and harm | Starting score and basis | Proposed response and owner | Review | Residual position |
| --- | --- | --- | --- | --- | --- |
| item-1 | A missing loan laptop could expose the offline contact file. No file access is confirmed. | 2 × 3 = 6, high. G1 shows one plausible public-area opportunity, not repeated opportunities. G2 lists sensitive fields, so possible exposure could have serious impact. | Reduce; fictional `device-owner`. G3 proposes locked checkout, prompt reporting, encryption, lock and a smaller offline cache. | 1 November 2026 in the fixture. | Proposed 1 × 2 is a projection only. G3 contains no implementation check. |
| item-2 | An unverified visitor could enter the workroom and disrupt access to the only shift rota. No entry is confirmed. | 1 × 2 = 2, low. G4 shows a closed badge door and normal reception process; G5 shows team-level disruption if the rota is lost. | The fixture proposes accept; fictional `device-owner` must seek the actual acceptance authority. | 1 November 2026 in the fixture. | No score reduction. `acceptance: false`; acceptance remains pending. |

The scoring rubric is local to this lab. It is not a measured probability,
NIST score or organization-wide threshold. Risk appetite, legal obligations
and organizational policy are **not supplied**. A reviewer may support a
different score if the same rubric and evidence justify it. Because the case
date is 25 October 2026, the fixture calls these reviews planned. At a later
date, a real owner would need to recheck the deadlines; the old fixture cannot
establish a current review status.

## 3. Control-evidence matrix

| Proposed control | Source | Intended effect | Operation shown? | Bounded next check |
| --- | --- | --- | --- | --- |
| Locked storage and named checkout | G3 | Reduce loss opportunity and improve custody. | No. | Ask for a sample checkout record and observe the storage process in an authorized setting. |
| Prompt lost-device reporting | G3 | Start response sooner. | No. | Check the approved reporting route and a fictional tabletop response time. |
| Encryption and automatic lock | G2–G3 | Limit use of an unattended device. | No; the loss-time state is unknown. | On an authorized test device, inspect configuration and lock behavior; do not infer the lost device's state. |
| Reduced offline contact cache | G2–G3 | Limit the fields exposed if the file is accessed. | No. | Compare an approved sample schema with the stated minimum fields, without publishing records. |
| Staffed entry and booking check | G4–G5 | Reduce unauthorized entry opportunity. | Baseline reception is described; no new check is supplied. | Have the owner review an authorized entry-process sample. |

The matrix distinguishes a proposed safeguard from evidence that it operated.
Even a successful test on a different device or day would not prove the lost
laptop's state at the time of loss.

## 4. Exception or acceptance decision

**Request:** retain the fictional visitor-entry risk at the baseline score.
**Status:** pending; no approval record. **Business reason:** the case suggests
a staffed reception and closed badge door, while the rota has limited team
impact. **Owner:** fictional `device-owner`; organizational acceptance
authority is **not supplied**. **Review date:** 1 November 2026 in the fixture;
no extension or sign-off is evidenced. **Reopen if:** entry is observed, the
door is found open, the rota's criticality changes, or the owner supplies a
different risk threshold. Do not describe this risk as accepted merely because
the fixture's `treatment` field says `accept`.

## 5. Challenge log

**Challenge raised during reference preparation:** A low teaching score
does not establish that an organization may accept the risk. The packet lacks
the acceptance authority and threshold. A proposed lower score for item-1
also depends on controls for which G3 provides no verification.

**Disposition:** retained both points in the reference. They follow from G3,
G5 and the fixture's `acceptance: false`; no external system was queried.
**Next validation:** obtain an authorized control check and a recorded owner
decision in a future fictional or explicitly authorized scenario. **Human
decision:** not made; reviewer assessment remains pending.

## 6. Public-safe decision report

**Question and scope.** Review two fictional risks in an offline teaching
packet: a missing loan laptop and an unverified visitor outside a workroom.
No real person, device or account was assessed.

**Evidence.** G1 records one public-area handover opportunity. G2 records a
sensitive offline file but does not confirm access or loss-time protection.
G3 lists proposed controls without checks. G4–G5 describe a closed badge door,
normal reception process and the only shift rota.

**Assessment.** The lab rubric places the laptop at 6/high and visitor entry
at 2/low as of 25 October 2026. These are teaching scores, not incident
findings or quantified probabilities. The proposed laptop residual score has
not been demonstrated. Visitor-risk acceptance has not been approved.

**Decision requested.** The fictional owner should establish the authorized
reporting route, verify applicable device controls, identify the person who
may accept risk, and review both dated entries. A real response would require
new, authorized evidence. Do not claim a confirmed data breach, approved
exception, or legal compliance from this packet.

## Framework trace

The exercise relates conceptually to CSF 2.0's Govern categories for risk
management strategy (GV.RM), roles and authorities (GV.RR), and oversight
(GV.OV). This is a learning map to [NIST CSF 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20),
not a claim that any CSF outcome has been achieved. The register's event,
likelihood, impact and ownership fields are informed by [NIST IR 8286A Rev. 1](https://csrc.nist.gov/pubs/ir/8286/a/r1/final).
