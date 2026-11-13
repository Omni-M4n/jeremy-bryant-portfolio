# GRC methods and case map

The [portfolio GRC path](https://jeremy-bryant.pages.dev/security-labs/grc/) is the visual entry point. This Wiki page connects the case decisions to their source records and practice worksheets.

| Case | Question | Evidence | Practice |
| --- | --- | --- | --- |
| [Loan cupboard](https://jeremy-bryant.pages.dev/security-labs/grc/loan-cupboard/) | What response is justified when a loan laptop is missing and a separate visitor risk is proposed for acceptance? | Fictional records G1–G5, with unknown protection state and no acceptance sign-off. | [Case packet](https://github.com/Omni-M4n/jeremy-bryant-portfolio/blob/main/labs/risk-register/GRC-CASE.md), [blank worksheet](https://github.com/Omni-M4n/jeremy-bryant-portfolio/blob/main/labs/risk-register/GRC-WORKSHEET.md), [worked reference](https://github.com/Omni-M4n/jeremy-bryant-portfolio/blob/main/labs/risk-register/GRC-REFERENCE.md). |
| [Public site control review](https://jeremy-bryant.pages.dev/security-labs/grc/public-control-review/) | Did release `42148d7` meet its stated rule on 13 November 2026? | Read-only HTTP statuses, SHA-256 comparisons and response headers for the specified deployment. Later changes are outside that result. | [Full report](https://github.com/Omni-M4n/jeremy-bryant-portfolio/blob/main/docs/grc-public-site-control-review.md), [evidence manifest](https://github.com/Omni-M4n/jeremy-bryant-portfolio/blob/main/docs/grc-public-site-control-manifest.json), [blank worksheet](https://github.com/Omni-M4n/jeremy-bryant-portfolio/blob/main/docs/grc-control-review-worksheet.md). |

## How to make a decision trail

1. Write the system, owner, permitted actions and excluded actions.
2. Set the decision rule before reading the result. For a risk case, state the scoring rubric and the authority needed to accept risk. For a control check, state the expected observation.
3. Record each source with an ID. Separate the source fact from the conclusion it might support.
4. Give the result, action owner, review date and a check that could change the decision.
5. Preserve the first attempt and a later correction. Ask a person to challenge one source or inference before marking the work independently reviewed.

The loan case is a **fictional worked example**. Its numerical scores are local teaching choices, not measured probabilities or NIST scores. The public-site case is an **observed, read-only release check**. It does not cover account authentication, deployment permissions or recovery. Neither case proves legal compliance or independent mastery.

For framework context, use [NIST CSF 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20) and [NIST IR 8286A Rev. 1](https://csrc.nist.gov/pubs/ir/8286/a/r1/final). The case records, rather than the framework, supply the facts and decisions here.
