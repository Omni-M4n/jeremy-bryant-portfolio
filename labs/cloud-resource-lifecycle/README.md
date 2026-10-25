# What remains after a resource is retired?

A school club stops using a rented room but keeps paying for a cupboard. Removing one item does not prove the whole bill has ended. You will check who owns each item and when it needs review. Then you will check a plan to remove items from a made-up list.

This is a new core topic. It builds on asset discovery and shared responsibility. You check who owns items, what they cost and which items need others. Then you plan the order to remove them.

**Before you start:** asset-discovery and shared-responsibility. Allow 25-35 minutes.

## Words used here

A **resource** is something a service supplies, such as a machine or disk.
A **tag** is a label with a value. An **owner** is the team in charge of a
resource. A **dependency** is something another resource needs.
**Teardown** means removing resources in a planned order.
A **retention hold** means you must keep an item until its hold reason has
been reviewed.

## Set up a first attempt

Use Python 3.10 or newer, already on your computer. It works on Windows,
macOS or Linux. You need no extra packages, cloud account or network link.
A terminal is where you type commands. From the project folder, open one in
`labs/cloud-resource-lifecycle`. The commands use `python`. If your Python 3
command has a different name, use that name.

```text
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the small JSON file. JSON stores values with names. Here, `true` means
yes, `false` means no, and `null` means no value was given. Predict each
result first. Save it in `run/attempt-01/answers.json`. Fill in each decision
and explain why. List the record IDs in `evidence`. An ID is a record's name.
Keep this first attempt.

Run these commands only after you save your prediction.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The check looks at your answer words and checks that written fields are
filled in. A person must still review your reasons. Exit codes show how a
command ended. Code 0 means success. Code 1 means a mismatch or an unfinished
worksheet. Code 2 means the input is not valid. The `verify` command checks
the supplied cases. It does not score your work. These commands stay on your
computer and do not contact a cloud service.

Prepare `changed` in `run/attempt-02`. Prepare `challenge` in
`run/attempt-03`. Edit only these copies. Use a new output folder each time
so you keep each earlier attempt. To undo an edit, prepare a fresh copy.
Keep your evidence until someone reviews it. Later, remove only the named
practice folder you made. Never put personal records in it.


## Exact model

The input has `today`, `budget_units`, `spent_units`, `resources` and
`delete_order`. Dates are whole practice day numbers. Costs are made-up
whole units. They are not money or real prices. Each resource has `id`,
`owner`, `daily_units`, `depends_on` and `retain`. It may have `expires_day`.

Each resource gets flags in a set order. A flag is a short finding.
First is `owner-missing`. Next is `expiry-missing` or `review-due`.
Review is due if expiry is today or earlier. Join multiple flags with +.
If there are no flags, use `tags-current`. An expiry tag sets a review date.
It never deletes an item on its own.

Read delete_order from left to right. Block an item with a retention hold.
Also block any item that a remaining resource still needs. Skip a blocked
step and keep checking the later steps. The helper does not retry it.
This model checks each proposed step. It does not cancel the whole plan
when one step is blocked. If any step is blocked, use `plan=blocked`.
Otherwise, use `order-valid-in-model`. An empty order is valid and removes
nothing.

Add the daily_units of all items left. Use `cost=residual-cost` if the sum
is above zero. Otherwise, use `zero-model-cost`. Zero cost does not prove
every item has gone. Use `budget=alert-threshold-reached` when spent_units
is at least budget_units. Otherwise, use `below-alert-threshold`.
An alert does not enforce a spending cap.

The helper rejects wrong value types, links to unknown records and repeated
targets. It also rejects dependency cycles. A cycle is a chain of items
that need each other and leads back to where it started.

## Small operation

Make a new changed-case copy. Use the arrows in depends_on to write an order.
Predict which resources will remain and add their daily units. Then compare
your answer with the helper. This changes only a local plan. Never run
cloud deletion commands for this exercise.

## Evidence and handover

Save a list of owners and expiry dates. Draw which items need others.
Keep your ordered removal checklist, your sum of units left and your budget
assumptions. For each item, state whether to keep, delete or review it.
Name who must approve that step and which data must be kept.
Include a later check of the bill.

Label the stage of your work. Was it a first attempt, done with prompts,
checked on your own, or recalled later? A matching answer alone does not
show that you have learnt the skill or used a real cloud tool.

## Limits and sources

All listed items and costs are made up. The helper cannot see hidden
resources or snapshots (saved copies). It cannot see fees for moving data,
late bills or which real items need others. An owner tag does not prove
that the owner has approved a step. A held item needs a separate decision
before anyone removes it for real.

The authors opened these source documents when they prepared this lab.
The helper uses the rules above. The sources explain how real services work.

- [AWS tags](https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/what-are-tags.html) - tags store resource labels; they should not contain sensitive data.
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) - alerts can arrive after usage and costs can continue above a threshold.
- [AWS instance termination](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html) - data preservation and attached-volume behaviour need review before termination.
