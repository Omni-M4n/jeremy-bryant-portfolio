# Use shell commands for read-only troubleshooting

Which small command answers your question? What does its output show? Practise paths and quoting, searches, output and errors, services, processes, free space and local listening ports. These cases are made-up command notebooks. The optional live task reads a few things inside a prepared disposable Windows or Linux VM. It does not install tools, change services or scan another machine.

Start with a basic grasp of folders and files. The offline helper needs Python 3.10+. Allow 20-30 minutes per given case and 20-30 minutes for one live task. Linux commands need Bash, GNU grep/coreutils, `ps`, `ss` and systemd in an Ubuntu 22.04/24.04 VM. Windows commands need a Windows VM with PowerShell 7.x and the NetTCPIP module already present. If a tool is missing or access is denied, save the error. Use the given evidence. Do not switch to admin rights just to finish this task.

The **working directory** is where relative paths begin. An **argument** is one value passed to a command. **Quoting** keeps a value together, such as a path with spaces. A **cmdlet** is a command made for PowerShell. A **native program** is a separate program file, such as `grep`. **Stdout** carries its normal output. **Stderr** carries its error messages. An **exit status** is the number a program returns to report its result. A **pipeline** feeds one command's output to another.

A **PID** is a process ID. A **socket** is a program's network connection point. It has an address and port. A **listener** is a socket that waits for connections. A **wildcard binding** listens on all local IPv4 addresses (`0.0.0.0`) or IPv6 addresses (`::`). It does not show whether another computer can connect. PowerShell puts output into separate streams: Success, Error, Warning, Verbose, Debug and Information. Its pipeline normally carries objects. These are values with named fields, such as a process name and ID.

## Supplied notebook

From this lab folder:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the prepared `notebook.txt` and structured `data.records`. For each ID, write the question and actual arguments or fields. Add what they mean, a next read-only check and one limit in `notes.txt`. Fill `answers.json` with labels, a reason and exact record references. Save this first attempt before opening the worked example or answer file.

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python test_lab.py
python lab.py verify
```

The helper only reads the given JSON. It never runs commands from the notebook. `prepare` writes a new ignored folder under `run/`. `check` returns 0 for matching labels with written fields. It returns 1 for differences or missing work, or 2 for bad input. A person must review your reasons and evidence. `verify` compares the three fixtures to fixed answers. It checks the materials, not the learner.

## Exact interpretation rules

The outer case fields follow `../FOUNDATION-CONTRACT.md`. `data.shell` is `bash` or `powershell`. The `records` list holds 1-20 objects with unique IDs. Each has `id`, `kind`, `command` and only the fields for that kind. Commands give context. They are **not parsed or executed**. The case supplies the actual arguments and results. Missing results use the stated `null` fields. Do not invent success values.

| Kind | Fields and decision rule |
|---|---|
| `path` | Fully specified `cwd`, `wanted` and `existing_files`, plus actual `arguments`. More than one path token → `repair-path-quoting`; otherwise the calculated path differs from wanted → `check-working-directory`; wanted is absent from the supplied list → `requested-file-missing`; otherwise `requested-file-resolved`. Windows comparisons ignore letter case and treat `/` and `\` as separators. See the supported forms below. |
| `search` in Bash | Ordinary GNU `grep -F`, no quiet mode: `exit_status` 0 with matches → `matching-lines-observed`; 1 with no matches → `no-matching-lines`; 2 → `search-command-error`, even if partial matches exist. `success` and `last_native_exit` must be null. `stderr` is retained. |
| `search` in PowerShell | `exit_status` is null. Immediately captured boolean `success` represents `$?` for `Select-String`; false → `search-command-error`; true and zero `match_count` → `no-matching-lines`; true with matches → `matching-lines-observed`. `last_native_exit` is retained context and is never used as cmdlet status. |
| `pipeline` | Bash only; `statuses` lists each stage's exit code. With `pipefail` off, the last status is reported. With it on, the rightmost nonzero is reported, or zero if all stages return zero. A contradictory `reported_status` is rejected. Labels: `all-stages-zero`, `earlier-nonzero-hidden`, or `pipeline-nonzero-review-stage`. A nonzero grep 1 can mean no match, not an execution error. |
| `capacity` | `available_bytes - required_bytes` is the margin. Zero or positive → `stated-space-budget-met`; negative → `stated-space-budget-short`. Equality meets this stated byte budget but supplies no reserve. |
| `service` | `query_succeeded` means enough output was obtained to establish the transcribed `state`, not that a native process returned exit 0. States `running`, `stopped`, `not-found` give the corresponding `service-...` label. False with null state → `service-query-inconclusive`. Other combinations are rejected. |
| `process` | Observed `pid` equals the separately supplied `expected_pid` → `process-pid-correlated`; otherwise `process-pid-mismatch`. `name` is context, not proof of identity or intent. |
| `listener` | Wildcard `bind` (`0.0.0.0` or `::`) → `wildcard-listener-review`; loopback with null `owner_pid` → `listener-owner-unresolved`; wrong PID → `listener-pid-mismatch`; matching PID → `loopback-listener-correlated`. Port is 1-65535. |

Windows base paths must include a drive and its root, such as `C:\Lab\run`. Or they must be a full UNC path, such as `\\files.test\practice\run`. **UNC** is the Windows form for a named server and shared folder. This helper only reads the text. It never connects to that path. Both server and share names are needed. Arguments may use those full forms or a plain relative path such as `.\notes with spaces.txt`. The helper rejects `C:notes.txt`, `\notes.txt` and `/notes.txt`. They leave out part of the location. Device paths such as `\\?\C:\...` are outside this task. These fixed rules do not use Python's Windows `isabs()` test, which can vary by version.

The notebook's made-up `LabDemo` / `lab-demo.service` is not a service to create. The notebook paths are made up too. The small text samples in this package are under `samples/`. The hyphenated text files made by `prepare` are separate evidence copies. The helper does not check links, permissions, live processes, network access or how a real shell reads commands. It does not expand wildcard patterns such as `*.txt`.

## Live lane A: Linux Bash in the disposable VM

Open a normal user terminal in **this lab folder inside the VM**. Run each command on its own. Check failures before going on. Read local help first: `help pwd`, `help printf`, `grep --help`, `df --help`, `ps --help`, `ss --help`, `systemctl --help`. Keep a short notebook outside the VM if you plan to restore it later.

1. Confirm location and read one exact spaced path. These sample files contain only fictional words.

```bash
pwd
ls -l -- './samples/notes with spaces.txt'
cat -- './samples/notes with spaces.txt'
```

Predict why unquoted `./samples/notes with spaces.txt` would become several arguments. An error alone does not mean “file absent”. First check the current folder and where each argument begins and ends.

2. Read the sample using literal patterns and capture the outcome immediately:

```bash
grep -F 'WAITING' './samples/notes with spaces.txt'
printf 'grep exit=%s\n' "$?"
grep -F 'READY' './samples/notes with spaces.txt'
printf 'grep exit=%s\n' "$?"
grep -F 'READY' './samples/does-not-exist.txt'
printf 'grep exit=%s\n' "$?"
```

Expect a matching line and 0, no selected line and 1, then a missing-file error and 2. The wording can vary. If the supposedly missing file exists, stop and choose an unused sample filename. The error is stderr. It is not a selected line. Record the output and code together. Another command replaces `$?`.

3. Check a pipeline's status without changing your shell's options. A subshell is a temporary child shell. This one turns `pipefail` off for this small task. It prints both statuses in the next command:

```bash
(set +o pipefail; grep -F 'READY' './samples/notes with spaces.txt' | head -n 1; printf 'pipeline=%s stages=%s\n' "$?" "${PIPESTATUS[*]}")
```

Expect overall 0 and stage statuses `1 0`. The first program found no match. The final program ran successfully. Read each status using that program's rules. “The pipeline succeeded” does not describe both stages.

4. Ask four bounded system questions. These commands only inspect the guest:

```bash
ps -p "$$" -o pid,ppid,comm
df -B1 --output=avail .
systemctl show --property=LoadState,ActiveState -- cron.service
ss -ltnp 'sport = :8765'
```

The first shows your shell process and its parent. Compare the PID with `printf '%s\n' "$$"`. The second gives the free bytes on the file system for the current folder. Compare that with a written 1,048,576-byte practice budget. Do not create a large file. The third asks whether this one known unit is loaded and active. `LoadState=not-found` differs from a loaded but inactive service. A systemd or permission error leaves the query unresolved. The fourth looks for a local TCP listener on one port. A header with no row means none was shown at that instant. Missing process details limit what you can see. They do not prove a hidden attacker exists. Do not start or stop services to force a result.

To practise separating streams, first prepare a fresh offline attempt. Use two **new** filenames under its `run/` folder for one missing-file grep: `1> run/attempt-01/output-01.txt 2> run/attempt-01/error-01.txt`. Check both paths and make sure the files do not exist. The `>` sign overwrites. The query only reads state. Redirection writes your named evidence files. Record the exit code at once, then read both files. Close the terminal when done and keep the notebook. No system state needs to be restored.

## Live lane B: Windows PowerShell in the disposable VM

Open PowerShell 7 in this lab folder. Read the local help: `Get-Help Get-Content`, `Get-Help Select-String`, `Get-Help Get-Service`, `Get-Help Get-Process` and `Get-Help Get-NetTCPConnection`. Do not update help or install modules. Record `$PSVersionTable.PSVersion`.

```powershell
Get-Location
Get-Item -LiteralPath '.\samples\notes with spaces.txt'
Get-Content -LiteralPath '.\samples\notes with spaces.txt'
Select-String -LiteralPath '.\samples\notes with spaces.txt' -SimpleMatch 'READY'
$cmdletSucceeded = $?
$cmdletSucceeded
```

Expect no matching line and `$cmdletSucceeded` true. `-LiteralPath` stops wildcard matching. Quotes keep the spaced path together. `$LASTEXITCODE` is for a native program or script that sets it. It may still hold an earlier value. It does not replace the `$?` value saved at once for this cmdlet.

```powershell
Get-Content -LiteralPath '.\samples\does-not-exist.txt' -ErrorAction Continue
$cmdletSucceeded = $?
$cmdletSucceeded
Get-Process -Id $PID | Select-Object Id, ProcessName
Get-PSDrive -Name C | Select-Object Name, Used, Free
Get-Service -Name Spooler | Select-Object Name, Status
Get-NetTCPConnection -State Listen -LocalPort 8765 | Select-Object LocalAddress, LocalPort, OwningProcess
```

Expect an error for the missing-file read and a saved success value of false. The other results depend on the VM. Find your current process. Compare free bytes with the same written budget. Inspect one service and one listening port. A missing service, no matching socket and access denied mean different things. Do not change the execution policy, permissions, firewall, services or other settings. If needed, look up one returned PID with `Get-Process -Id <observed-PID>`. Replace the placeholder with the number you saw. A process can end and its PID can be reused. If that happens, collect fresh evidence from the same time.

To separate streams, use a new prepared attempt and filenames that do not exist. On the missing-file read, use a form such as `1> .\run\attempt-01\output-01.txt 2> .\run\attempt-01\error-01.txt`. Save `$?` on the very next line. Keep the two files separate and readable. The PowerShell version matters for native binary output. This task uses only text cmdlets. Close the terminal when done. No service or host setting needs to be restored.

## Evidence, limitations and handover

Save the exact shell and version, current folder, chosen command and help reference. Keep output, error text, the status saved at once, time, meaning, next check and help used. Include one positive result and one expected empty or error case. A reviewer should be able to explain why each command was chosen. The evidence should support a precise claim, not just “working” or “malicious.”

The live tasks are instructions. They were not run on a Windows or Linux guest while making this package. Passing Python tests checks only the offline rules. A free-space reading does not account for quotas or later writes. A process name can mislead. A stopped service may be meant to stay stopped. A wildcard binding does not prove remote access is allowed. Keep failed attempts. Explain why “not observed” differs from “not present.”

Handover prompt: “Question __; shell/version __; directory __; command __; output/status evidence __; supported conclusion __; smallest next read-only check __; unresolved limitation __.”

## Primary documentation

Opened 2026-10-25; retrieval details are in `SOURCES.json`.

- [GNU grep exit status](https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html): ordinary search outcomes and the quiet-mode exception excluded here.
- [GNU Bash pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html): last-command status and `pipefail` behavior.
- [PowerShell automatic variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables?view=powershell-7.5): `$?`, `$LASTEXITCODE` and `$PID`.
- [PowerShell redirection](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_redirection?view=powershell-7.5): separate streams, overwrite behavior and version-sensitive native output.
