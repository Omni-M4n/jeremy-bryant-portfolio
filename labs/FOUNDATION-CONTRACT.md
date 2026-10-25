# Additional foundation labs: maintained contract

This contract covers the original twenty added foundation labs, numbered 07–26
in the practice guide. It does not cover all 86 packages. These twenty share
`foundation_runtime.py`. That file reads and writes files and handles commands.
Each folder keeps its own topic rules in `lab.py`. Each lab has its own logic.
Use Python 3.10+ and its standard library only. The standard library is the set
of tools that comes with Python.

## Module interface

Each `lab.py` exports `LAB_ID`, `ROOT`, and `analyse(case)`. It then calls
`main(ROOT, LAB_ID, analyse)` under its main guard. The guard runs this call only
when the file is run as a script. To import the shared module, add
`str(Path(__file__).resolve().parents[1])` to `sys.path`.

The analysis must be a pure function. It reads the case and returns a result.
It must not write files, use the network, start processes or change the host.
The host is the computer that runs the code.

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

`context`, `data`, and `artifacts` are objects. Each holds named fields and their
values. Artifacts are readable evidence files. The artifacts object may be
empty. Each artifact name must be a simple lowercase basename with an extension.
A basename is just a file name, with no path to a folder.

The topic analyser checks each input field. It must raise `ValueError` for data
it does not support or data that conflicts with itself. Bad data must not become
a safe verdict without an error. Keep the input data intact. Use only reserved
addresses and `.test` names. These are names and addresses set aside for examples.

The analyser returns exactly:

```json
{
  "decisions": {"record-id": "a-short-explicit-result"},
  "observations": ["Specific facts and calculations supporting the results."],
  "limitations": ["What this small model cannot establish."]
}
```

Decisions map unique string IDs to result strings. The mapping must not be empty.
Each result string must also have text. Observations and limitations are lists
of strings. Neither list may be empty. An observation states a fact or a check.
A limitation states what the result cannot prove. Every result needs evidence.
Do not claim that a small check proves all parts of a system are safe.

Work out each reference answer through a separate review of the evidence.
Save these outputs in `reference/<case_id>.json`. They must use the same structure.

## Common commands

- `python lab.py cases`: list the three scenarios.
- `python lab.py prepare --scenario guided --out run/attempt-01`: create a fresh
  case, readable artifacts, blank `answers.json`, and a notes template. Put the
  output below the lab's `run/`. The command refuses existing folders and linked
  paths. A linked path points to a file or folder elsewhere.
- `python lab.py show --case run/attempt-01/case.json`: show input evidence.
- `python lab.py analyse --case run/attempt-01/case.json`: show the reference
  analysis. Keep this closed until the learner saves a prediction.
- `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`:
  compare submitted decision fields. Require an explanation and evidence
  references. A person must still judge the explanation. The check cannot
  award mastery.
- `python lab.py verify`: validate all fixtures and compare actual output with
  the three shipped reference outputs. This does not assess a learner.

Default `--case` is `fixtures/guided.json` beside the script. An explicit input
path starts from the working directory, which is the terminal's current folder.
`--out` starts from the lab folder. An exit code is the number returned when a
command ends. These codes mean: `0` success or decision match;
`1` differences/incomplete worksheet; `2` invalid input or filesystem problem.
JSON output is the default. JSON stores data as named fields and lists.

The worksheet has `decisions`, `explanation` (string), and `evidence` (list of
record/line references as strings). A string is a text value. A matching answer
and some text do not prove that the explanation is right. All practice files
remain ignored by version control, which tracks changes to project files.

## Complete lab contents

Each lab contains `lab.py`, `test_lab.py`, `.gitignore`, `README.md`,
`WORKED-EXAMPLE.md`, `DRILLS.md`, three fixtures and three reference outputs.
The README states the task, skills needed first and time to allow. It gives the
input format, the exact meaning of each decision, commands and what to save.
It also states the limits and links to primary sources. The worked example
walks through the guided evidence. Use exact IDs and calculations.

Drills cover guided work, prompts, solo work and a changed case. They also cover
teach-back and later recall. Teach-back means explaining the result to someone
else. Recall means trying to remember the method after a delay. Provide a word
box and a handover prompt. A handover tells someone else what to check next.
Keep personal completion unassessed. In these twenty labs, the learner uses
commands and makes small edits to data or settings. Writing code is not required.

Unit tests check small parts of the code. They must test the topic rules, edge
cases and invalid inputs. A test must do more than compare a function with itself.
Run each folder's test file on its own. This avoids clashes between module names
when tests are found. `verify` compares all three explicit reference answers.
No network calls are part of execution.

All authored bytes use UTF-8/LF: UTF-8 text with LF line endings. Do not include
coursework, personal identifiers, credentials or production logs. Credentials
are secrets used to gain access. Production logs come from systems in real use.
These are original fictional exercises. A release manifest lists exact file
hashes. A hash is a fingerprint of file bytes. It can check file identity. It
cannot prove skill, who made a file, or that no similar work exists elsewhere.

## Collection maintenance

From `labs/`, `python check_foundation_release.py` checks the reviewed file list.
It also checks required contents for all twenty labs. Add `--tests` to run the
shared runtime suite and each topic suite. Each topic suite runs in its own
process. This also checks all sixty reference cases. A suite is a group of tests.
`--receipt NEW_FILE.json` saves the full output. It will not overwrite an earlier
receipt. Each check prints a short progress update.

After reviewing a new release, a maintainer can create a missing inventory with
`--write-manifest`. This refuses to overwrite an existing inventory. A planned
revision needs a new review and inventory update. These checks test the
materials. They cannot judge a learner's explanation or real-world security.
