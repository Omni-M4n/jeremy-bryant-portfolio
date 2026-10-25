# Offline file integrity and change triage

A made-up community workshop has approved a notice update. Which other files changed? Describe what the evidence shows. Separate explained changes from unexplained ones. Then judge how much you can trust the baseline.

This is new guided practice for a beginner. It uses generated dummy text files and runs offline. You need only Python 3.10 or later. There are no accounts, live systems or executable payloads. There are no extra packages to install. Use commands and explain results. You do not need to write a program.

Independent completion and understanding have not been assessed. The tool, fixtures and supplied key are learning aids. They are not proof of professional experience. They do not show that the learner wrote them without help.

## The security idea

A SHA-256 hash is a short value made from file bytes. Compare it with a value recorded earlier to detect a byte change. A changed hash does not explain why the file changed. An approved edit and an unauthorised edit both alter bytes. Even a change to line endings can alter a hash.

This lab combines three pieces of evidence:

1. A **baseline** records file names, byte lengths and hashes. It describes the time before the change window only if evidence supports that history.
2. A **current inventory** records what is present now.
3. The supplied **change list** records approved paths and exact before/after hashes. A path or ticket number alone does not approve any new content you choose.

Matching hashes do not prove a file is safe or authentic. They say nothing about an earlier time that was never measured. An attacker could replace a file and an unprotected baseline together. Most variants include a fictional **reference anchor**. This is a known value used to check the baseline. It is editable local training evidence. It is not a digital signature or an independent trust service.

## Command contract

Run these commands from this folder. `lab.py` is the single maintained entry point. The default `--run` is `run/` beside the script. Explicit paths start from your current working folder. The parent folder of a new run must exist.

| Command | Input and result | Exit codes |
| --- | --- | --- |
| `python lab.py generate` | Creates a new sandbox with `reference/`, `current/`, scenario, approvals, and answer key. Defaults to `mixed`, seed `23`. Refuses an existing run folder, even an empty one. | `0` created; `2` invalid input or existing folder |
| `python lab.py baseline` | Scans `run/reference/` and creates `run/baseline.json`. Does not modify the reference or current files. Refuses an existing output. | `0` created; `2` invalid input or existing output |
| `python lab.py check` | Scans `run/current/`, compares it with the baseline, and applies the supplied exact change approvals. Prints a report without repairing anything. | `0` no unexplained changes and exercise anchor matches; `1` review needed; `2` invalid or unreadable input |
| `python lab.py manifest --verify` | Checks the shipped source and fixture hashes against `PROVENANCE.json`. | `0` match; `1` difference; `2` invalid or unreadable input |

All commands accept `--json` for structured output. Input errors go to standard error. Use `python lab.py COMMAND --help` for options.

| Command | Options |
| --- | --- |
| `generate` | `--variant approved`, `mixed`, `replacement`, or `suspect-baseline`; `--seed 0` through `999999` |
| `baseline` | `--source reference` or `--source current`; `--name NAME.json` |
| `check` | `--baseline NAME.json` |

A baseline name must be one lowercase JSON file name inside the chosen run. It cannot point outside that run.

```console
python lab.py generate
python lab.py baseline
python lab.py check
```

The default check exits `1` on purpose. Three changes need a closer look. Read [the worked example](WORKED-EXAMPLE.md). Then try [the drills](DRILLS.md) with unfamiliar inputs. A check result sorts evidence; it is not a learner grade. Explain your reasoning before opening `expected-findings.json`.

## How the report decides

- **Unchanged:** the name, hash and byte length match the supplied baseline.
- **Approved:** a changed, added or deleted path matches both hashes in its change-list entry. An addition or deletion has one missing side. That side is recorded as `null`.
- **Unexpected:** the change lacks that exact approval. It needs review. The output does not call it malicious.
- **Unused approval:** a listed change was not seen exactly. The work may not have happened yet. The baseline may be wrong. Or the contents may differ from the approved version. This is context, not automatically an incident.

The checker also compares the baseline content with the scenario's reference anchor. It puts the JSON in a standard form before hashing it. This is called **canonicalisation**. Changing the inventory's indentation will not cause an anchor mismatch. Hashes of the dummy files still cover their exact raw bytes. A matching anchor supports only the supplied exercise history. A missing or mismatched anchor produces exit `1`. This applies even if there are no unexpected file differences.

| Variant | What changes in the conclusion |
| --- | --- |
| `approved` | The notice edit matches approval; no unexplained changes. |
| `mixed` | The notice is approved; a config edit, an addition, and a deletion are unexplained. |
| `replacement` | The notice and the exact report replacement are approved; additions and deletions are not inherently suspicious. |
| `suspect-baseline` | A prior config change is already in both trees. The comparison sees no config difference, but the baseline has no independent anchor and conflicts with a written requirement. |

A seed changes made-up labels, counts, ticket IDs and their hashes. It does not change the scenario's security reasoning. Choose another variant for that.

## Files, safety, and limits

`reference/` is a supplied exercise snapshot. `current/` is the dummy file tree seen now. Keep both intact while writing your first findings. Normal commands write only new runs and new baseline files. The checker does not execute files or contact services. It does not delete, quarantine or restore anything.

The tool works only in its generated sandboxes. A sandbox is a separate set of dummy files for practice. It needs a valid scenario file and the named `reference/` and `current/` children. It scans the entries actually in those folders. It does not open paths taken from a baseline.

| Boundary | Exact rule |
| --- | --- |
| Rejected paths and names | Path traversal; absolute baseline entries; Windows device names; uppercase or unsupported file names |
| Rejected file types | Symbolic links; reparse points, including junctions; hard-linked files; nonregular files |
| Size and depth | At most 100 files, 100 directories, eight directory levels, 1 MB per file and 10 MB of file content |
| Empty current tree | Can be reported as deletions |
| Empty baseline | Rejected |

This exercise checks a small file tree that stays still. It is not a forensic acquisition tool built to resist changes during a scan. Do not change files while a command is running. Permission errors or unsupported inputs stop the check. The tool will not give a reassuring partial report. Renames appear as an addition and a deletion.

| Outside the model | What the lab cannot establish |
| --- | --- |
| Metadata | Owner, permissions, timestamps, alternate data streams and extended attributes |
| Security findings | Actor, intent, execution or compromise |
| Original baseline coverage | Whether it included every required file when first trusted |

Generated files use repeatable UTF-8/LF bytes. The local `.gitattributes` preserves LF for shipped files. `PROVENANCE.json` records the original, made-up source of the material. It hashes the tool, docs, tests and worked fixture. It cannot authenticate its own contents or establish educational acceptance. `python lab.py manifest --write` creates a missing inventory for a reviewed release. It refuses to overwrite an existing one. To update a release, a maintainer must review and replace that inventory.

```console
python -m unittest discover -s . -p test_lab.py -v
python lab.py manifest --verify
python lab.py check --run fixtures/worked-example
```

The shipped fixture check exits `1` with the expected mixed-case findings. The tests cover these points:

| Test area | Coverage |
| --- | --- |
| Findings | Changed conclusions, exact approvals, poor baselines and removal of every current file |
| File handling | Repeatable bytes, malformed inputs, output protection and link/path restrictions |
| Link rejection | Link-creation tests skip if the operating system blocks creation; a separate reparse-attribute test always checks rejection |
