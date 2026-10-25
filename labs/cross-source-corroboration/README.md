# Resolve a disagreement between evidence sources

Two clocks can disagree by two minutes. Two receipts at similar times can also describe different purchases. Check a shared receipt number and the clock error before joining the records.

**Question:** Which proposed event links survive identifier, content and clock checks?

This extends `timeline-analysis, http-triage and endpoint-triage`. It adds source comparison and explicit clock correction to the earlier timeline and event exercises.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. You need no extra install or paid service. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `evidence-custody, file-time-analysis and logging-health` first. Allow 25-40 minutes. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **corroboration:** support from another source.
- **clock error:** how far a clock is ahead of or behind the reference.
- **uncertainty:** a stated range in which a time may fall.
- **identifier:** a label used to link records, which may be missing or reused.

## First attempt and real local operation

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the small local task described below. It saves the results in `receipt.json`.
5. Open the new practical folder, `run/practical-01`. Read output/timeline.csv. Keep observed_utc and corrected_utc side by side. A positive clock error means the source clock was ahead, so subtract it. A blank correction means unknown, not zero. Check collection notes when discussing reliability.
6. Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read WORKED-EXAMPLE.md.

Copy the made-up source records into a fresh evidence folder. Hash the input. Write a CSV timeline with original and corrected UTC times and the stated uncertainty. UTC is a shared time standard. Keep the original records and any values that conflict. This task compares evidence. It does not act on a real system.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

Each source gives an ID, kind (host, web or packet) and short collection note. It also gives clock_error_seconds and uncertainty_seconds. Clock error is observed time minus reference time, or null when unknown. Each record gives its source, UTC time, request ID or null, and object SHA-256. A pair names two different records from different sources. Corrected time = observed minus clock error. Time intervals are the ranges allowed by the stated uncertainty. They are compatible when they touch or overlap.

Check present request IDs that differ first. Then check different content hashes, missing IDs, unknown clock errors and time bounds that do not overlap, in that order. Keep every observation even when the first matching rule ends the check.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

Every observed time must fall within UTC years 0001-9999. Every time after a supplied clock correction must stay in that range too. The model rejects a correction outside it, even for an unpaired record. Unknown clock errors remain unresolved.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `identifiers-conflict` | Two present request IDs differ. |
| `content-conflict` | The recorded object hashes differ. |
| `insufficient-link` | At least one request ID is missing; time alone is insufficient. |
| `clock-unresolved` | IDs/content agree but at least one clock error is unknown. |
| `time-conflict` | Corrected uncertainty intervals do not overlap. |
| `link-supported-within-clock-bounds` | Request IDs and content hashes agree and corrected intervals overlap. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

Keep your first `answers.json`, notes, the input `case.json`, the practical `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

There is no service to stop or system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- A shared ID and compatible time interval support a link within this fictional model; IDs and logs can be reused, copied or wrong.
- Clock correction is supplied evidence, not a fitted value chosen to force agreement. Timing alone does not identify a person or establish causation.

- No real endpoint, web server or packet logs were acquired. Clock errors are supplied training measurements rather than live synchronization tests.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [RFC 3339, timestamps](https://www.rfc-editor.org/rfc/rfc3339.html): Explicit UTC date-time representation.
- [NIST SP 800-86, sections 3.1.2 and 4](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf): Evidence handling and bounded forensic interpretation.
- [Microsoft File Times](https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times): Platform-specific file-time behavior.
