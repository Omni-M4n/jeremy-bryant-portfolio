# Interpret filesystem timestamps and copies

A copied homework file can keep yesterday's modified time. That does not mean the new copy existed yesterday. Compare the bytes and the time fields separately.

**Question:** Did file contents, timestamps, or both change during a recorded operation?

This extends `timeline-analysis`. It adds a real file-copy and timestamp experiment to reading a supplied timeline.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. You need no extra install or paid service. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `timeline-analysis and evidence-custody` first. Allow 25-40 minutes. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **modified time:** the filesystem's recorded content-change time.
- **created time:** when a filesystem records the file as created.
- **access time:** a recorded read time that may be delayed or disabled.
- **nanosecond:** one billionth of a second; a reported unit does not guarantee this precision.

## First attempt and real local operation

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the small local task described below. It saves the results in `receipt.json`.
5. Open the new practical folder, `run/practical-01`. Read output/snapshots.json. Compare SHA-256 first, then mtime_ns. Note that atime was collected before hashing. Record whether birthtime_ns is available. Do not call ctime a creation time on all platforms.
6. Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read WORKED-EXAMPLE.md.

Create a dummy file and set a known modified time. Then use copy2, copyfile, or a controlled write followed by resetting the modified time. Record the actual stat fields and hashes. The stat fields are file details reported by the system. Save birth time only where Python exposes it. Label ctime with the platform, since its meaning can differ.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

Records contain SHA-256 values from before and after. Modified times are whole numbers of nanoseconds since the Unix epoch. That starting point is 1 January 1970 at 00:00:00 UTC. The recorded operation is copyfile, copy2 or write-and-reset-time. These labels name the task. Check the values before you draw a conclusion.

Compare the hashes and modified times independently. Their two true/false comparisons produce the four possible labels.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `content-equal-time-equal` | The two hashes and modified times both match. |
| `content-equal-time-differs` | Hashes match but modified times differ. |
| `content-differs-time-equal` | Hashes differ despite equal modified times. |
| `content-and-time-differ` | Both hashes and modified times differ. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

Keep your first `answers.json`, notes, the input `case.json`, the practical `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

There is no service to stop or system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- File timestamps can be copied or set explicitly; they do not identify a person or prove an action occurred at that exact time.
- Creation/access behavior and timestamp precision vary by operating system and filesystem. ctime is not treated as a portable creation time.

- No universal access-time, birth-time, cross-filesystem or clock-accuracy claim was tested. Only the local filesystem experiment ran.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [Microsoft File Times](https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times): Platform-specific file-time behavior.
- [Python os.stat_result documentation](https://docs.python.org/3/library/os.html#os.stat_result): mtime, birthtime and platform differences.
- [Python shutil documentation](https://docs.python.org/3/library/shutil.html): copyfile/copy2 behavior and metadata limitations.
