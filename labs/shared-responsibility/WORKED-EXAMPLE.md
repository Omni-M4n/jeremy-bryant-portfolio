# Worked example: the guided VM

Use this only after saving a prediction. The evidence is synthetic and all rows
refer to `orchard-vm`. Agreement A1 assigns physical hosts to the provider and
the guest OS to the customer. These are different components.

| ID | Decision | Evidence and reasoning |
| --- | --- | --- |
| host | `provider:owner-matches:evidence-pass` | A1 and E1 agree on provider host patching; E1 supplies a current attestation. |
| guest | `customer:correct-owner:evidence-fail` | A1 leaves the guest with the customer. E2 reports a missing patch and a provider owner claim. |
| access | `customer:owner-matches:evidence-missing` | A2 leaves user choices with the customer. E3 supplies no review, so effectiveness is unknown. |
| copy | `customer:owner-matches:evidence-missing` | A3 explicitly excludes managed backup; E4 contains no customer job record. |
| accept | `customer:owner-matches:evidence-pass` | A4 and E5 show customer acceptance of one historical restored report. |

The useful next action for `guest` is to assign the guest patch task to the
customer operator and obtain a scoped retest. Do not treat the host attestation
as guest patch evidence. For `copy`, request a current job record with scope;
then check retention and perform an isolated restore acceptance check as needed.
The successful historical `accept` row does not fill the missing current backup
record. The evidence supports neither "all cloud controls failed" nor "the
provider has secured everything."

A good handover names A1/E2 for the guest issue, A3/E4 for the copy evidence gap,
and asks for the omitted backup scope and recovery-time requirements. In the
worksheet, preserve this reasoning and exact references, not just matching codes.
