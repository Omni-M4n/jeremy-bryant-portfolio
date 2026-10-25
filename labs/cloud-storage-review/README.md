# Trace a storage exposure path

Trace who can read stored files without signing in. Check two ways to grant access and three ways to block it. Explain when a grant is blocked and what could make it work again.

**Time:** Allow 30-45 minutes for your first pass. Try the recall task on another day.
**Before you start:** You need to open files and edit a small JSON worksheet. JSON stores named fields and lists as text. Basic network and security terms will help. You do not need work experience, a cloud account or coding skills. You will not change code.

## Key words

A **bucket** holds stored objects, such as files. A **policy** sets rules that grant or deny access. An **ACL** is another list of access rights. **Anonymous read** means reading without signing in. A **dormant grant** is a grant that a control blocks for now. A **Boolean** is either `true` or `false`.

## Evidence and exact rules

The case format is set out in [the shared contract](../FOUNDATION-CONTRACT.md). The `data` field has `account_block_public` and a `buckets` list. The list must not be empty. `account_block_public` is a Boolean.

Each bucket has these fields. Each `id` must be unique and lowercase.

| Field | Allowed values |
| --- | --- |
| `id` | A unique lowercase ID. |
| `purpose` | `internal` or `public-site`. |
| `data_class` | `public`, `internal` or `restricted`. |
| `approval` | `approved` or `none`. |
| `bucket_block_public` | A Boolean. |
| `policy_public_read` | A Boolean. |
| `acl_public_read` | A Boolean. |
| `explicit_deny_public_read` | A Boolean. |

The tool rejects unknown keys and repeated IDs. Each flag must be a Boolean.

This is a small practice model. It is **not an AWS evaluator**. Apply the rules in this order:

1. There is a public grant if the policy **OR** the ACL allows public read. Either route is enough.
2. A block applies if the account block, bucket block **OR** explicit deny is true. Any one of these blocks both grant routes here.
3. A grant works only if no block applies. That public access is approved only if all three approval tests pass. The purpose must be `public-site`, the class must be `public`, and approval must be `approved`.

Use an exact decision string for each bucket ID:

| Decision | Exact meaning |
| --- | --- |
| `no-public-grant` | Neither grant exists. Blocks do not affect this label. |
| `blocked-public-grant` | At least one grant exists and at least one block applies. |
| `public-read-approved` | A grant works and all three approval tests pass. |
| `public-read-unapproved` | A grant works but not all three approval tests pass. |

Approval does not override the data class. Removing a policy grant does not remove an ACL grant. This model checks read access only.

## Run the exercise

From the repository root, enter this folder with `cd labs/cloud-storage-review`.

Use Python 3.10 or newer. On Windows, you may use `py` in place of `python` if it is your installed launcher. You do not need to install packages or set up an account or billing. All commands run offline. They change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any `.txt` evidence files. Open the blank `run/attempt-01/answers.json` worksheet. Fill in each decision with an exact label from the rules above. Write your own reason for each choice. In `evidence`, cite record IDs or line numbers from this case. Use `notes.txt` to record your first prediction, doubts and any help used.

Save your prediction before you run these commands:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has just three fields:

- `decisions` is an object. It pairs each record ID with your chosen label.
- `explanation` is text. Write why you chose those labels.
- `evidence` is a list of text references. You could name a record ID and its field. Use IDs from your case. Do not invent them.

`check` compares the decision labels. It also checks that you filled in the written fields. A person must judge whether those words are right. `verify` checks the supplied test cases. It does not assess your skill.

The exit code tells you what happened. Code 0 means success or a match. Code 1 means a mismatch or blank written fields. Code 2 means invalid input. If you omit `--case`, the command uses the guided case beside the script. Input paths start from your current terminal folder. The `--out` path starts from this lab folder. It must name a new folder below `run/`.

Use fresh folders for the next cases:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with your chosen folder. Edit practice copies only. Do not overwrite the supplied fixtures or reference answers. Fixtures are the starting cases.

## Deliverable and handover

Save a filled worksheet and a short evidence note for each case. Include your first prediction and any change to it. State what is still unclear. Name one next check that these files cannot answer. Record any help used, including the worked example.

Ask a reviewer: "Can you reach my decision from these record IDs? Which claim goes beyond the evidence?" Your skill at doing this alone is still **unassessed**. A matching output does not prove skill, a qualification or work experience. These are made-up practice cases. They are not work for assessment.

## Limits

Real storage services have more complex policy rules. Access may depend on conditions, object ownership and separate public-access settings. Do not apply this Boolean model to a real provider account. Review a blocked grant too. A later settings change could make it public.

## Primary references

The provider guide explains how access grants and blocks interact. This exercise puts them into a few Boolean fields. It does not copy the provider's four settings or all their rules.

- [AWS: blocking public access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)

The links are optional extra reading. They were checked on 2026-10-23. The lab does not fetch them. Read [the worked example](WORKED-EXAMPLE.md) after you save your prediction. Use [the drills](DRILLS.md) for more practice.
