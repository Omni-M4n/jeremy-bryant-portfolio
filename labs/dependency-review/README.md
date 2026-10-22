# Triage a fictional software inventory and advisory ranges

Read a small software inventory, compare versions numerically, and distinguish an affected range from demonstrated exposure. Include build dependencies and uncertainty in a practical handover.

**Time:** 30-45 minutes for a first pass; use the later recall task on another day.
**Prerequisites:** Basic file navigation, editing a small JSON worksheet, and introductory networking/security vocabulary. No professional security experience, cloud account, coding background or programming changes are required.

> **Vocabulary:** **SBOM**: software bill of materials, an inventory of components. **Advisory**: a notice describing affected versions. **Range**: version interval. **Runtime**: when the deployed application runs. **Development dependency**: software used to build or test. **Reachability**: whether a relevant execution path can reach a component. **Exploitability**: whether conditions permit harmful use.

## Evidence and exact semantics

`data` contains nonempty `components` and an `advisories` list, which may be
empty. A component has unique `id`, fictional `name` starting `demo-`, `version`,
`scope` (`runtime`, `development`), `reachability` (`reachable`,
`not-demonstrated`, `unknown`), and nonempty `evidence` describing that claim.
Different component IDs may name different installed versions of the same package.
An advisory has a unique fictional `DEMO-ADV-NNN` ID, `package`, `introduced`,
and `fixed`. These are not real CVEs or claims about real packages.

Versions must be stable `X.Y.Z`: each part is an integer from 0 through 9999,
with no leading zeroes except the single digit 0. Compare integer triples,
not strings: `(1, 9, 9) < (1, 10, 0)`. Prefixes, pre-releases, build metadata,
wildcards and shortened forms are rejected. The range is `[introduced,fixed)`:
introduced is included; fixed is excluded; introduced must be less than fixed.
All supplied ranges for an exact package name are examined.

Use one exact decision per component ID, with this precedence:

| Decision | Meaning |
| --- | --- |
| `no-advisory-supplied` | No advisory for that package in the supplied set. |
| `outside-supplied-ranges` | Advisory exists, but this version matches no supplied range. |
| `affected-review-build-exposure` | Affected development dependency, regardless of reachability label. |
| `affected-prioritise-runtime-path` | Affected runtime component with supplied reachable-path evidence. |
| `affected-validate-path` | Affected runtime component where a path has not been demonstrated. |
| `affected-investigate-path` | Affected runtime component with unknown reachability. |

"Not demonstrated" does not mean unreachable. Multiple advisories may have
separate ranges; exceeding one fixed boundary does not exclude a different
later range. Output lists matching advisory IDs and intervals. Compatibility,
actual vulnerable functions, mitigations and exploit preconditions still need
review before selecting and testing an update.

## Run the exercise

From the repository root, enter this folder with `cd labs/dependency-review`.
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

There is no package installation, network advisory feed, exploit, dependency resolver or ecosystem-specific version logic. Inventory freshness and reachability evidence are supplied assertions. Being outside these fictional ranges establishes no universal safety claim.

## Primary references

The specification defines numeric major/minor/patch ordering and no leading zeroes. This exercise intentionally supports only the stable three-part subset and a fictional half-open advisory range convention.

- [Semantic Versioning 2.0.0 specification](https://semver.org/)

Links are optional further reading, checked 2026-10-23. Running this lab does
not fetch them. See [the worked example](WORKED-EXAMPLE.md) after your prediction
and [the drills](DRILLS.md) for varied practice.
