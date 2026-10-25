# Which policy statements apply?

A club lets helpers read its noticeboard files. A second rule protects one folder. When both rules match, which decision wins? You will make a request table, then change one copied policy line and explain the effect.

This extends [access-review](../access-review/README.md). The earlier lab only has rules that grant access. Here, you also use rules that refuse access. You check which object names each rule covers. This is a small model based on AWS rules. It is an extension to the earlier lab.

**Before you start:** access-review and identity-lifecycle. Allow 30 minutes.

## Words used here

**IAM** means identity and access management. These are rules about who may
do what. A **policy** is a set of rules. A **statement** is one rule. An
**ARN** is an AWS resource name. A **wildcard** stands for part of a name.
An **explicit deny** means a rule matches the request and says no.
An **implicit deny** means no rule grants the request.

## Set up a first attempt

Use Python 3.10 or newer, already on your computer. It works on Windows,
macOS or Linux. You need no extra packages, cloud account or network link.
A terminal is where you type commands. From the project folder, open one in
`labs/iam-explicit-deny`. The commands use `python`. If your Python 3
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

The input has `statements` and `requests`. These show a small part of a
policy. You cannot upload this file as an AWS policy. Each statement has
`id`, `effect`, `actions`, and `resource`. Its effect is `Allow` or `Deny`.
A request has `id`, `action` and `resource`. The model supports three actions.
They are `s3:GetObject` (read), `s3:PutObject` (write) and
`s3:DeleteObject` (delete).

Both the action and the resource must match. Uppercase and lowercase letters
in resource names must match too. An exact name matches only itself.
One `*` at the end matches any remaining characters. These may include
slashes. The helper refuses all other wildcard forms.

All requests come from the same identity. Assume it has already signed in
and proved who it is. All listed statements apply to it. It has no other
policies.

Use these answer words.

- Use `explicit-deny` if at least one `Deny` matches. This wins even if an `Allow` also matches.
- Use `allow` if an `Allow` matches and no `Deny` matches.
- Use `implicit-deny` if neither an `Allow` nor a `Deny` matches.

The order of statements does not matter. Unknown fields are errors.
Repeated IDs and actions outside the three listed above are errors too.
An empty list of statements is valid. It grants nothing.

## Small operation

Make a fresh guided copy. Change only s2's action to s3:DeleteObject.
Predict each request again. Explain which set of matching rules changed.
Keep both case files. Do not upload either file to a cloud service.

## Evidence and handover

Keep your first prediction, your table of policy decisions and your edited
copy. Write one sentence on how a missing grant differs from a matching deny.
Cite the statement and request IDs. In your handover, name the request you
would check next. Name a type of policy left out of this model that could
change a real result.

Label the stage of your work. Was it a first attempt, done with prompts,
checked on your own, or recalled later? A matching answer alone does not
show that you have learnt the skill or used a real cloud tool.

## Limits and sources

The helper checks only the listed rules for this identity. It leaves out
conditions, which set extra tests. It also leaves out policies on resources
and sessions, and role trust rules. It does not check permission boundaries
or organization controls, which can limit access. A result cannot prove
real AWS access. This lab does not use or change the access-review helper.

The authors opened these source documents when they prepared this lab.
The helper uses the rules above. The sources explain how real services work.

- [AWS policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html) - a matching explicit deny overrides an allow; other policy types also affect real requests.
- [AWS Resource element](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_resource.html) - resource names and wildcard scope select objects.
