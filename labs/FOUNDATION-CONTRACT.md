# Additional foundation labs: maintained contract

The twenty additional labs share `foundation_runtime.py` for file handling and
command syntax. Each folder owns its domain analysis in `lab.py`; this is not a
single detector with renamed inputs. Python 3.10+ and the standard library only.

## Module interface

Each `lab.py` exports `LAB_ID`, `ROOT`, and `analyse(case)`, then calls
`main(ROOT, LAB_ID, analyse)` under its main guard. Import the shared module by
adding `str(Path(__file__).resolve().parents[1])` to `sys.path`. Analysis is a
pure function: no writes, network, processes or host changes.

Case files are `fixtures/guided.json`, `fixtures/changed.json`, and
`fixtures/challenge.json`. All three must change the reasoning, not just names.
Each case has exactly these fields:

```json
{
  "schema_version": 1,
  "lab_id": "folder-name",
  "case_id": "guided",
  "title": "A short original scenario",
  "synthetic": true,
  "context": {"question": "What should be checked?"},
  "data": {},
  "artifacts": {"evidence.txt": "Optional readable evidence, UTF-8 text.\n"}
}
```

`context`, `data`, and `artifacts` are objects. Artifacts may be empty; artifact
names are simple lowercase basenames with an extension, never paths. The domain
analyser validates its input fields and rejects unsupported or contradictory
data with `ValueError`. It must not silently turn malformed data into a safe
verdict. Preserve input data. Use reserved addresses and `.test` names only.

The analyser returns exactly:

```json
{
  "decisions": {"record-id": "a-short-explicit-result"},
  "observations": ["Specific facts and calculations supporting the results."],
  "limitations": ["What this small model cannot establish."]
}
```

Decisions are a nonempty mapping of unique string IDs to nonempty strings.
Observations and limitations are nonempty lists of strings. Every result needs
evidence; avoid universal security verdicts. Independently reasoned reference
outputs live in `reference/<case_id>.json` and match that structure.

## Common commands

- `python lab.py cases`: list the three scenarios.
- `python lab.py prepare --scenario guided --out run/attempt-01`: create a fresh
  case, readable artifacts, blank `answers.json`, and a notes template. Output
  must be below the lab's `run/`; existing folders and linked paths are refused.
- `python lab.py show --case run/attempt-01/case.json`: show input evidence.
- `python lab.py analyse --case run/attempt-01/case.json`: show the reference
  analysis. Keep this closed until the learner has saved a prediction.
- `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`:
  compare submitted decision fields, requiring an explanation and evidence
  references. A person must still assess the explanation; no automatic mastery.
- `python lab.py verify`: validate all fixtures and compare actual output with
  the three shipped reference outputs. No learner assessment.

Default `--case` is `fixtures/guided.json` beside the script. Explicit input paths
are relative to the working directory. `--out` is relative to the lab folder.
Exit codes: `0` success or decision match, `1` differences/incomplete worksheet,
`2` invalid input or filesystem problem. JSON output is the default.

The worksheet has `decisions`, `explanation` (string), and `evidence` (list of
record/line references as strings). Matching fields plus nonempty prose do not
establish that the explanation is correct. All practice files remain ignored.

## Complete lab contents

Each lab contains `lab.py`, `test_lab.py`, `.gitignore`, `README.md`,
`WORKED-EXAMPLE.md`, `DRILLS.md`, three fixtures and three reference outputs.
The README states its purpose, prerequisites, time estimate, input format,
exact decision semantics, commands, deliverable, limits and primary references.
The worked example walks through the guided evidence with exact IDs/calculations.
Drills cover guided, prompts, independent, changed case, teach-back and later
recall. Provide a vocabulary box and a handover prompt. Keep personal completion
unassessed. The learner uses commands and small data/config edits, not programming.

Unit tests must exercise the domain logic, meaningful boundaries and invalid
inputs, not only compare a function with itself. Run each folder's test file
separately to avoid duplicate module names in discovery. `verify` compares all
three explicit reference answers. No network calls are part of execution.

All authored bytes use UTF-8/LF. Do not include coursework, personal identifiers,
credentials or production logs. These
are original fictional exercises. A release manifest records exact file hashes;
hashes establish identity, not competence, authenticity or global novelty.

## Collection maintenance

From `labs/`, `python check_foundation_release.py` verifies the reviewed file
inventory and required contents for all twenty labs. Add `--tests` to run the
shared runtime suite, each domain suite in a separate process, and all sixty
reference cases. `--receipt NEW_FILE.json` retains detailed output without
overwriting an earlier receipt. Each check prints compact progress.

After reviewing a new release, a maintainer can create a missing inventory using
`--write-manifest`; it refuses to overwrite an existing inventory. A deliberate
revision needs a new review and inventory update. These checks validate the
materials, not a learner's explanation or real-world security.
