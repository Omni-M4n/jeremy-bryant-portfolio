# Linux mode bits and directory traversal

Evaluate a fictional unprivileged user against owner/group/other mode bits and explain why readable files may be unreachable through a directory.

This is an original, fictional, offline exercise for an introductory security learner. It is independent practice, not copied coursework or a claim of professional experience. Completion and competence remain unassessed.

## Before you start

Allow **30-45 minutes**: 5 minutes reading, 10 inspecting and predicting, 10 checking and explaining, and 5-20 for a changed or independent case. You need Python 3.10+ (standard library only), a terminal and a text editor. Comfort opening files, reading a small table and basic evidence notes is enough; programming, administrator rights, a Linux installation and cloud accounts are unnecessary. Previous introductory network or Wireshark practice is useful but not required.

> **Vocabulary:** Owner/group/other: mutually selected permission classes. Octal: base eight, used for the sum 4+2+1. Directory search: permission to resolve names through a directory. ACL: additional access-control entries outside this model. Mode: the ordinary permission bits in this exercise.

## Evidence and exact rules

The case JSON is the single authoritative input. Fixtures are guided.json, changed.json and challenge.json. All data is synthetic; artifacts is empty to avoid competing editable copies. Edit only a prepared run copy. The analyser is a pure calculation and never executes evidence text.

data contains actor name and complete group list, nodes with canonical absolute path/type/owner/group/three-digit octal mode, and requests with ID/path/operation. Supply / and every ancestor directory. Only ordinary file/directory nodes and non-root actors are supported. Special bits, links and missing ancestors are rejected. Nothing reads or changes your operating system.

Select owner bits when the actor owns the node, else group bits when its group is in the actor list, else other bits. Never fall through to a more permissive class. Read=4, write=2, execute/search=1. Every ancestor directory requires search. Target read-file needs 4, write-file 2, execute-file 1, list-dir 4, search-dir 1 and create-entry 3 (write plus search). All required bits and ancestor searches must pass for allowed-by-mode; otherwise denied-by-mode. list-dir means listing names only, not reading file contents or metadata.

## Run the exercise

Open a terminal in this lab folder. Use your Python command (`python`, or `py -3` if that is how Python is installed). Commands below use `python` consistently.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. In run/attempt-01/answers.json, fill each decision with an exact label from the rules; add an explanation and evidence references such as record IDs or configuration line numbers. In notes.txt, separate observation, interpretation, uncertainty, next check and help used. Save your prediction before opening the answer.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

For changed/challenge use the corresponding attempt folder in show/analyse/check. prepare refuses an existing output folder. --out is relative to this lab and must be below run/; explicit input paths are relative to your terminal directory. analyse/show default to the guided fixture if --case is omitted. Exit 0 means command success or decision match; 1 means differences/incomplete written fields; 2 means invalid input or a filesystem problem. The checker verifies decision fields and the presence of writing, not the quality of reasoning. verify checks shipped examples, not learner mastery.

## Deliverable and limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. Deliver a short handover: the question, your conclusion, two precise evidence references, one alternative explanation or limitation, and the next evidence you would request. State whether you used the worked example and whether you completed a fresh case unaided. Do not describe an automated match as assessment or professional experience.

Owner bits take precedence over group, then other; there is no fallback to a more permissive class. Ancestor directories need search (execute) permission. This evaluates ordinary mode bits for an unprivileged synthetic actor only. ACLs, SELinux, capabilities, special bits, symlinks and mount restrictions are not modelled. No host permissions were inspected or changed.

Use WORKED-EXAMPLE.md after making a first prediction, and DRILLS.md for progressively less support. Do not use these rules as an operational security verdict or modify a real host as part of this exercise.

## Primary references

The following documentation supports the underlying concepts; the tiny schema and explicit teaching rules above are specific to this lab. Links were checked during authoring on 23 October 2026. Running the lab needs no internet connection.

- [Linux path resolution manual](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
- [Linux inode and mode manual](https://man7.org/linux/man-pages/man7/inode.7.html)
