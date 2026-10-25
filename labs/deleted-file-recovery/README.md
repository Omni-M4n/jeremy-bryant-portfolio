# Recover a deleted dummy file from a disposable image

Crossing a name off a list does not always rub out the words on the page. A deleted directory entry can leave data behind. The old data may also have been overwritten.

**Question:** Does a candidate recovered from this generated image match the known training file?

This beginner lab uses made-up data written for this task.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. You need no extra install or paid service. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `evidence-custody, file-type-triage and isolated-lab-workbench` first. Allow 25-40 minutes. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **image:** a file holding the bytes of a pretend disk.
- **FAT12:** a simple filesystem that uses a table to track blocks assigned to files.
- **cluster:** a block of storage assigned to file data.
- **recovery candidate:** bytes found at a possible old file location.

## First attempt and real local operation

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the small local task described below. It saves the results in `receipt.json`.
5. Open the new practical folder, `run/practical-01`. Read output/recovery-log.json. The generated layout has 512-byte sectors, two one-sector FAT copies, a root directory at byte 1536, and data at byte 2048. A first directory byte e5 marks the deleted entry. Compare the separately extracted item-01.bin with the known training hash.
6. Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read WORKED-EXAMPLE.md.

Build a real FAT12 byte layout in memory. Write it only to a new ordinary image file under run/. Mark a training entry deleted and clear its allocation entry. This marks its storage block as free. Reopen the image read-only and read the directory entry. Copy candidate bytes into a separate output folder. Never mount the image or supply a drive/device path.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

The recorded entry has an ID, directory_present flag and cluster_allocated flag. It also has declared_size, candidate bytes and the known training hash. A missing entry must have zero size, no candidate bytes and no allocated cluster. To compare a file, the cluster must be free and the file must be 1-512 bytes long.

Check directory absence first, then allocation and size support, then candidate length, then the known-file hash. An absent entry cannot also supply candidate bytes.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `no-directory-candidate` | The supplied directory entry is absent; no candidate is selected. |
| `outside-recovery-model` | The cluster is allocated or the file is longer than one cluster. |
| `candidate-size-differs` | The byte count does not equal the directory size. |
| `candidate-content-differs` | Length matches but the known training hash does not. |
| `matches-known-training-file` | Candidate length and SHA-256 match the known training file. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

Keep your first `answers.json`, notes, the input `case.json`, the practical `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

There is no service to stop or system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- This parser accepts only the generated 32 KiB FAT12 layout and one-cluster deleted entries. It is not a general recovery tool.
- A known-file hash match checks this training file. Missing entries or different bytes do not establish that all old data is gone or why it changed.

- Mounting the image in an OS, recovery suites, fragmented files, physical disks, TRIM and damaged media were not tested.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [Linux FAT structures and constants](https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/msdos_fs.h): Directory layout, allocation constants and deleted-entry marker.
- [Linux FAT directory implementation](https://raw.githubusercontent.com/torvalds/linux/master/fs/fat/dir.c): Directory deletion behavior; source consulted, no code copied.
- [NIST SP 800-86, sections 3.1.2 and 4](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf): Evidence handling and bounded forensic interpretation.
