# Acquire and register a small evidence set

You copy a club timetable to another folder. A matching fingerprint checks the bytes. A handling note explains which file you copied, when, and what you did next.

**Question:** Can this copy be traced to the recorded source without hiding a handling gap?

This extends `file-integrity`. You make a real file copy, compare hashes and keep a handling register. The register lists who handled the file, when and what they did.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. You need no extra install or paid service. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `file-integrity` first. Allow 25-40 minutes. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **evidence register:** a list of items and where each came from.
- **SHA-256:** a fingerprint calculated from file bytes.
- **custody:** the recorded handling of an item.
- **source:** the item from which a copy was made.

## First attempt and real local operation

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the small local task described below. It saves the results in `receipt.json`.
5. Open the new practical folder, `run/practical-01`. Compare the source and copy hashes in output/register.json. Find the recorded handler and UTC time. Write which fields you observed and which fields are statements entered by the script.
6. Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read WORKED-EXAMPLE.md.

Create two harmless source files and set their read-only flag. Copy their bytes, then hash each source and copy. Save a handling register with UTC times. UTC is a shared time standard. Check the records for changed bytes and gaps in handling. Read-only flags help guard local files. They are not hardware write blockers.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

Each file has an ID and a source label. Its acquisition time records when it was collected, in UTC. It also has a handler alias, three SHA-256 values and a handling log in time order. An alias is a name used for this task. Empty handler/log fields mean records are missing. The model rejects a log time before acquisition. It also rejects a log with times out of order.

Check source change first, then a different copy hash, then missing handler/log fields. A match is reported only after those checks.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `source-changed` | The source hash before and after handling differs. Preserve both records and investigate. |
| `copy-differs` | The source stayed stable but the copied bytes have a different hash. |
| `handling-record-incomplete` | Bytes match but the handler or handling log is absent. |
| `copy-matches-recorded-source` | Bytes match and the required handling fields are present. The log is still a claim requiring review. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

Keep your first `answers.json`, notes, the input `case.json`, the practical `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

There is no service to stop or system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- Matching hashes support byte identity at the recorded checks; they do not prove who created the file or that its contents are true.
- This is a dummy logical-file copy, not disk imaging, a write blocker, or a legal chain-of-custody process.

- Physical device imaging, forensic write blockers, real evidence handling and legal admissibility were not tested.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [NIST SP 800-86, sections 3.1.2 and 4](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf): Evidence handling and bounded forensic interpretation.
- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html): SHA-256 byte hashing API.
- [Python shutil documentation](https://docs.python.org/3/library/shutil.html): copyfile/copy2 behavior and metadata limitations.
