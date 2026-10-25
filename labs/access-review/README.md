# Offline object-store access review

Who needs access, and what should they be able to do? This new, fictional lab guides you through those questions. Start with two terms:

| Term | Meaning |
| --- | --- |
| **Authentication** | Checking who someone is |
| **Authorisation** | Deciding what that identity may do |

The program starts with a known identity. It checks permissions. It does not authenticate anyone.

The starting policy gives too much access. Replace it with the smallest set of grants that meets the written business needs. A grant gives a role access to a resource. This is **least privilege**. Keep access needed for the work. Remove access with no stated need.

This is a toy permission model. It is not an AWS or Azure IAM evaluator. It runs locally with Python's standard library. It makes no network calls. It needs no account or credentials. There are no cloud service costs. It does not deploy or access a real object store. Passing it does not prove that a cloud policy is secure.

## Command contract

Run commands from this folder with Python 3.10 or later. `lab.py` is the maintained entry point. There are no extra packages to install.

| Command | Input and result | Exit code |
| --- | --- | --- |
| `python lab.py generate` | Creates a fictional scenario, expected matrix, starting policy, editable practice policy, and answer key in `run/`. Refuses to overwrite existing lab files. | `0` success; `2` invalid input or existing files |
| `python lab.py check` | Checks `run/practice-policy.json` against every expected access decision. Prints missing or excess permissions. | `0` exact match; `1` mismatches; `2` malformed input |
| `python lab.py review` | Compares the starting policy with the practice policy, including retained business access and removed excess. | `0` corrected policy matches; `1` mismatches; `2` malformed input |
| `python lab.py manifest --verify` | Verifies the SHA-256 hashes of the shipped source and fictional fixtures. | `0` matches; `1` differences; `2` unreadable/invalid manifest |

`generate`, `check`, and `review` accept `--run PATH`. The default is `run/` beside the script. This stays the same whichever folder your terminal uses. `check --policy PATH` selects another policy. `review --before PATH --after PATH` selects two policies. Explicit paths start from your current working folder. Add `--json` for output a program can read. Input errors go to standard error. A pass checks permissions against this lab's stated needs. It does not check the learner's understanding.

## Exact model

1. The scenario gives a fixed list of identities, roles and resources. Each identity has exactly one role. Several identities may share a role.
2. A grant names one exact role and one exact resource. It needs at least one action. The only actions are `read`, `write`, and `delete`.
3. An identity can act on a resource only through its role's grant. The grant must match that resource and include that action. Otherwise access is denied. An empty `grants` list denies everything.
4. Actions are separate. `write` does not imply `read`. `delete` does not imply `write`. Matching is case-sensitive, so letter case matters.

Keep these model limits in mind:

| Limit | Exact scope |
| --- | --- |
| Resource IDs | Whole fictional stores; no individual objects |
| Features not modelled | Wildcards, explicit deny statements, groups, inheritance, ownership rules, resource policies, conditions, paths or provider-specific behaviour |
| Rejected input | Unknown identities, roles, resources or actions; duplicate entries; unsupported fields; malformed JSON |

Invalid input is an error. It is not counted as a valid denial.

The expected matrix is a table of access decisions. It lists every identity × resource × action combination exactly once. The checker checks that table against the written business rules. It also checks each role's grants against those rules. This includes roles with no assigned identity. The business rules set the answers. The policy cannot define its own expected answers. Both identity and role checks must pass.

| Result group | Counts |
| --- | --- |
| Identity results | Access decisions for listed identities |
| Separate role results | `role_missing_required`, `role_excess_allowed` and `role_mismatches` |

## Worked example

The shipped `fixtures/worked-example/` case uses three roles. Seed `17` selects store and identity IDs from made-up names. The same seed always gives the same IDs.

| Role | Business need | Unwanted access |
| --- | --- | --- |
| `report-reader` | Read the published reports store | Write/delete reports; any access to uploads or snapshots |
| `intake-operator` | Read and write the incoming uploads store | Delete uploads; any access to reports or snapshots |
| `archive-custodian` | Read published reports; read, write, and delete archive snapshots | Change reports; any access to uploads |

The starting policy gives every role all three actions on all three stores. That means **27 allowed decisions**. The key grants only what is needed: **7 allowed, 20 denied**. All seven needed decisions remain. That includes the custodian's required delete permission. It removes 20 unwanted decisions. Removing every grant would block valid work and fail the review.

```console
python lab.py generate
python lab.py check
python lab.py check --policy run/solution-policy.json
python lab.py review --after run/solution-policy.json
python -m unittest discover -s . -p test_lab.py -v
```

The first check should exit with code `1`. The practice policy starts with too much access. The solution check and review should exit with code `0`. `solution-policy.json` is a supplied answer key. It is not evidence of learner work.

One grant looks like this. Use the exact resource ID from your generated scenario:

```json
{
  "schema_version": 1,
  "grants": [
    {"role": "report-reader", "resource": "daily-reports", "actions": ["read"]}
  ]
}
```

This lets identities with that role read reports only. The rest of the policy denies everything. It still needs grants for the other roles to meet the full scenario.

## Practice in three stages

These exercises are for practice. Independent completion and understanding have **not been assessed**. The supplied program and keys are learning aids. They do not show that a learner wrote the tool without help. They are not proof of work in cloud production.

1. **Guided correction.** Run `generate` and read `run/scenario.json`. Edit only `run/practice-policy.json`. Remove grants with no business purpose. Then trim the action lists that remain. Run `check` after each change. Before reading the key, explain why each remaining action is needed. Run `review`. Check that all seven needed decisions remain and 20 excess decisions are gone.
2. **Hints first.** Run `python lab.py generate --variant hints --seed 29 --run run-hints`. Work from `run-hints/scenario.json` and edit its practice policy. Hint: group business needs by role and resource. Test the deletion decisions with care. Run `python lab.py check --run run-hints` and `python lab.py review --run run-hints`. These runs use different IDs. Their generated instructions give less feedback. Do not copy a policy with old resource IDs.
3. **Unfamiliar case.** Run `python lab.py generate --variant unfamiliar --seed 71 --run run-unfamiliar`. This case has four roles and four stores. Some roles need write-only or read-and-delete access. Before editing, make a role/resource/action table from the business rules. Use the same check and review commands with `--run run-unfamiliar`. Explain why giving `read` to every writer would be a mistake here. For another naming variant, change `--seed` and use a new run folder. The same seed and variant always produce the same case.

The generated key and expected matrix are available at every stage. Use them for self-checks. A seed changes made-up names and rule order. `--variant unfamiliar` changes the business needs and size of the case. A new seed alone does not create a new security model. Note one excess permission you removed. Note one valid permission you kept. Do not claim this lab as real cloud experience.

## Files and checks

- `lab.py`: generator, strict validators, evaluator, checker, review report, and manifest command.
- `test_lab.py`: meaningful checks for retained business access, removed excess, default deny, independent actions, malformed inputs, determinism, CLI exit codes, and overwrite protection.
- `fixtures/worked-example/`: reproducible fictional inputs and supplied answers; seed `17`, guided variant.
- `PROVENANCE.json`: origin statement and SHA-256 inventory. It records file integrity, not factual or educational acceptance.
- `run/` and `run-*/`: ignored local practice and verification outputs. Keep originals in `fixtures/` intact.

Run `python lab.py manifest --verify` to check the shipped files. Maintainers may need to change shipped source or fixtures. After review, they can run `python lab.py manifest --write`. This refreshes hashes. It does not prove who wrote the work or a learner's skill.
