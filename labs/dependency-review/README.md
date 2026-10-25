# Check software versions against a notice

A software list can help you find items that need review. It cannot prove that a flaw can be used. In this lab, compare fictional versions with a notice about affected versions. Then explain what the supplied path evidence does and does not show.

Allow **30–45 minutes** for a first pass. Split the task if needed. Return to the recall task on another day. You need to open files, edit a small JSON worksheet and read basic security terms. You do not need work experience, a cloud account or coding skills. No program changes are required.

## Useful terms

- **SBOM:** software bill of materials. It lists the parts used in software.
- **Advisory:** a notice that names affected versions.
- **Range:** the versions between two bounds.
- **Runtime:** when the deployed app runs.
- **Development dependency:** a tool or package used to build or test the app.
- **Reachability:** whether a path through the program can reach a part.
- **Exploitability:** whether the needed conditions exist to use a flaw to cause harm.

## Read the case

The `data` section has a nonempty `components` list and an `advisories` list. The latter may be empty.

Each component has a unique `id`, a fictional `name` that starts with `demo-`, and a `version`. Its `scope` is either `runtime` or `development`. Its `reachability` is `reachable`, `not-demonstrated` or `unknown`. The nonempty `evidence` field states what supports that claim. Different component IDs may list different installed versions of the same package.

Each advisory has a unique fictional `DEMO-ADV-NNN` ID, a `package`, an `introduced` version and a `fixed` version. These are dummy notices. They are not real CVEs or claims about real packages. A CVE is an identifier for a publicly known security flaw.

## Compare the versions

Use stable three-part versions in the form `X.Y.Z`. Each part is a whole number from 0 to 9999. Leading zeroes are not allowed, except the single digit 0.

Compare the three parts as numbers, from left to right. For example, `(1, 9, 9) < (1, 10, 0)`. Do not sort the version text as a string. This model rejects prefixes, pre-release forms, build metadata, wildcards and shortened forms.

The affected range is `[introduced,fixed)`. It includes `introduced` and stops just before `fixed`. The introduced version must be lower than the fixed version. Check every supplied range for the exact package name. Being above one range does not rule out a match with a later range.

## Choose a decision

Use one exact decision per component ID. Apply the rows in this order:

| Decision | Meaning |
| --- | --- |
| `no-advisory-supplied` | There is no notice for this package in the supplied set. |
| `outside-supplied-ranges` | A notice exists, but this version matches none of its supplied ranges. |
| `affected-review-build-exposure` | The version matches a range and its scope is development. Use this row for any reachability label. |
| `affected-prioritise-runtime-path` | The version matches, runs in the app and has supplied evidence of a reachable path. |
| `affected-validate-path` | The version matches and runs in the app, but a path has not been demonstrated. |
| `affected-investigate-path` | The version matches and runs in the app, but reachability is unknown. |

"Not demonstrated" does not mean unreachable. The output lists each matching advisory ID and range. Before choosing an update, review the functions at risk, ways to reduce the risk and conditions needed to use the flaw. Check that the update works with the app. Then test it. A version match alone does not answer all those questions.

## Run the exercise

From the repository root, use `cd labs/dependency-review`. Use Python 3.10 or later. On Windows, `py` may replace `python` if that is your installed launcher. No package install, account or billing setup is needed. The commands work offline and change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any extracted `.txt` evidence. Edit `run/attempt-01/answers.json`. Use the exact labels in the table above. Write your own explanation. In `evidence`, cite IDs or lines from your case. Keep `notes.txt` for your prediction, remaining doubt and help used.

Save that first answer before checking it:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has exactly three fields: `decisions` (an object), `explanation` (text) and `evidence` (a list of text references). An evidence entry could be an actual record ID and field name. Do not invent a reference.

The `check` command compares decision strings and requires text in the written fields. A person must judge that text. The `verify` command checks the supplied cases, not learner skill.

Exit 0 means success or a match. Exit 1 means a difference or missing written fields. Exit 2 means bad input. The default `--case` is the guided fixture beside the script. Explicit input paths start from the current working folder. The `--out` path starts from this lab and must be a new folder below `run/`.

Prepare new folders for the next cases:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with the chosen folder. Edit practice copies only. Keep the fixture and reference files intact.

## Hand over the evidence

Save a worksheet and short note for each case. Include your prediction, any change in your answer, a limit and one next check. Record help used, including the worked example. Ask a reviewer to trace your decision from the cited records and spot any claim that goes too far.

Independent skill remains **unassessed** until someone checks the evidence and reasoning. A matching output is not a qualification or work experience. These are fictional practice cases, not assessment submissions.

## Limits

This lab does not install packages, fetch live notices or use an exploit. It does not resolve a full chain of packages or model each ecosystem's version rules. It trusts the supplied inventory and path evidence. Being outside these dummy ranges does not prove software safe.

## Primary reference

This specification defines numeric major, minor and patch order. It also rules out leading zeroes in those numbers. The lab uses only stable three-part versions. Its affected-range rule is a teaching rule.

- [Semantic Versioning 2.0.0 specification](https://semver.org/)

The link was checked on 23 October 2026. It is optional reading; the lab does not fetch it. Read [the worked example](WORKED-EXAMPLE.md) after your prediction. Use [the drills](DRILLS.md) for varied practice.
