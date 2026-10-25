# Who is using this short-lived session?

A museum helper receives a visitor pass that ends at a set time. The helper, the job printed on the pass, and the pass itself are different things. You will trace those three parts in fictional cloud records.

This is a new core topic. It builds on the earlier identity and access labs. You check when a role session can be used and who it came from.

**Before you start:** access-review, identity-lifecycle and cloud-audit-triage. Allow 25-35 minutes.

## Words used here

An **identity** names a person or service. A **role** is a set of allowed
jobs. **Delegation** lets someone use a role. A **session** is a short period
of access. **Expiry** is its end time. **Revocation** takes access away before
that end. **Attribution** links a record to an identity. That link does not
prove who was at the keyboard.

## Set up a first attempt

Use Python 3.10 or newer, already on your computer. It works on Windows,
macOS or Linux. You need no extra packages, cloud account or network link.
A terminal is where you type commands. From the project folder, open one in
`labs/temporary-credentials`. The commands use `python`. If your Python 3
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

The four lists are `humans`, `roles`, `sessions` and `requests`.
Each record has a unique `id`. A human may have a `disabled_at` time.
A role lists `trusted_humans` and `actions` (read/write). It may have a
`revoke_at` time. A session names its `human`, `role`, `issued` time and
`expires` time. A request names its `session`, `at` time and `action`.
Times are made-up whole seconds from 0 to 100000.

At issue time, the session's human must be trusted and enabled. The expiry
must be later than the issue time. These records show successful issues.
The helper rejects records that break those rules.
Check requests in this order.

1. Before the issue time, use `not-yet-issued`.
2. At or after expiry, use `expired`.
3. At or after the role's revoke_at time, check when the session was issued. If it was strictly before that time, use `revoked`.
4. If the role does not grant the action, use `action-not-granted`.
5. In all other cases, use `allowed-in-model`.

The start time counts. The end time does not. Disabling the human stops new
sessions from being issued here. It does not revoke an existing session.
A session issued exactly at the revoke time is not an older session.
The session IDs act as fake tokens. They have no power outside this file,
so you need no secret token.

## Small operation

Make a new changed-case copy. Add a role revoke_at time of 40.
Draw q2's timeline before and after this edit. Do this before you run analyse.
Keep the human's disabled_at field as it is. Explain which change affected
the existing session.

## Evidence and handover

Save a human -> role -> session timeline and a table of requests.
Keep your expiry checks, revoke checks and first prediction. In your handover,
give the record IDs, the last allowed time and the next check.
Give one reason why a record may not prove who used a session.

Label the stage of your work. Was it a first attempt, done with prompts,
checked on your own, or recalled later? A matching answer alone does not
show that you have learnt the skill or used a real cloud tool.

## Limits and sources

This is a practice model with chosen time rules. It does not issue real
tokens or test a cloud service's access rules. It leaves out policy changes
and clocks that run fast or slow. It leaves out delays before changes take effect
and flows that renew tokens. It also leaves out using one role to reach
another, or trust between accounts. Real services and session types differ
in how they revoke access.

The authors opened these source documents when they prepared this lab.
The helper uses the rules above. The sources explain how real services work.

- [AWS temporary credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html) - temporary credentials have an end time and are issued when requested.
- [AWS role session revocation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html) - a deny policy can target role sessions issued before a chosen cutoff; the model omits deployment delays and provider exceptions.
