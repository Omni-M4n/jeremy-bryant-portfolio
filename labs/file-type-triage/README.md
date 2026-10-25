# Identify file types beyond the extension

A lunch box may have the wrong label. A file named photo.png can also have the wrong label. Look at its first bytes without opening it as a program.

**Question:** What can a file header tell us when its filename and metadata disagree?

This beginner lab uses made-up data written for this task.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. You need no extra install or paid service. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `file-integrity and shell-troubleshooting` first. Allow 25-40 minutes. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **extension:** the ending of a filename, such as .png.
- **signature:** a known sequence of starting bytes.
- **hexadecimal:** a short way to write bytes using 0-9 and a-f.
- **metadata:** details about a file, such as its type label. These can be wrong.
- **prefix/header:** the bytes at the start of a file.
- **MIME label:** a reported content type. It is a label to check, not proof.

## First attempt and real local operation

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the small local task described below. It saves the results in `receipt.json`.
5. Open the new practical folder, `run/practical-01`. Read output/observations.json. Convert the first eight PNG bytes to 89 50 4e 47 0d 0a 1a 0a. For a database, compare all 16 signature bytes. Do not double-click unknown files.
6. Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read WORKED-EXAMPLE.md.

Create a small set of harmless PNG bytes, a tiny made-up SQLite database, plain text or short byte samples. Hash each file. Inspect only its prefix (starting bytes) and size. Do not run any sample as a program. Decide whether the starting bytes match either of the two supported signatures.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

Each record gives an ID, neutral filename, total size and reported MIME label. It also gives the first up to 16 bytes as lowercase hex. The model keeps the label but does not trust it as a signature. Prefix length must equal min(size,16): use all bytes if the file is shorter than 16 bytes. Otherwise use the first 16.

Check zero length first, then a complete PNG signature, then a complete SQLite signature. Otherwise leave the type undetermined. The reported MIME label never overrides bytes.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `empty-file` | Zero bytes give no format evidence. |
| `type-undetermined` | Neither supported complete signature is present. |
| `png-signature-extension-agrees` | PNG starting bytes and .png agree; whole-file validity remains unchecked. |
| `png-signature-extension-differs` | PNG starting bytes and the filename ending disagree. |
| `sqlite-signature-extension-agrees` | SQLite starting bytes and .db/.sqlite/.sqlite3 agree. |
| `sqlite-signature-extension-differs` | SQLite starting bytes and the filename ending disagree. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

Keep your first `answers.json`, notes, the input `case.json`, the practical `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

There is no service to stop or system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- A matching signature is a format clue, not proof that the whole file is valid or safe.
- An extension mismatch alone does not establish malware. Only PNG and SQLite signatures are recognized here.

- No antivirus, full format validator, executable analysis, or unknown user file was run.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [W3C PNG specification, file signature](https://www.w3.org/TR/png/): PNG signature bytes; a header is not full validation.
- [SQLite database file format](https://www.sqlite.org/fileformat.html): Database signature and journal/WAL context.
- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html): SHA-256 byte hashing API.
