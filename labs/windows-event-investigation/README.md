# Windows process evidence: from a VM to an explanation

Build a short process timeline from exported Sysmon Event 1 XML. Explain which
process started another, which nearby event is unrelated to the recorded chain,
and what a missing parent prevents you from concluding.

This original beginner lab has two distinct parts: **synthetic offline practice**
and **an optional real capture in your own disposable Windows VM**. The shipped
records were manually authored, never captured from Windows. Automated checks
test the offline parser; no real VM capture or learner competence is claimed.

## Before you start

Allow 25-40 minutes for the examples, then 30-60 minutes for an already prepared
VM. Offline work needs Python 3.10+ and a text editor. Use `python` below, or your
installed `py -3` equivalent. No extra Python packages are needed.

The real exercise needs a disposable Windows 11 VM, a snapshot, and Sysmon
already installed by you or a lab administrator. Use a VM with no personal
accounts or private files; disconnect its network after preparation. Keep the
host and its Sysmon settings untouched. If the VM is not ready, complete only
the offline part and state that limitation. Do not run installation or logging
changes on a work computer, your host, or a shared VM.

> **Vocabulary:** Image: executable path. PID: numeric process identifier.
> Process GUID: identifier recorded for a process instance. Parent: process
> recorded as creating a child. Event record ID: location within an event log,
> not a global process identifier. UTC: common time reference. Export window:
> the slice of evidence selected for saving.

## 1. Predict with synthetic evidence

Run these commands from this folder:

```text
python lab.py --help
python lab.py prepare --name first-notes
```

Open `fixtures/guided.xml` in a text editor. Do not execute command strings from
evidence. Fill `run/first-notes/worksheet.json` and `notes.txt`: find the three
linked records, the nearby look-alike, and the absent parent creation. Predict
the UTC order before opening the worked example or analysis.

```text
python lab.py inspect --xml fixtures/guided.xml --name guided-check --evidence-kind synthetic
python lab.py inspect --xml fixtures/changed.xml --name reuse-check --evidence-kind synthetic
python lab.py inspect --xml fixtures/challenge.xml --name gap-check --evidence-kind synthetic
python -m unittest -v test_lab.py
```

Read `analysis.json` in each new run. It is a reference calculation, not a grade.
Complete your written reasoning, then compare it with [the worked example](WORKED-EXAMPLE.md).
Use [the drills](DRILLS.md) to repeat with less help.

## 2. Prepare the disposable VM deliberately

This section is manual setup inside the VM. The Python utility does none of it.
Take a snapshot before setup and keep a note of the VM name, Windows version,
Sysmon version, configuration and time settings. Obtain Sysmon from its
[official Microsoft page](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).
Read its licence and installation guidance. Have the lab administrator install
it in the disposable VM if you are not comfortable with the service and driver
change; this tutorial does not auto-download, install or request elevation.

`sysmon-lab.xml` is a small teaching configuration: retain process creation and
omit network connection collection. It is not a complete event-suppression or
production detection policy. In the VM, `Sysmon64.exe -s` prints the binary's
schema. Check compatibility with the sample's `schemaversion="4.82"` before an
administrator applies it using Microsoft's documented configuration workflow.
If Sysmon is already configured, do not casually replace its configuration.

Open Event Viewer and navigate to **Applications and Services Logs > Microsoft
> Windows > Sysmon > Operational**. Confirm that new process-create events
appear. If the channel is missing, or access is denied, stop the real portion
and resolve VM preparation with its administrator; do not alter host policy.

Sysmon records events; it does not supply an investigation verdict. Its process
GUID helps distinguish reused PIDs. Network connection Event 3 is disabled by
default, and this lab does not enable it. No network conclusion follows from
an Event 1 export. These behaviours are described in the
[Sysmon documentation](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).

## 3. Generate one harmless chain, inside that VM only

With logging active, open a fresh **Windows PowerShell** window using
`powershell.exe -NoProfile`. Keep this window open. Run the following lines
manually there:

```powershell
$labStart = Get-Date
cmd.exe /d /c 'powershell.exe -NoProfile -Command "Write-Output ''WINDOWS-LAB-CHILD''"'
$labEnd = Get-Date
$labStart.ToUniversalTime().ToString('o', [Globalization.CultureInfo]::InvariantCulture)
$labEnd.ToUniversalTime().ToString('o', [Globalization.CultureInfo]::InvariantCulture)
```

You should see `WINDOWS-LAB-CHILD` in the window. The intended sequence is the
new PowerShell session, a child `cmd.exe`, then its child `powershell.exe`.
`Write-Output` is a PowerShell cmdlet, so do not expect a separate executable
with that name. The line prints a marker; it does not create files, contact a
network endpoint or change system settings. Record what actually appeared and
the two UTC times. The round-trip `o` format with invariant culture avoids
day/month ordering differences. Preserve the XML's timestamp strings; do not
replace them with a regional date from the rendered Event Viewer table. A
terminal observation is separate evidence from Event 1.

The synthetic example models this shape; its record IDs, paths, times and GUIDs
are invented. Do not expect your real export to match its values. If quoting
fails, record the error, use a fresh attempt, and inspect the actual command
line. Do not label failed generation as a completed capture.

## 4. Export actual events from Event Viewer

In the VM's copy of this lab, first prepare a fresh storage folder:

```text
python lab.py prepare --name vm-capture-01
```

1. Return to **Sysmon > Operational**, click **Refresh**, then **Filter Current
   Log...**. Enter `1` in **Includes/Excludes Event IDs**. Select a small logged
   interval containing the fresh PowerShell launch and the command, including
   about two minutes of context before the recorded start. Event Viewer may
   display local times; note the VM's UTC offset rather than mixing the two.
2. Inspect candidate rows. Open a row, choose **Details > XML View**, and check
   `Provider`, `EventID`, `UtcTime`, `Image`, `CommandLine`, `ProcessGuid` and
   `ParentProcessGuid`. Do not choose records by marker text alone.
3. In the log's Actions pane choose **Save Filtered Log File As...** (or select
   the needed rows and **Save Selected Events...**). In the save dialog set
   **Save as type: XML (*.xml)** and save as
   `run/vm-capture-01/events.xml`. Use a new name if the file already exists;
   do not approve an overwrite. Do not use **Save Filter to Custom View**:
   that saves a query, not events.
4. Open the saved file in a text editor. It should contain an `Events` wrapper
   and `Event` records with `System` and `EventData`, or one complete `Event`.
   The event namespace is `http://schemas.microsoft.com/win/2004/08/events/event`.
   An `.evtx` file renamed `.xml`, a screenshot or a rendered table is unsuitable.
5. For a single record you can instead copy the entire XML from **Details >
   XML View** into a new UTF-8 `.xml` file. A one-record export will usually
   have no parent creation available; explain that restriction. Multiple
   fragments require one `<Events> ... </Events>` wrapper. Do not copy the XML
   tab from the filter dialog, which describes the selection query.

The exact save labels can vary with the Windows build; confirm the file's
contents instead of its extension alone. This UI procedure has not been
executed in a real VM during authoring. Microsoft describes
[saving selected events](https://download.microsoft.com/download/7/3/8/7381E0E8-CE72-4366-9849-13B2BAFBBA3C/Microsoft_Press_ebook_Windows_10_Tools_Mobile-Only.pdf)
and distinguishes [event-filter XML queries](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-5.1)
from returned event data.

Inspect your saved file; this command only reads the file and writes a new run:

```text
python lab.py inspect --xml run/vm-capture-01/events.xml --name vm-analysis-01 --evidence-kind vm-export
```

Use `receipt.json` to record the exact SHA-256 of the bytes inspected. It proves
file identity only. `vm-export` is your declaration, not tool authentication.
Retain the original export privately; the inspector does not copy or modify it.
If more context is needed, export to a new capture folder and inspect it in a
new analysis run. Do not silently merge overlapping exports.

## 5. Explain the relationships and the timeline

For each child, match its `ParentProcessGuid` to another record's `ProcessGuid`
on the same `Computer`. Read the matched record's image, PID and command line.
The script labels a GUID match `parent-present`, and an unavailable match
`parent-not-in-export`. It lists other matching PIDs separately as
`pid_only_other_candidates`; they are **not links**. Contradictory parent PID,
image or time gets a consistency note rather than a confident explanation.

The timeline sorts by `EventData/UtcTime`, converted to UTC with seven fractional
digits. It also retains the original `UtcTime` and `System/TimeCreated`
`SystemTime`. Do not assume these fields are identical. Event Viewer may render
its display time locally. The script keeps 100-nanosecond numeric precision,
which is not a claim that the VM clock is accurate to that level. Equal times
use computer and record ID for a stable display only. Record order, clock drift,
delayed logging and a narrow export can limit the story.

Missing parent creation can mean it started before the selected interval,
filtering excluded it, logging was unavailable, or records were lost. Ask for a
wider export and configuration context. Neither a matching chain nor a familiar
executable proves command success, benign intent or the integrity of the export.

## Maintained utility contract

`lab.py` is the sole entry point. `prepare` creates blank notes and a worksheet;
`inspect` adds `analysis.json` and `receipt.json`. Every output uses a fresh
direct child of this folder's ignored `run/`. Existing output folders, path
traversal, symbolic links and Windows reparse paths are refused. Input paths are
relative to your terminal directory. No commands found in XML are executed.

Accepted input: one namespaced `Event`, or `Events` containing such events,
UTF-8 or BOM-marked UTF-16, at most 5 MiB and 5,000 records. Only Sysmon Event 1
from its Operational channel is analysed; other providers/event IDs are counted
as skipped. Required fields are the two timestamps, computer, record ID, image,
command line, process GUID/PID, and parent GUID/PID/image/command line. Empty
command lines are retained. Missing fields, duplicate record/process identities,
DTD/entity declarations and invalid values fail closed. EVTX and CLIXML are not
supported. Exit code `0` means success; `2` means invalid input or filesystem
error. A failed write can leave a partial new run: keep it and choose a new name.

This bounded utility assumes a quiet local folder, not hostile concurrent path
replacement. It is not a forensic acquisition tool. The ignore rule prevents
ordinary accidental Git tracking; it does not encrypt data or prevent an upload.
Keep exports private because command lines and machine names can disclose
sensitive information. Tests leave small ignored `run/tests-*` records.

## Handover and honest completion

Deliver a short note with the question, evidence kind, source hash, capture
window, two exact record/GUID references, your finding, a limitation and next
check. Say whether help or the worked answer was used. For real work, add the
VM/configuration details and actual terminal observation. Only claim a real
capture if you personally performed and checked it. Leave competence unassessed.
Return the disposable VM to its snapshot when finished through your usual VM
controls; the lab does not remove or change host services.

Primary documentation was checked on 23 October 2026. Offline operation needs
no internet connection. The
[PowerShell output reference](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-output?view=powershell-5.1)
explains the harmless marker command.
