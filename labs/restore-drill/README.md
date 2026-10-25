# Perform and measure a real dummy-data restore

A spare copy of a school project helps only if you can open the right version when needed. Restore into a new folder, then compare every expected file.

**Question:** Does the separate restore meet the recorded file, time and data-age needs?

This extends `backup-verification`. It adds an actual dummy-data restore and measured duration to reviewing supplied backup evidence.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. You need no extra install or paid service. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `backup-verification and file-integrity` first. Allow 25-40 minutes. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **restore:** copy saved data back into a usable location.
- **inventory:** the complete list of expected files.
- **recovery time:** the time taken by the measured restore step.
- **recovery point:** how far back the available saved version goes.

## First attempt and real local operation

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the small local task described below. It saves the results in `receipt.json`.
5. Open the new practical folder, `run/practical-01`. Read output/restore-log.json. Compare every baseline name, size and hash against restored. Compare current_after_change to explain which version was restored. Keep copy_elapsed_ns separate from verification_elapsed_ns. Nanoseconds are the counter unit, not a promise of precise disaster timing.
6. Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read WORKED-EXAMPLE.md.

Create a source folder and make a backup. Change only the dummy current files. Restore the backup into a separate new folder. Check all names you expect and look for extra names too. Do not assume the backup covers every need. Save sorted file lists. Measure and save the time to copy, then the time to check the restored files.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

The expected/restored inventories list a neutral filename, ID, size and SHA-256 for each file. An inventory is a file list. Each ID must be unique within its list. A filename found in both lists must keep the same ID. measured_ms and target_ms are whole numbers. backup_age_minutes and maximum_age_minutes describe the saved version. A time of zero is valid when the timer rounds to a coarse unit.

For each expected filename, check absence before size/hash agreement. Report unexpected names separately. Then compare duration and age independently; equality meets either target.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `file-matches` | Name, size and hash match the expected inventory. |
| `file-missing` | An expected filename is absent. |
| `file-differs` | The filename exists but size or hash differs. |
| `inventory-no-extras` | No unexpected filenames are present; expected files can still be missing. |
| `inventory-has-extra` | At least one unexpected file is present. |
| `within-time-target` | The measured duration is at or below the target. |
| `over-time-target` | The measured duration is above the target. |
| `within-data-age-target` | The backup age is at or below the limit. |
| `older-than-data-age-target` | The available version is older than the limit. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

Keep your first `answers.json`, notes, the input `case.json`, the practical `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

There is no service to stop or system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- A local byte-copy drill does not establish application startup, permissions, cloud availability, full-machine recovery or a disaster recovery time.
- The supplied worksheet times and ages are fictional. The practical receipt separately records actual copy and validation durations.

- Application recovery, OS recovery, cloud backups, real disaster timing and a real recovery-point objective were not exercised.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [Python shutil documentation](https://docs.python.org/3/library/shutil.html): copyfile/copy2 behavior and metadata limitations.
- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html): SHA-256 byte hashing API.
- [NIST SP 800-86, sections 3.1.2 and 4](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf): Evidence handling and bounded forensic interpretation.
