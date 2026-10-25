# Reconstruct a benign browsing session from a lab database

A library borrowing record says a book was checked out. It does not prove who read it. Browser records have a similar limit: they record stored events, not a person's attention.

**Question:** Which history, download and cache records can be linked in this fictional session?

This beginner lab uses made-up data written for this task.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. You need no extra install or paid service. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `timeline-analysis and evidence-custody` first. Allow 25-40 minutes. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **SQLite:** a database stored in a file.
- **history:** stored page-visit records.
- **cache:** stored copies used to load content again.
- **session:** a label grouping records in this exercise.

## First attempt and real local operation

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the small local task described below. It saves the results in `receipt.json`.
5. Open the new practical folder, `run/practical-01`. Read output/timeline.json. Match URL and session before checking the time gap. The SQLite tables store explicit UTC text. A complete download record is not proof that the downloaded file still exists on disk.
6. Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read WORKED-EXAMPLE.md.

Create and close a made-up SQLite database with history, downloads and cache tables. Set it read-only and copy it. Open the copy with mode=ro and run SELECT queries with no parameters. These queries read rows without changing them. Save rows and hashes before and after the checks. The lab documents its own schema, or table layout. It is not the current layout of a real browser.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

Each event has an ID and kind (history/download/cache). It has a UTC time, reserved .test URL, session ID and state. UTC is a shared time standard. It also has counts for received and expected bytes. History/cache use state recorded and zero counts. A download marked complete must have equal counts. To link records, the URL and session must match. The history event must be at or before the other record, with a gap of no more than 60 seconds.

Validate all records first. History has its own label. Cache uses the link rule. A download must have state complete and equal byte counts before it can receive a complete label.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `history-record` | A stored history entry; no personal attribution. |
| `download-complete-linked` | Recorded complete byte counts plus a matching nearby history entry. |
| `download-complete-unlinked` | Recorded complete byte counts with no history entry meeting the link rule. |
| `download-incomplete` | The download state is interrupted or in-progress. |
| `cache-linked` | Cache record meets the narrow history link rule. |
| `cache-without-linked-history` | No history entry meets the link rule; this does not establish no visit. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

Keep your first `answers.json`, notes, the input `case.json`, the practical `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

There is no service to stop or system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- This is a fictional SQLite schema with explicit UTC times, not a Chrome/Firefox profile parser. No real browser history is read.
- Records do not identify the person at the keyboard or prove page attention. Missing history can reflect deletion, private browsing, collection gaps or no visit.

- Real browsers, real profiles, live database/WAL acquisition, incognito inspection and browser-specific timestamp conversion were not run.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [SQLite URI filenames](https://www.sqlite.org/uri.html): Read-only mode=ro database opening.
- [SQLite database file format](https://www.sqlite.org/fileformat.html): Database signature and journal/WAL context.
- [Google Chrome Incognito documentation](https://support.google.com/chrome/answer/95464?hl=en): Limits on retained history and persistent downloaded files.
