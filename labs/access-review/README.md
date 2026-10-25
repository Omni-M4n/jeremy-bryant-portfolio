# Offline object-store access review

This original, fictional lab is guided training material for learning the difference between **authentication** (establishing who someone is) and **authorisation** (deciding what that identity may do). The program starts with a known identity and checks permissions; it does not authenticate anyone.

The task is to replace an overbroad policy with the smallest set of grants that meets the written business needs. This is **least privilege**: keep the access needed for the work, and remove access that has no stated need.

This is a toy permission model, not an AWS or Azure IAM evaluator. It runs locally with Python's standard library. It makes no network calls, needs no account or credentials, incurs no cloud service costs, and does not deploy or access a real object store. Passing it does not prove that a cloud policy is secure.

## Command contract

Run commands from this folder with Python 3.10 or later. `lab.py` is the maintained entry point; there are no dependencies to install.

| Command | Input and result | Exit code |
| --- | --- | --- |
| `python lab.py generate` | Creates a fictional scenario, expected matrix, starting policy, editable practice policy, and answer key in `run/`. Refuses to overwrite existing lab files. | `0` success; `2` invalid input or existing files |
| `python lab.py check` | Checks `run/practice-policy.json` against every expected access decision. Prints missing or excess permissions. | `0` exact match; `1` mismatches; `2` malformed input |
| `python lab.py review` | Compares the starting policy with the practice policy, including retained business access and removed excess. | `0` corrected policy matches; `1` mismatches; `2` malformed input |
| `python lab.py manifest --verify` | Verifies the SHA-256 hashes of the shipped source and fictional fixtures. | `0` matches; `1` differences; `2` unreadable/invalid manifest |

`generate`, `check`, and `review` accept `--run PATH`. Its default is the `run/` folder beside the script, independent of the current working directory. `check --policy PATH` selects another policy; `review --before PATH --after PATH` selects two policies. Explicit paths are relative to the current working directory. Add `--json` for machine-readable command output. Input errors go to standard error. A passing result checks permissions against this lab's stated needs, not a learner's understanding.

## Exact model

1. The scenario lists a finite set of identities, roles, and resources. Each identity has exactly one role. Multiple identities may share a role.
2. A grant names one exact role, one exact resource, and a nonempty list of actions. The only actions are `read`, `write`, and `delete`.
3. An identity may perform an action on a resource if its role has a matching grant containing that action. Otherwise the decision is deny. An empty `grants` list denies everything.
4. Actions are independent. `write` does not imply `read`; `delete` does not imply `write`. Matching is case-sensitive.
5. There are no wildcards, explicit deny statements, groups, inheritance, ownership rules, resource policies, conditions, paths, or provider-specific behaviour. Resource IDs represent whole fictional stores; the lab does not model individual objects.
6. Unknown identities, roles, resources, actions, duplicate entries, unsupported fields, and malformed JSON are errors. Invalid input is rejected instead of being counted as a valid denial.

The expected matrix contains every identity × resource × action combination exactly once. The checker also verifies that this matrix agrees with the scenario's written business rules. It separately compares every role's grants with those rules, including roles with no currently assigned identity. The policy is checked against that authority; it is not used to invent its own expected answers. Identity counts remain separate from the `role_missing_required`, `role_excess_allowed` and `role_mismatches` fields. Both checks must pass.

## Worked example

The shipped `fixtures/worked-example/` scenario uses three roles. Store and identity IDs are selected deterministically from synthetic names with seed `17`.

| Role | Business need | Unwanted access |
| --- | --- | --- |
| `report-reader` | Read the published reports store | Write/delete reports; any access to uploads or snapshots |
| `intake-operator` | Read and write the incoming uploads store | Delete uploads; any access to reports or snapshots |
| `archive-custodian` | Read published reports; read, write, and delete archive snapshots | Change reports; any access to uploads |

The starting policy grants all three actions on all three stores to every role: **27 allowed decisions**. The answer key grants only the seven required decisions: **7 allowed, 20 denied**. This retains all seven necessary decisions, including the custodian's required delete permission, and removes 20 unwanted decisions. Removing every grant would block legitimate work and fail the review.

```console
python lab.py generate
python lab.py check
python lab.py check --policy run/solution-policy.json
python lab.py review --after run/solution-policy.json
python -m unittest discover -s . -p test_lab.py -v
```

The first check is expected to exit with code `1`: the practice policy starts overbroad. The solution check and review should exit with code `0`. `solution-policy.json` is a supplied answer key, not evidence of learner work.

For example, a single grant has this shape (use the exact resource ID from your generated scenario):

```json
{
  "schema_version": 1,
  "grants": [
    {"role": "report-reader", "resource": "daily-reports", "actions": ["read"]}
  ]
}
```

This grants only report reading to identities with that role. The rest of that policy denies everything, so it would still need the grants for the other roles to satisfy the full scenario.

## Practice in three stages

These exercises are invitations to practise; independent completion and understanding have **not been assessed**. The supplied program and answer keys are guided learning scaffolds, not a claim that a learner wrote the tooling independently or worked in cloud production.

1. **Guided correction.** Run `generate`, read `run/scenario.json`, and edit only `run/practice-policy.json`. Remove grants that have no business purpose, then trim the remaining action lists. Run `check` after each change. Before looking at the answer key, explain why each remaining action is necessary. Run `review` to check that all seven necessary decisions remain and 20 excess decisions have been removed.
2. **Hints first.** Run `python lab.py generate --variant hints --seed 29 --run run-hints`. Work from `run-hints/scenario.json` and edit its practice policy. Hint: group business needs by role and resource, and test the deletion decisions carefully. Run `python lab.py check --run run-hints` and `python lab.py review --run run-hints`. These runs use different IDs and less feedback in the generated instructions; do not copy a policy with old resource IDs.
3. **Unfamiliar case.** Run `python lab.py generate --variant unfamiliar --seed 71 --run run-unfamiliar`. This case has four roles and four stores. Some roles need write-only or read-and-delete access. Make your own role/resource/action table from the business rules before editing. Use the same check and review commands with `--run run-unfamiliar`. Explain why granting `read` to every writer would be a mistake here. Change `--seed` and choose a new run folder for another deterministic naming variant.

The generated answer key and expected matrix remain available at every stage for self-checking. A seed changes synthetic names and rule order; `--variant unfamiliar` changes the business requirements and size of the case. A new seed alone does not create a new security model. Keep a short personal note about one excess permission removed and one legitimate permission preserved; do not claim this lab as real cloud experience.

## Files and checks

- `lab.py`: generator, strict validators, evaluator, checker, review report, and manifest command.
- `test_lab.py`: meaningful checks for retained business access, removed excess, default deny, independent actions, malformed inputs, determinism, CLI exit codes, and overwrite protection.
- `fixtures/worked-example/`: reproducible fictional inputs and supplied answers; seed `17`, guided variant.
- `PROVENANCE.json`: origin statement and SHA-256 inventory. It records file integrity, not factual or educational acceptance.
- `run/` and `run-*/`: ignored local practice and verification outputs. Keep originals in `fixtures/` intact.

Run `python lab.py manifest --verify` to verify shipped file integrity. Maintainers deliberately updating shipped source or fixtures can run `python lab.py manifest --write` after review; that refreshes hashes and does not establish independent authorship or learner competence.
