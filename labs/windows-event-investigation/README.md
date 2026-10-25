# Windows process evidence: from a VM to an explanation

Build a short timeline from exported Sysmon Event 1 XML. It records new processes, or running programs. Explain which process started another. Find the nearby event that does not join that chain. State what a missing parent stops you from knowing.

This lab has two parts: **made-up offline practice** and **an optional real capture in your own disposable Windows VM**. The supplied records were written by hand. They were never captured from Windows. Automated checks test the offline file reader. They do not prove a real VM capture or a learner's skill.

## Before you start

Allow 25-40 minutes for the examples. Allow 30-60 minutes more for a VM that is already prepared. Offline work needs Python 3.10+ and a text editor. Use `python` below, or your installed `py -3` equivalent. You do not need extra Python packages.

For the real exercise, use a disposable Windows 11 virtual machine, or **VM**. You need a snapshot to restore it later. You or the lab administrator must already have installed Sysmon. Use no personal accounts or private files in this VM. Disconnect its network after setup. Do not change the host or its Sysmon settings. If the VM is not ready, do only the offline part and say so. Do not install tools or change logging on a work computer, your host or a shared VM.

An **image** is an executable's path. A **PID** is a process number. A **process GUID** is an ID for one instance of a process. A **parent** is the process recorded as creating a child. An **event record ID** locates a record within a log. It is not a global process ID. **UTC** is a common time reference. An **export window** is the slice of evidence you choose to save.

## 1. Predict with synthetic evidence

Run these commands from this folder:

```text
python lab.py --help
python lab.py prepare --name first-notes
```

Open `fixtures/guided.xml` in a text editor. Do not run command strings found in evidence. Fill `run/first-notes/worksheet.json` and `notes.txt`. Find the three linked records, the nearby look-alike and the absent parent creation. Predict the UTC order before opening the worked example or analysis. For each later case below, save your prediction before its inspect command.

```text
python lab.py inspect --xml fixtures/guided.xml --name guided-check --evidence-kind synthetic
python lab.py inspect --xml fixtures/changed.xml --name reuse-check --evidence-kind synthetic
python lab.py inspect --xml fixtures/challenge.xml --name gap-check --evidence-kind synthetic
python -m unittest -v test_lab.py
```

Read `analysis.json` in each new run after saving your reasons. It shows the tool's calculation. It is not a grade. Compare your guided answer with [the worked example](WORKED-EXAMPLE.md). Use [the drills](DRILLS.md) to repeat with less help.

## 2. Prepare the disposable VM deliberately

Do this setup by hand inside the VM. The Python tool does none of it. Take a snapshot before setup. Note the VM name, Windows version, Sysmon version, settings and time settings. Get Sysmon from its [official Microsoft page](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon). Read its licence and install guide. Ask the lab administrator to install it in the disposable VM if needed. This changes a service and driver. This tutorial does not download, install or request elevated access for you.

`sysmon-lab.xml` is a small teaching setup. It keeps process-create events and omits network connection collection. It is not a complete policy for suppressing events or detecting threats in a live system. In the VM, `Sysmon64.exe -s` prints the binary's schema, or rules for its settings file. Check that it supports the sample's `schemaversion="4.82"`. An administrator can then apply it through Microsoft's documented workflow. If Sysmon already has settings, do not replace them casually.

Open Event Viewer. Go to **Applications and Services Logs > Microsoft > Windows > Sysmon > Operational**. Check that new process-create events appear. If the channel is missing or access is denied, stop the real part. Resolve VM setup with its administrator. Do not change host policy.

Sysmon records events. It does not decide what they mean. Its process GUID helps tell apart processes that reuse a PID. Network connection Event 3 is off by default. This lab does not turn it on. An Event 1 export cannot support a network conclusion. See the [Sysmon documentation](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).

## 3. Generate one harmless chain, inside that VM only

With logging active, open a fresh **Windows PowerShell** window using `powershell.exe -NoProfile`. Keep it open. Run these lines by hand in that window:

```powershell
$labStart = Get-Date
cmd.exe /d /c 'powershell.exe -NoProfile -Command "Write-Output ''WINDOWS-LAB-CHILD''"'
$labEnd = Get-Date
$labStart.ToUniversalTime().ToString('o', [Globalization.CultureInfo]::InvariantCulture)
$labEnd.ToUniversalTime().ToString('o', [Globalization.CultureInfo]::InvariantCulture)
```

You should see `WINDOWS-LAB-CHILD`. The intended chain is the new PowerShell session, its child `cmd.exe`, then that process's child `powershell.exe`. `Write-Output` is a PowerShell cmdlet, which runs inside PowerShell. Do not expect a separate program with that name. The line prints a marker. It creates no files, contacts no network endpoint and changes no system settings. Record what actually appeared and the two UTC times.

The round-trip `o` format and invariant culture keep day and month order clear. Keep the XML's exact time strings. Do not replace them with a local date from the Event Viewer table. What you see in the terminal is separate evidence from Event 1.

The made-up example models this chain's shape. Its IDs, paths, times and GUIDs are invented. Your real export will have its own values. If quotes cause an error, record it. Use a fresh attempt and inspect the real command line. Failed generation is not a completed capture.

## 4. Export actual events from Event Viewer

In the VM's copy of this lab, prepare a fresh storage folder:

```text
python lab.py prepare --name vm-capture-01
```

1. Return to **Sysmon > Operational** and click **Refresh**. Choose **Filter Current Log...**. Enter `1` in **Includes/Excludes Event IDs**. Choose a short logged interval that includes the fresh PowerShell launch and command. Include about two minutes before your recorded start. Event Viewer may show local time. Note the VM's UTC offset so you do not mix time zones.
2. Inspect possible rows. Open a row and choose **Details > XML View**. Check `Provider`, `EventID`, `UtcTime`, `Image`, `CommandLine`, `ProcessGuid` and `ParentProcessGuid`. Do not choose records from marker text alone.
3. In the log's Actions pane, choose **Save Filtered Log File As...**. Or select the needed rows and choose **Save Selected Events...**. Set **Save as type: XML (*.xml)**. Save as `run/vm-capture-01/events.xml`. If that file exists, use a new name. Do not approve an overwrite. Do not use **Save Filter to Custom View**. That saves a query, not events.
4. Open the saved file in a text editor. It should have an `Events` wrapper and `Event` records with `System` and `EventData`. One complete `Event` is also accepted. The event namespace is `http://schemas.microsoft.com/win/2004/08/events/event`. A renamed `.evtx` file is not XML. A screenshot or displayed table is not suitable input either.
5. For one record, you can copy all its XML from **Details > XML View**. Save it in a new UTF-8 `.xml` file. A single record will often lack its parent's creation record. Explain that limit. Several fragments need one `<Events> ... </Events>` wrapper. Do not copy the filter dialog's XML tab. That describes a query used to select events.

Save labels may differ with the Windows build. Check the file's contents, not just its extension. **These UI steps were not run in a real VM during authoring.** Microsoft describes [saving selected events](https://download.microsoft.com/download/7/3/8/7381E0E8-CE72-4366-9849-13B2BAFBBA3C/Microsoft_Press_ebook_Windows_10_Tools_Mobile-Only.pdf). It also explains [event-filter XML queries](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-5.1), which differ from returned event data.

Inspect your saved file with this command. It only reads the file and writes a new run.

```text
python lab.py inspect --xml run/vm-capture-01/events.xml --name vm-analysis-01 --evidence-kind vm-export
```

Use `receipt.json` for the exact SHA-256 of the bytes inspected. This hash checks file identity only. `vm-export` is your claim about the source. The tool does not prove that claim. Keep the original export private. The inspector does not copy or edit it. If you need more context, export to a new capture folder. Inspect it in a new run. Do not merge overlapping exports without saying so.

## 5. Explain the relationships and the timeline

For each child, match its `ParentProcessGuid` to a record's `ProcessGuid` on the same `Computer`. Read that record's image, PID and command line. The tool labels a GUID match `parent-present`. If no match is available, it uses `parent-not-in-export`. It lists other PID matches as `pid_only_other_candidates`. They are **not links**. If parent PID, image or time conflict, the tool adds a consistency note. Treat it as a conflict to review.

The timeline sorts by `EventData/UtcTime`, converted to UTC with seven fractional digits. It also keeps the original `UtcTime` and `System/TimeCreated` `SystemTime`. Do not assume those fields are the same. Event Viewer may show local time. The tool keeps numeric precision of 100 nanoseconds. That does not prove the VM clock is that accurate. If times are equal, computer and record ID give a stable display order only. Record order, clock drift, late logging and a narrow export can limit your account of events.

A missing parent may have started before the chosen time window. A filter may have left it out. Logging may have been off, or records lost. Ask for a wider export and the logging settings. A matching chain or familiar program name cannot prove command success or harmless intent. It also cannot prove the export is intact.

## Maintained utility contract

`lab.py` is the sole entry point. `prepare` makes blank notes and a worksheet. `inspect` adds `analysis.json` and `receipt.json`. Each output needs a fresh direct child of this folder's ignored `run/`. The tool refuses existing folders, paths that escape this folder, symbolic links and Windows reparse paths. Input paths start from your terminal's current folder. No commands found in XML are run.

Input must be one namespaced `Event`, or `Events` with such records inside. Use UTF-8 or UTF-16 with a byte-order mark. The size limit is 5 MiB and the record limit is 5,000. The tool analyses only Sysmon Event 1 from its Operational channel. It counts other providers and event IDs as skipped. Each record needs both times, computer, record ID, image and command line. It also needs process GUID/PID and parent GUID/PID/image/command line. Blank command lines are kept.

The tool rejects missing fields, duplicate record or process identities, and invalid values. It also rejects DTD/entity declarations, which can define extra XML structures or replacements. EVTX and CLIXML are not supported. Exit `0` means success. Exit `2` means bad input or a file error. A failed write may leave a partial new run. Keep it and choose a new name.

This tool assumes a quiet local folder. It does not guard against hostile path changes during a run. It is not a forensic evidence collection tool. Git's ignore rule helps prevent accidental tracking. It does not encrypt files or prevent uploads. Keep exports private. Command lines and computer names may reveal private information. Tests leave small ignored `run/tests-*` records.

## Handover and honest completion

Write a short note. Include the question, evidence kind, source hash and capture window. Cite two exact record/GUID references. Give your finding, one limit and the next check. Say whether you used help or the worked answer. For real work, add the VM settings and what you saw in the terminal. Claim a real capture only if you did and checked it yourself. Leave competence unassessed.

When done, restore the disposable VM to its snapshot with your usual VM controls. The lab does not remove or change host services.

Primary sources were checked on 23 October 2026. Offline work needs no internet. The [PowerShell output reference](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-output?view=powershell-5.1) explains the harmless marker command.
