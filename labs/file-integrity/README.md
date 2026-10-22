# Offline file integrity and change triage

A fictional community workshop has approved a notice update. Other files may
also have changed. Your task is to describe the evidence, separate explained
changes from unexplained ones, and judge whether the baseline deserves confidence.

This is original guided practice for a beginner. It uses generated dummy text
files, runs entirely offline, and needs only Python 3.10 or later. There are no
accounts, live systems, executable payloads, or dependencies to install. You use
commands and explain results; you do not need to write a program.

Independent completion and understanding have not been assessed. The utility,
fixtures, and supplied answer key are learning scaffolds, not a claim of
professional experience or independent learner authorship.

## The security idea

A SHA-256 hash is a compact value calculated from file bytes. Comparing it with
a previously recorded value helps detect a byte change. A changed hash does not
explain the change: an approved edit and an unauthorised edit both alter bytes.
Even a line-ending conversion can alter a hash.

This lab combines three pieces of evidence:

1. A **baseline** records file names, byte lengths, and hashes before the change
   window, if that history is supported.
2. A **current inventory** records what is present now.
3. The supplied **change list** records approved paths and exact before/after
   hashes. A path or ticket number alone does not approve arbitrary new contents.

Hash agreement does not prove that a file is safe, authentic, or unchanged since
some earlier time that was never measured. An attacker could replace a file and
an unprotected baseline together. This lab's scenario includes a fictional
reference anchor for most variants; it is editable local training evidence,
not a digital signature or an independent trust service.

## Command contract

Run these commands from this folder. `lab.py` is the single maintained entry
point. The default `--run` is `run/` beside the script; explicit paths are
relative to your current working directory. The parent of a new run must exist.

| Command | Input and result | Exit codes |
| --- | --- | --- |
| `python lab.py generate` | Creates a new sandbox with `reference/`, `current/`, scenario, approvals, and answer key. Defaults to `mixed`, seed `23`. Refuses an existing run folder, even an empty one. | `0` created; `2` invalid input or existing folder |
| `python lab.py baseline` | Scans `run/reference/` and creates `run/baseline.json`. Does not modify the reference or current files. Refuses an existing output. | `0` created; `2` invalid input or existing output |
| `python lab.py check` | Scans `run/current/`, compares it with the baseline, and applies the supplied exact change approvals. Prints a report without repairing anything. | `0` no unexplained changes and exercise anchor matches; `1` review needed; `2` invalid or unreadable input |
| `python lab.py manifest --verify` | Checks the shipped source and fixture hashes against `PROVENANCE.json`. | `0` match; `1` difference; `2` invalid or unreadable input |

All commands accept `--json` for structured output. Input errors go to standard
error. Use `python lab.py COMMAND --help` for options.

`generate` accepts `--variant approved`, `mixed`, `replacement`, or
`suspect-baseline`, plus `--seed 0` through `999999`. `baseline` accepts
`--source reference` or `--source current` and `--name NAME.json`. `check`
accepts `--baseline NAME.json`. Baseline names must be a single lowercase JSON
file name inside the chosen run; they cannot point outside it.

```console
python lab.py generate
python lab.py baseline
python lab.py check
```

The default check exits `1` deliberately: three changes need investigation.
Read [the worked example](WORKED-EXAMPLE.md), then use [the drills](DRILLS.md)
with unfamiliar inputs. A check result is an evidence classification, not a
learner grade. Explain your reasoning before opening `expected-findings.json`.

## How the report decides

- **Unchanged:** the name, hash, and byte length match the supplied baseline.
- **Approved:** a changed, added, or deleted path matches both hashes in its
  change-list entry. A missing side is recorded as `null` for an addition or
  deletion.
- **Unexpected:** the observed change lacks that exact approval. It needs
  investigation; the output does not call it malicious.
- **Unused approval:** a listed change was not observed exactly. This can mean
  work has not happened yet, the wrong baseline was used, or contents differ
  from the approved version. It is context, not automatically an incident.

The checker independently reports whether the baseline content matches the
scenario's reference anchor. It canonicalises JSON before hashing, so indentation
changes to the inventory do not create an anchor mismatch. Hashes of the actual
dummy files always cover their exact raw bytes. A matching anchor supports only
the supplied exercise history. An absent or mismatched anchor produces exit `1`,
even when no unexpected file differences appear.

| Variant | What changes in the conclusion |
| --- | --- |
| `approved` | The notice edit matches approval; no unexplained changes. |
| `mixed` | The notice is approved; a config edit, an addition, and a deletion are unexplained. |
| `replacement` | The notice and the exact report replacement are approved; additions and deletions are not inherently suspicious. |
| `suspect-baseline` | A prior config change is already in both trees. The comparison sees no config difference, but the baseline has no independent anchor and conflicts with a written requirement. |

A seed changes synthetic labels, counts, ticket IDs, and their hashes. It does
not change the scenario's security reasoning; select another variant for that.

## Files, safety, and limits

`reference/` is a supplied exercise snapshot, and `current/` is the observed dummy
tree. Preserve both while writing your first findings. Only fresh run creation
and new baseline files are written by normal commands. The checker does not
execute files, contact services, delete, quarantine, or restore anything.

The utility is deliberately limited to generated sandboxes with a valid scenario
file and the named `reference/` and `current/` children. It scans actual directory
entries rather than opening paths from a baseline. It rejects path traversal,
absolute baseline entries, Windows device names, uppercase or unsupported file
names, symbolic links, reparse points (including junctions), hard-linked files,
and nonregular files. Bounds are 100 files, 100 directories, eight directory
levels, 1 MB per file, and 10 MB of file content. An empty current tree can be
reported as deletions; an empty baseline is rejected.

This is a small static-tree exercise, not a race-resistant forensic acquisition
tool. Do not change files while a command is running. Permission errors or
unsupported inputs stop the check instead of producing a reassuring partial
report. Metadata such as owner, permissions, timestamps, alternate data streams,
and extended attributes is outside its model. Renames appear as addition and
deletion. The lab cannot determine actor, intent, execution, compromise, or
whether every required file was included in an originally trusted baseline.

Generated files use deterministic UTF-8/LF bytes, and the local `.gitattributes`
preserves LF for shipped files. `PROVENANCE.json` records original synthetic
provenance and hashes of the utility, documentation, tests, and worked fixture.
It does not authenticate its own contents or establish educational acceptance.
`python lab.py manifest --write` creates a missing provenance inventory for a
reviewed release; it refuses to overwrite an existing one. Updating a release
requires deliberate review and replacement of that inventory by a maintainer.

```console
python -m unittest discover -s . -p test_lab.py -v
python lab.py manifest --verify
python lab.py check --run fixtures/worked-example
```

The shipped fixture check exits `1` with the expected mixed-case findings.
The tests cover changed conclusions, exact approvals, poor baselines, removal
of every current file, deterministic bytes, malformed inputs, output protection,
and link/path restrictions. Link creation tests report a skip if the operating
system denies creation; a separate reparse-attribute test always checks rejection.
