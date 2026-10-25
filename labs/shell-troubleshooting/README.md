# Use shell commands for read-only troubleshooting

Which small command answers your question, and what does its output actually show? Practise paths and quoting, search results, output and errors, services, processes, free space and local listening ports. The supplied cases are fictional command notebooks. The optional live lane gathers a few observations inside an already prepared disposable Windows or Linux VM; it does not install tools, change services or scan another machine.

Prerequisites: basic folders/files and Python 3.10+ for the offline helper. Allow 20-30 minutes per supplied case and 20-30 minutes for one live lane. Linux commands assume Bash, GNU grep/coreutils, `ps`, `ss` and systemd in an Ubuntu 22.04/24.04 VM. Windows commands assume a Windows VM with PowerShell 7.x and the existing NetTCPIP module. If a tool is missing or permissions prevent a query, preserve the error and use the supplied evidence. Do not elevate merely to complete this exercise.

**Vocabulary:** working directory = where relative paths begin; argument = one value passed to a command; quoting = keeping a value such as a spaced path together. A **cmdlet** is a command made for PowerShell. A **native program** is a separate executable file, such as `grep`. **Stdout** carries its ordinary output; **stderr** carries its error messages. An **exit status** is the number a program returns to report its result. A **pipeline** feeds one command's output to another.

A **PID** is a process ID. A **socket** is a program's network connection point, with an address and port. A **listener** is a socket waiting for connections. A **wildcard binding** listens on all local IPv4 addresses (`0.0.0.0`) or IPv6 addresses (`::`). It does not show whether another computer can connect. PowerShell separates Success, Error, Warning, Verbose, Debug and Information output into streams. Its pipeline normally carries objects: values with named fields, such as a process name and ID.

## Supplied notebook

From this lab folder:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the prepared `notebook.txt` and structured `data.records`. For each ID, record the question, actual arguments/fields, interpretation, next read-only check and one limitation in `notes.txt`. Fill `answers.json` with decision labels, an explanation and exact record references. Preserve this first attempt before opening the worked example or reference.

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python test_lab.py
python lab.py verify
```

The helper reads supplied JSON only; it never runs commands from the notebook. `prepare` writes a fresh ignored folder under `run/`. `check` returns 0 for matching labels with written fields, 1 for differences/incomplete work, or 2 for malformed input. A human reviews whether the explanation and evidence are sound. `verify` compares the three fixtures to explicitly authored references; it is a material check, not learner assessment.

## Exact interpretation rules

The case envelope follows `../FOUNDATION-CONTRACT.md`. `data.shell` is `bash` or `powershell`; `records` contains 1-20 uniquely identified objects. Each has `id`, `kind`, `command` and only the fields for that kind. Commands are readable context, **not parsed or executed**. Actual arguments and observations are supplied explicitly. Missing observations use the documented `null` fields, not invented success values.

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

Windows base paths must include a drive and its root, such as `C:\Lab\run`, or a complete UNC path, such as `\\files.test\practice\run`. **UNC** is the Windows form for a named server and shared folder; this helper reads the text only and never connects to it. Both server and share names are required. Arguments may use those full forms or a plain relative path such as `.\notes with spaces.txt`. The helper rejects `C:notes.txt`, `\notes.txt` and `/notes.txt` because they leave out part of the location. Device paths such as `\\?\C:\...` are outside this exercise. These rules are explicit and do not use Python's version-dependent Windows `isabs()` test.

The supplied notebook's fictional `LabDemo` / `lab-demo.service` is not a service you should create. Paths in the notebook are fictional. The repository's small text samples are under `samples/`; the hyphenated text files made by `prepare` are separate evidence copies. The helper does not check links, permissions, live processes, network access or actual shell parsing. It does not expand wildcard patterns such as `*.txt`.

## Live lane A: Linux Bash in the disposable VM

Open a normal user terminal in **this lab folder inside the VM**. Run each command separately; inspect failures before continuing. Use local help first: `help pwd`, `help printf`, `grep --help`, `df --help`, `ps --help`, `ss --help`, `systemctl --help`. Keep a short notebook outside the VM if it will later be restored.

1. Confirm location and read one exact spaced path. These sample files contain only fictional words.

```bash
pwd
ls -l -- './samples/notes with spaces.txt'
cat -- './samples/notes with spaces.txt'
```

Predict why unquoted `./samples/notes with spaces.txt` would become several arguments. Do not infer “file absent” from an error until you have checked the actual current directory and argument boundary.

2. Read the sample using literal patterns and capture the outcome immediately:

```bash
grep -F 'WAITING' './samples/notes with spaces.txt'
printf 'grep exit=%s\n' "$?"
grep -F 'READY' './samples/notes with spaces.txt'
printf 'grep exit=%s\n' "$?"
grep -F 'READY' './samples/does-not-exist.txt'
printf 'grep exit=%s\n' "$?"
```

Expect a matching line and 0, no selected line and 1, then a missing-file diagnostic and 2. Output wording can vary. If the supposedly missing file exists, stop and choose an unused sample filename. The diagnostic is stderr, not a selected line. Record the output and code together; another command replaces `$?`.

3. Examine a pipeline's status without changing shell options. This subshell uses `pipefail` off only for the small exercise and prints both statuses in the next command:

```bash
(set +o pipefail; grep -F 'READY' './samples/notes with spaces.txt' | head -n 1; printf 'pipeline=%s stages=%s\n' "$?" "${PIPESTATUS[*]}")
```

Expect overall 0 and stage statuses `1 0`. The first program found no match; the final program ran successfully. Interpret each status using its own program's contract. This is why “the pipeline succeeded” is too broad.

4. Ask four bounded system questions. These commands only inspect the guest:

```bash
ps -p "$$" -o pid,ppid,comm
df -B1 --output=avail .
systemctl show --property=LoadState,ActiveState -- cron.service
ss -ltnp 'sport = :8765'
```

The first shows your shell process and parent; compare the PID with `printf '%s\n' "$$"`. The second reports available bytes on the filesystem holding the current folder; compare it with a written 1,048,576-byte practice budget without creating a large file. The third asks whether this one known unit is loaded and active; `LoadState=not-found` differs from a loaded but inactive service. A systemd/permission error is an inconclusive query. The fourth looks for a local TCP listener on one chosen port. A header with no row means no matching listener was shown at that instant. Missing process details are a visibility limit, not evidence of a hidden attacker. Do not start or stop services to force an expected result.

To practise separating streams, prepare a fresh offline attempt first and use two **new** filenames under its `run/` folder for one missing-file grep: `1> run/attempt-01/output-01.txt 2> run/attempt-01/error-01.txt`. Check the paths and absence of existing files before redirection; `>` overwrites. The query stays read-only, while redirection writes only your named evidence files. Immediately record the exit code, then inspect both files. Cleanup is closing the terminal and retaining the notebook; no system rollback is needed.

## Live lane B: Windows PowerShell in the disposable VM

Open PowerShell 7 in this lab folder. Use `Get-Help Get-Content`, `Get-Help Select-String`, `Get-Help Get-Service`, `Get-Help Get-Process` and `Get-Help Get-NetTCPConnection` locally; do not run help updates or install modules. Record `$PSVersionTable.PSVersion`.

```powershell
Get-Location
Get-Item -LiteralPath '.\samples\notes with spaces.txt'
Get-Content -LiteralPath '.\samples\notes with spaces.txt'
Select-String -LiteralPath '.\samples\notes with spaces.txt' -SimpleMatch 'READY'
$cmdletSucceeded = $?
$cmdletSucceeded
```

Expect no matching line and `$cmdletSucceeded` true. `-LiteralPath` prevents wildcard interpretation; quotes keep the spaced path together. `$LASTEXITCODE` is for a native program or script that sets it, and may still hold an earlier value. It does not replace the immediately captured `$?` for this cmdlet.

```powershell
Get-Content -LiteralPath '.\samples\does-not-exist.txt' -ErrorAction Continue
$cmdletSucceeded = $?
$cmdletSucceeded
Get-Process -Id $PID | Select-Object Id, ProcessName
Get-PSDrive -Name C | Select-Object Name, Used, Free
Get-Service -Name Spooler | Select-Object Name, Status
Get-NetTCPConnection -State Listen -LocalPort 8765 | Select-Object LocalAddress, LocalPort, OwningProcess
```

Expect the missing-file read to report an error and captured success false. The remaining results depend on the VM: identify your current process, compare free bytes against the same written budget, inspect one service, and inspect one listening port. Missing service, no matching socket, and access denied are distinct observations. Do not change the execution policy, permissions, firewall, service state or other system settings. If needed, look up one returned PID using `Get-Process -Id <observed-PID>` after substituting the observed number; a reused or vanished PID requires fresh time-correlated evidence.

To separate evidence streams, use a prepared new attempt and nonexisting names such as `1> .\run\attempt-01\output-01.txt 2> .\run\attempt-01\error-01.txt` on the missing-file read. Capture `$?` on the immediately following line. Keep the stream files separate and readable. For native binary output, PowerShell version matters; this exercise uses text cmdlets only. Close the terminal when finished. No service or host rollback is required.

## Evidence, limitations and handover

Save the exact shell/version, current directory, selected command and help reference, output/error text, immediately captured status, timestamp, interpretation, next check and help used. Include one positive result and one expected empty/error case. A reviewer should be able to explain why each command was chosen and why the resulting observation is narrower than “working” or “malicious.”

The live lanes are instructions and have not been executed on a Windows or Linux guest during package creation. Passing the Python tests establishes only the offline rules. A free-space reading does not account for quotas or later writes; a process name can be misleading; a service being stopped may be intentional; a wildcard binding does not prove remote access is allowed. Retain failed attempts and distinguish “not observed” from “not present.”

Handover prompt: “Question __; shell/version __; directory __; command __; output/status evidence __; supported conclusion __; smallest next read-only check __; unresolved limitation __.”

## Primary documentation

Opened 2026-10-25; retrieval details are in `SOURCES.json`.

- [GNU grep exit status](https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html): ordinary search outcomes and the quiet-mode exception excluded here.
- [GNU Bash pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html): last-command status and `pipefail` behavior.
- [PowerShell automatic variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables?view=powershell-7.5): `$?`, `$LASTEXITCODE` and `$PID`.
- [PowerShell redirection](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_redirection?view=powershell-7.5): separate streams, overwrite behavior and version-sensitive native output.
