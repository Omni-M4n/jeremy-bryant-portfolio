# Inventory more than scheduled tasks

A note opens when a user signs in. A timer runs as a service. Both can start on
their own, but they use different places and accounts. Compare what was approved
with what is there now. Check changes to old entries as well as new ones.

This extends [scheduled-task-review](../scheduled-task-review/README.md). It adds
Windows services, the Startup folder, Run keys and Linux service units. The new
evidence is the owner, account that runs it, command, file hash and exact approval
for a change.
Start with that lab, [endpoint-triage](../endpoint-triage/README.md), and
[isolated-lab-workbench](../isolated-lab-workbench/README.md).

> **Words:** Startup means launch at boot or sign-in. A mechanism is the place
> that launches it. Identity is the account used to run it. Owner here means the
> account that owns the launch file or setting. A digest, or hash, is a fingerprint
> of bytes.

## Run the evidence cases

Use Python 3.10+ and a text editor. Allow 25-40 minutes. Start in this lab folder.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Save predictions in `answers.json`, using the exact labels below. Add reasons
and record IDs in `explanation` and `evidence`. Keep your first attempt and record
help used in `notes.txt` before viewing the analysis.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

The helper reads made-up JSON cases only. It does not run the text found in
evidence or change settings. Unknown fields, repeated IDs and values outside the
rules are errors. A person must assess your reasons. Matching labels do not prove skill.

## Exact offline rules

Each of `baseline`, `observed` and `approvals` is a list. Records contain neutral
IDs plus `mechanism`, `command`, `identity`, `owner`, and a full lowercase `sha256`.
Supported mechanisms are `windows-service`, `startup-folder`, `run-key` and
`systemd-unit`. Hashes are made up. For files, they refer to the file being launched.
For a unit or registry record, save a text export in the same way for both
snapshots. Compare that export's hash. Never compare a binary file's hash with
the hash of a text export of settings.

The command, identity and owner must each be one printable line, at most 200
characters. Spaces inside a value are allowed. Leading or trailing spaces,
line breaks, tabs, NUL and other hidden control characters are refused.

Assume that the baseline is approved for this case. Compare all five fields
exactly. An unchanged record is `matches-baseline`. A new record is
`approved-addition` only if its approval lists the same ID and all observed
fields. Otherwise, it is `unexplained-addition`. For an old record that changed,
use the same test to choose `approved-change` or `unexplained-change`. A baseline
record that is now missing gets `missing-follow-up`. It needs a check even if
someone may have had good reason to remove it. An approval for a missing or
different observed record is an error. No result proves malware or tells you to remove an entry.

## VM practice: inspect startup sources

Use a **new disposable Windows 11 VM** and, for the Linux part, a **new disposable
Debian VM with systemd already installed**. Take clean snapshots. Keep both
original VMs and the host untouched. Network access is not needed. These platform
steps have not been run for this package. Allow 30-45 minutes per platform.

In Windows PowerShell, read these locations:

```powershell
Get-CimInstance Win32_Service | Select-Object Name,StartMode,StartName,PathName
Get-ChildItem -LiteralPath ([Environment]::GetFolderPath('Startup'))
Get-ChildItem -LiteralPath ([Environment]::GetFolderPath('CommonStartup'))
Get-ItemProperty -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue
Get-ItemProperty -LiteralPath 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue
```

A missing registry key is evidence, not a command failure to hide. Pick one
service and one Startup entry, if present. Record the account, full launch command
and file owner. For a chosen file use `Get-Acl -LiteralPath 'EXACT-FILE'` and
`Get-FileHash -LiteralPath 'EXACT-FILE' -Algorithm SHA256`, replacing `EXACT-FILE`
with its verified path. Do not execute an unexplained command to see what it does.

For a harmless new Startup entry, use a fresh standard account in that new VM.
Stop if its `lesson-signin.txt` temp note already exists. The following creates a
new launch file only if the name is unused:

```powershell
$startup = [Environment]::GetFolderPath('Startup')
$lesson = Join-Path $startup 'lesson-note.cmd'
if (Test-Path -LiteralPath $lesson) { throw 'Name already exists; stop.' }
if (Test-Path -LiteralPath (Join-Path $env:TEMP 'lesson-signin.txt')) { throw 'Note exists; stop.' }
'@echo off', 'echo lesson sign-in>>"%TEMP%\lesson-signin.txt"' | Set-Content -LiteralPath $lesson -Encoding ascii
Get-FileHash -LiteralPath $lesson -Algorithm SHA256
Get-Acl -LiteralPath $lesson | Format-List Owner,AccessToString
```

Record the approved exact command, owner and hash. Sign out and back into that
VM account. Run `Get-Content -LiteralPath (Join-Path $env:TEMP 'lesson-signin.txt')`.
Confirm a new line appeared after sign-in. Do not infer exact launch time from
the file alone. Export redacted notes, then revert the snapshot to clean up.

On Debian, inspect units without creating or enabling anything:

```sh
systemctl list-unit-files --type=service
systemctl list-units --type=service --all
systemctl show systemd-journald.service -p User -p FragmentPath -p ExecStart -p ActiveState
systemctl cat systemd-journald.service
```

Record the main unit file's fragment path and any extra drop-in paths from `cat`.
Use `stat -- 'EXACT-PATH'` and `sha256sum -- 'EXACT-PATH'` for each actual file.
A missing `User=` on a system service means the default is root. This read-only
list does not prove that every service starts at boot. Check whether it is
enabled, what triggers it and which other units it needs. Keep the two lists
separate. Export notes, then revert the disposable VM.

## Hand over and limits

Give a reviewer one unchanged entry, one approved change and one unexplained item
from the made-up cases. Add the VM results you actually saw. Include scope and
dates. An entry may be missing because it was removed or because the check missed
it. Approval can be wrong. Hashes only compare bytes. This small list cannot
cover every startup route or prove that a computer has no malware.

## Primary sources opened for this lesson

- [Microsoft: Run and RunOnce](https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys) — sign-in launch behavior and timing limits.
- [systemd: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) — unit files versus loaded units.
- [systemd: execution settings](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html) — service execution accounts.
