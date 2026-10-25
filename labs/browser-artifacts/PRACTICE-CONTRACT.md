# Maintained local entry point

Read this before changing or running `practice.py`.

- Command: `python practice.py run --scenario guided --out run/practical-01` (also changed/challenge).
- Inputs: choose one of the three supplied cases. The script will not accept your own source, drive, profile, URL or device.
- Output: a new folder directly inside this lab's `run/`. No existing folder is replaced. Read-only dummy sources go in `source/`. Working files go in `output/`. The evidence goes in `receipt.json`.
- Safety: reject paths that escape the allowed folder (traversal). Reject symlinks/reparse paths, which can redirect a path. Reject hard-linked input files, which share stored bytes with another name. Also reject files that are too large and names that are not safe. The script does not install tools, use the network or capture traffic. It does not change host settings or start child processes.
- Operation: Create and close a made-up SQLite database with history, downloads and cache tables. Set it read-only and copy it. Open the copy with mode=ro and run SELECT queries with no parameters. These queries read rows without changing them. Save rows and hashes before and after the checks. The lab documents its own schema, or table layout. It is not the current layout of a real browser.
- Receipt: save the actual times and values from the task. Include source SHA-256 before and after. A matching source hash checks the bytes. It does not check every metadata field, such as a file time.
- Exit: 0 means the task was recorded. A code of 2 means the input was not valid or the task had an error. A training result can be incomplete or contain a conflict. That result is evidence to inspect; it does not mean the script failed.
- Keep first attempts. Remove only the exact attempt folders the script made when you clean up. There are no system changes to undo.
