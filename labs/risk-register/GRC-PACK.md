# GRC decision pack

This pack joins scope, risk treatment, control evidence, an exception decision,
reviewer challenge and a public-safe report around the fictional loan-laptop
case. It is a worked learning exercise, not a production assessment or proof
that Jeremy independently completed the work.

## Run the pack

1. Read [GRC-CASE.md](GRC-CASE.md) and the guided case in
   `fixtures/guided.json`. Use only the supplied facts and evidence IDs G1–G5.
2. Copy [GRC-WORKSHEET.md](GRC-WORKSHEET.md) outside the source folder. Save your
   first decision before opening the reference. Leave missing authority,
   obligations and control checks marked **not supplied**.
3. Run `python lab.py analyse --case fixtures/guided.json` to check the
   fixture's teaching labels. The helper does not assess the judgement in your
   worksheet.
4. Challenge your draft: record the strongest alternative interpretation of
   G1–G5, any unsupported inference, and a bounded check that would change the
   decision. Keep the challenge, response and reasons beside the first draft.
5. Compare with [GRC-REFERENCE.md](GRC-REFERENCE.md). Keep corrections beside
   the first draft, with their reasons; do not overwrite the first attempt.
6. Give [GRC-REVIEWER.md](GRC-REVIEWER.md) to a person for a changed-case
   challenge. Mark the result **unassessed** until that review occurs.

The six deliverables are: written scope, risk register, control-evidence
matrix, exception decision, challenge log, and sanitized decision report.
Keep the first draft, helper output, corrections and reviewer notes together.
Do not publish private records, credentials or real household details.

## Framework context

The [NIST CSF 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20)
Govern function provides context for roles, risk strategy, policy and oversight.
[NIST IR 8286A Rev. 1](https://csrc.nist.gov/pubs/ir/8286/a/r1/final)
discusses risk scenarios, likelihood, impact and risk-register records. This
case uses its own 1–3 teaching scale. The pack is an interpretation exercise,
not a NIST conformance assessment or a legal compliance determination.
