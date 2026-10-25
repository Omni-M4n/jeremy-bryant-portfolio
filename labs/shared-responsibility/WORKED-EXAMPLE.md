# Worked example: the guided VM

Use this only after saving a prediction. The evidence is made up. All rows
refer to `orchard-vm`. Agreement A1 gives the provider the physical host tasks.
It gives the customer the guest OS tasks. These are different parts of the service.

| ID | Decision | Evidence and reasoning |
| --- | --- | --- |
| host | `provider:owner-matches:evidence-pass` | A1 and E1 agree on provider host patching; E1 supplies a current attestation. |
| guest | `customer:correct-owner:evidence-fail` | A1 leaves the guest with the customer. E2 reports a missing patch and a provider owner claim. |
| access | `customer:owner-matches:evidence-missing` | A2 leaves user choices with the customer. E3 supplies no review, so effectiveness is unknown. |
| copy | `customer:owner-matches:evidence-missing` | A3 explicitly excludes managed backup; E4 contains no customer job record. |
| accept | `customer:owner-matches:evidence-pass` | A4 and E5 show customer acceptance of one historical restored report. |

For `guest`, the next step is to give the guest patch task to the customer's
operator. Then ask for a new check of that task. The host report does not show
whether the guest was patched. For `copy`, ask for a current job record that
states its scope. Then check how long copies are kept. Use an isolated restore
check if needed to test whether the restored files meet the team's needs.
The earlier successful `accept` row does not fill the gap in current backup
records. The evidence does not show that all cloud controls failed. It also does
not show that the provider has secured everything.

A good handover names A1/E2 for the guest issue and A3/E4 for the copy evidence gap.
Ask which files the backup should cover and how soon they must be recovered.
These details are missing. Keep this reasoning and the exact references in your
worksheet, along with the matching codes.
