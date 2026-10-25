# Draw a small office service

A guest uses office Wi-Fi. A small heat sensor also connects. Draw how both could reach a records service. Show what must check each request along the way.

## Before you begin

Complete `network-address-path`, `http-request-construction` and `access-review`. Allow 35 minutes.

Use Python 3.10 or later and a text editor. Keep the full lab collection.
No extra package, account, network link or admin access is needed for the
offline helper. Open a terminal in this lab folder. The commands work in
PowerShell or a terminal with Python on its path. Keep
`../foundation_runtime.py` in place; this folder alone is not enough.

## Words used here

An asset is something worth protecting. A data flow is a path that data takes. A trust boundary divides places with different rules. Authentication checks who you are. Authorisation checks what you may do. TLS protects data as it travels.

## Make an attempt

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use a fresh attempt name if that folder exists. Keep all first drafts.
`prepare` writes only to a new folder below this lab's `run/` folder.
It refuses existing folders and linked paths.

1. Read the settings and supplied observations. Fill `diagram-template.md` in your attempt folder.
2. Draw staff Wi-Fi, guest Wi-Fi, the temperature sensor in `device-segment`, `records-service.test` and its record store.
3. Draw arrows for data paths. Mark where network rules apply and where the service checks a request.
4. For each path, list the asset, possible failure, control and evidence still needed. A control is a step that limits harm.
5. Trace at least two separate checks. What could still stop harm if the network rule failed? What could happen without the record permission check?
6. Compare a shared Wi-Fi password with a named account. A shared password does not identify each user. Named access can be revoked for one account. Neither grants access to records.

This is a paper review of settings. Do not scan radio channels or try to connect.
Write **not supplied** beside any missing test evidence.

## Decision labels and model rules

Each answer has two parts: `network;service`. Use one network value below.
Settings say what should happen. An observation says what the case reports.

| Setting | Observation | Exact network value |
|---|---|---|
| `block` | `unrun` | `configured-only` |
| `block` | `blocked` | `path-block-observed` |
| `block` | `reachable` | `configuration-observation-conflict` |
| `allow` | `unrun` | `path-needs-check` |
| `allow` | `reachable` | `path-reachable` |
| `allow` | `blocked` | `unexpected-block` |

Check the service even when the network path is blocked.
Use `listed-service-checks-present` when all three service checks are listed.
Otherwise start with `review-`, then add each missing check from this list.
Keep this order. Join multiple missing checks with commas and no spaces.

| Missing check | Exact text to add |
|---|---|
| Identity is `shared` or `none`, not `named` | `named-identity` |
| `resource_check` is false | `resource-permission` |
| Transport is `plain`, not `tls` | `transport-protection` |

Use one semicolon between the two parts, with no spaces.
Listed checks do not prove that they work. One blocked path does not prove
that all paths are isolated. Wi-Fi access may be `shared-password` or `named-users`.
The only destination is `records-service.test`.

## Save your answer before the reveal

First write your claim in your own words. Then use the labels above to fill
`answers.json`. Keep each item ID. Put your reasons in `explanation` and exact
record, field or line references in the `evidence` list. Keep the three fields
`decisions`, `explanation` and `evidence`. JSON needs double quotes, with no
comments or trailing commas. Use `notes.txt` to record help and doubts.

Save this first attempt before opening the worked example, `reference/` or
the analysis. Then compare:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
```

The check matches exact text and checks that you wrote reasons and references.
It cannot judge those reasons. A spelling or format mismatch is not proof of
poor reasoning. A person must review your work. A match does not prove mastery.

Exit 0 means the command or comparison passed. Exit 1 means an answer is
missing or differs. Exit 2 means bad input or a file error. The default case is
`fixtures/guided.json`. Input paths start from the current folder.
The `--out` path starts from this lab folder.

## Input rules

Each case has these fields: `schema_version`, `lab_id`, `case_id`, `title`,
`synthetic`, `context`, `data` and `artifacts`. Version is 1.
`synthetic` must be true. The three fixtures show the full data shape.
The helper rejects missing or extra fields, repeated IDs, empty required text,
wrong types and choices it does not support. Numbers must be whole numbers;
true and false do not count as numbers. Lists hold at most 20 unique entries.
Row lists hold 1-20 rows. The helper leaves the case unchanged.

## Keep evidence and clean up

Keep the case, supplied files, first draft, answers and notes. Put corrections
in a new draft. Mark the stage: first attempt, prompted, corrected,
independently reviewed or recall attempted. Mark any check you did not run.
Keep private evidence private.

Attempt files stay in ignored `run/`. The offline helper changes no host
settings. To clean up, close the editor. Save the evidence you need, then remove
only the attempt folder you made. Keep fixtures and private originals.

Give a reviewer your question, exact evidence references, draft, one limit and
one next action. Do not invent a result.

## Maintainer checks

```text
python test_lab.py
python lab.py verify
```

These check the offline helper and three worked reference cases. They do not
prove that a learner did the writing task or a real test.

## Limits and sources

Settings state a claim. Supplied observations cover one fictional path at a time. This helper runs no radio or network test.

The supplied people, systems and records are fictional. The helper sends no
messages and runs no live tests. It changes no accounts and publishes nothing.
These small teaching rules draw on the sources below. Their scores and labels
are local to the lab; they are not standards.
Primary sources opened on 25 October 2026:

- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) - Data flows, threats, controls and review.
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) - Identity and permission are separate checks.
