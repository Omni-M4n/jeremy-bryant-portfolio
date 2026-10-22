# Trace a storage exposure path

Practise tracing anonymous read access through two grant routes and three blocking controls. Explain the difference between an effective exposure and a dormant grant that could reappear after a setting changes.

**Time:** 30-45 minutes for a first pass; use the later recall task on another day.
**Prerequisites:** Basic file navigation, editing a small JSON worksheet, and introductory networking/security vocabulary. No professional security experience, cloud account, coding background or programming changes are required.

> **Vocabulary:** **Bucket**: a container of objects. **Policy**: rules granting or denying access. **ACL**: another permission list. **Anonymous read**: reading without signing in. **Dormant grant**: a grant currently blocked by another control.

## Evidence and exact semantics

The case envelope is defined in [the shared contract](../FOUNDATION-CONTRACT.md).
`data` contains `account_block_public` (Boolean) and a nonempty `buckets` list.
Each bucket has a unique lowercase `id`; `purpose` is `internal` or `public-site`;
`data_class` is `public`, `internal` or `restricted`; `approval` is `approved` or
`none`. The remaining fields are Booleans: `bucket_block_public`,
`policy_public_read`, `acl_public_read`, and `explicit_deny_public_read`.
Unknown keys, duplicate IDs and non-Boolean flags are rejected.

This is a deliberately simplified exercise model, **not an AWS evaluator**.
Evaluate in this order:

1. A public grant exists when policy **OR** ACL allows public read.
2. A blocker exists when account block **OR** bucket block **OR** explicit deny
   is true. Any blocker overrides both grant routes here.
3. Effective public access is approved only when purpose is `public-site`, class
   is `public`, and approval is `approved` together.

Use these exact decision strings for each bucket ID:

| Decision | Exact meaning |
| --- | --- |
| `no-public-grant` | Neither grant exists, whether or not blockers exist. |
| `blocked-public-grant` | At least one grant exists, but at least one blocker applies. |
| `public-read-approved` | An effective grant and all three publication conditions exist. |
| `public-read-unapproved` | An effective grant exists without all publication conditions. |

An approval does not override data classification. Removing a policy grant does
not remove an ACL grant. This model examines read access only.

## Run the exercise

From the repository root, enter this folder with `cd labs/cloud-storage-review`.
Use Python 3.10 or newer. On Windows, `py` may replace `python` if that is your
installed launcher. No package install, account, cloud subscription or billing
setup is needed. Commands run entirely offline and change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any extracted `.txt` evidence. Edit the blank
`run/attempt-01/answers.json`: fill every decision with the exact vocabulary
below, write your own explanation, and cite record IDs or line references in
`evidence`. Keep `notes.txt` for prediction, uncertainty and help used.
Only after saving your prediction:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has exactly `decisions` (object), `explanation` (text), and
`evidence` (list of text references). For example, an evidence entry can be a
record ID plus its field name. Use your own case IDs, not invented references.
`check` compares decision strings and requires nonempty written fields; a person
must assess their accuracy. `verify` checks shipped fixtures, not learner skill.
Exit codes are 0 for success/match, 1 for differences or incomplete written
fields, and 2 for invalid input. Default `--case` is the guided fixture beside
the script. Explicit input paths are relative to the working directory; `--out`
is relative to this lab and must be a new folder below `run/`.

For the next cases, prepare fresh folders:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with the chosen folder.
Edit practice copies only. Do not overwrite fixture or reference files.

## Deliverable and handover

Save one completed worksheet and a short evidence note for each case. Include
your prediction, changed judgment, uncertainty, and one next check you cannot
perform from this evidence. Record whether you used the worked example or help.
Ask a reviewer: "Can you reproduce my decision from these record IDs, and which
claim goes beyond the evidence?" Your independent status remains **unassessed**;
matching output is not a qualification, professional experience or proof of
mastery. These are original fictional practice cases, not assessment submissions.

## Limits

Real storage services have richer policy languages, conditional access, object ownership and separate public-access settings. Do not paste this Boolean model into a provider account. A blocked grant still deserves review because later configuration changes can expose it.

## Primary references

The provider documentation explains that several access routes and blocking settings interact. The exercise collapses them into named Boolean fields; it does not reproduce the four provider settings or their full evaluation rules.

- [AWS: blocking public access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)

Links are optional further reading, checked 2026-10-23. Running this lab does
not fetch them. See [the worked example](WORKED-EXAMPLE.md) after your prediction
and [the drills](DRILLS.md) for varied practice.
