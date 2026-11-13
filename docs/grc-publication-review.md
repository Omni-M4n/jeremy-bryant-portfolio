# GRC publication review — 12–13 November 2026

## Scope and method

The public repository was cloned on a separate laptop and reviewed at base commit `d1128b3e4e34`. No desktop device, live target, private account, or production system was assessed. This review concerns teaching materials and portfolio presentation; it does not establish that the learner independently completed the exercises.

The review focused on `labs/risk-register/README.md` and its guided case, `labs/rules-of-engagement/README.md`, `labs/data-classification/README.md`, the accepted lab registry and the website navigation. The risk-register Python suite passed 9 tests. The static build, public-output check and Node suite passed after the changes below. Those checks validate implementation rules, not the quality of a person's GRC judgement.

## Findings and changes

| Observation | Evidence | Change | Remaining limit |
| --- | --- | --- | --- |
| GRC exercises were present but hard to find from the portfolio home. | The accepted registry groups ten packages under “Governance and reporting”; the home page led with the LG device project. | Added a GRC route and made it the first home-page action. | A route does not demonstrate independent practice. |
| The risk-register exercise distinguished projected residual risk from verified controls, but did not explicitly ask the learner to identify a missing organization-wide risk threshold or acceptance authority. | `risk-register/README.md` and `fixtures/guided.json` show fictional scores, an unaccepted risk and no supplied threshold or legal duty. | Added review prompts that require those gaps to be recorded rather than invented. | A human reviewer must judge the decision and any real policy or legal obligation. |
| Search discovery was disabled despite the stated goal of a public career portfolio. | HTML metadata and a site-wide `X-Robots-Tag` requested `noindex`. | Changed content pages to permit indexing; kept the 404 page `noindex`. | Search engines decide if and when pages appear. |
| There was no published GitHub Wiki. | The repository's public Wiki URL returned to the code page. | Enabled the Wiki with editing restricted to collaborators, published its GRC-first Home page, and kept the source copy in `docs/wiki-home.md`. | The Wiki is a navigation guide, not evidence of independent GRC practice. |
| The separate GRC exercises did not show one complete decision trail. | The risk-register lab had a fixture and scoring helper, but no connected scope, control-evidence, exception and reviewer record. | Added `GRC-PACK.md`, a fictional case packet, blank worksheet, worked reference and reviewer guide under `labs/risk-register/`; linked the pack and worked case study from the GRC route. | A first attempt and independent human review remain outstanding. |

## Framework check

The [NIST Cybersecurity Framework 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20) treats governance as a set of outcomes that informs other security work. [NIST IR 8286A Rev. 1](https://csrc.nist.gov/pubs/ir/8286/a/r1/final) discusses documenting risk scenarios, likelihood and impact in risk registers. The lab's 1–3 scale is expressly a teaching rubric; it is not a NIST scale or a certification claim.

## Next evidence to collect

Complete an unfamiliar GRC case without the worked answer, retain the first decision and rationale, record a source-based challenge to the decision, have a person review it, and publish a sanitized decision memo with a changed-case retest. Do not mark the work independently assessed until that review occurs.
