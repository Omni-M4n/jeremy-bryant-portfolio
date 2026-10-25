# Build and verify a disposable lab workbench

Can you show which connections are allowed, then make and undo one harmless change? Start with made-up saved evidence. The optional real task uses one **separately created disposable Ubuntu VM in VirtualBox 7.x on Windows**. Every network adapter must be disabled. The one allowed connection is an HTTP request from the guest to its own loopback interface. This is a small first workbench to use before adding a second VM.

Allow 25 minutes for the given case. Allow 30-45 minutes for the real task once the VM exists. Start with a basic grasp of virtual machines, folders and a terminal. The offline helper needs Python 3.10+. The real task needs Ubuntu 22.04/24.04, Bash, `ip`, `ss`, `curl`, `sha256sum` and Python 3 in the guest. These must already be present. Choosing an OS image, installing it and making the VM are separate setup tasks with a supervisor. If anything needed is missing, use the given case. Record hands-on work as **not performed**.

The **host** is the computer that runs the VM software. The **guest** is the operating system inside a VM. **Loopback** is a connection back to the same operating system. An **adapter** is a virtual network device. A **default route** is the path to other networks when no more specific path is listed. A **wildcard binding** listens on all local IPv4 addresses (`0.0.0.0`) or IPv6 addresses (`::`).

A **snapshot** saves a VM's state. To **restore** it is to return to that state. A **normal virtual disk** stores the VM's files. Its changes are included in snapshots. A **write-through disk** keeps its changes when a snapshot is restored. A **hash** is a fingerprint of a file's bytes. A **UUID** is a unique ID for a VM or snapshot. **Passthrough** lets a guest use a host device directly. The **boundary** is the exact set of allowed connections and shared resources for this task.

## Start with supplied evidence

From this lab folder:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `inventory.txt`, `connectivity.txt` and `restore.txt`. Draw a host box with one guest box inside it. Draw the loopback request inside the guest. Record evidence for `scope`, `network`, `host-paths`, `connectivity`, `rollback` and `review` in `answers.json`. Save your prediction and its limits in `notes.txt` before revealing the answer.

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python test_lab.py
python lab.py verify
```

`check` compares labels and requires written reasons and evidence. A person must judge the reasoning. `verify` checks the materials. Neither command assesses real VM use. Exit code 0 means success. Code 1 means missing or different answers, or a mismatch with the saved reference. Code 2 means bad input. Save each first attempt. Use a new `run/` folder for another case.

## Exact offline model

Every case uses the shared foundation envelope. `data` contains the fixed boundary `disconnected-loopback` and a made-up VM ID. It has a true/false claim that the VM is disposable. Adapter records give `slot` 1-8 and a mode. Other fields list host transfer settings, guest route/address counts, a loopback summary and snapshot/hash evidence. `null` means a record was not given. The program only reads these fields. It does not run commands, read real VM-tool output, query a host or inspect a VM.

| Decision | Rule, in precedence order |
|---|---|
| `scope` | Recorded disposable → `disposable-vm-recorded`; otherwise `stop-non-disposable`. |
| `network` | Any adapter outside disabled/not-attached → `network-boundary-violated`; otherwise missing any of eight slots → `adapter-inventory-incomplete`; otherwise a default route or non-loopback guest address → `guest-evidence-conflicts`; otherwise `disconnected-boundary-supported`. |
| `host-paths` | Any shared folder, clipboard, drag/drop or passthrough enabled → `host-transfer-path-present`; otherwise `no-listed-host-transfer-path`. |
| `connectivity` | Wildcard bind → `listener-binding-out-of-scope`; missing field → `loopback-evidence-incomplete`; response other than HTTP 200 with exact `BASELINE` + LF → `loopback-positive-failed`; no refusal after stop → `loopback-stop-check-failed`; otherwise `loopback-pair-demonstrated`. |
| `rollback` | Write-through disk → `disk-outside-snapshot-model`; missing evidence → `restore-evidence-incomplete`; wrong VM/snapshot ID → `snapshot-identity-mismatch`; unchanged pre-restore hash → `change-not-demonstrated`; restored hash differs from baseline → `restored-bytes-mismatch`; otherwise `dummy-file-rollback-demonstrated`. |
| `review` | All five checks have their positive result → `supplied-evidence-complete`; otherwise `resolve-evidence-gaps`. |

IDs and hashes are compared as supplied. The planned dummy-file texts are `BASELINE\n` and `CHANGED\n`; `\n` means one line-feed byte. A plan to change the text does not show that the edit happened. Use the recorded hashes to compare the three file states. Case addresses come from ranges set aside for examples. Guest addresses and routes are supplied summaries. The helper rejects fields it cannot read or does not support. A guest route alongside disconnected adapters could be an old route or a record from a different time. This small model cannot tell which explanation is right.

## Optional real workflow: disconnected VirtualBox guest

Use only a VM made separately for disposable practice. Do not reuse a coursework VM or one with personal data. Keep the host's firewall, network and security settings as they are. This task changes only the named disposable VM and its dummy file. It needs no scan or outside connection.

1. **Identify the VM while it is shut down normally.** Record its exact name and UUID, VirtualBox version, guest version, time and purpose. Check that its disks hold no work you need. They must be normal virtual disk images. Do not use a real host disk, a disk shared with another VM or a mounted host folder. Do not use a write-through disk: its changes survive a restore. In VirtualBox Manager, select only this VM and open Settings. Disable all four visible Network adapters. Check the full adapter list as shown below. If slots 5-8 include an enabled adapter, stop. Ask the setup supervisor to prepare the VM correctly.
2. **Review the other paths.** In General → Advanced, disable Shared Clipboard and Drag and Drop. Shared Folders must be empty. USB must have no host devices attached and no automatic attachment filters. Do not attach a USB network adapter. Storage must list only this VM's normal virtual disk and the intended OS media. Keep remote display and serial host connections disabled. Save screenshots or notes of the settings. These checks give evidence. They do not certify the VM as secure.
3. **Read all adapter slots on the Windows host.** In PowerShell, replace the example VM name with the verified disposable name. The path below points to the installed program. It is not a script to download. If the path differs, find the installed app through its shortcut. Do not install anything for this step.

```powershell
& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' --version
& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' showvminfo 'Practice Ubuntu' --machinereadable
```

Confirm that `nic1` through `nic8` each report `none` (disabled). In VirtualBox, `null` means Not attached. The offline case accepts it. This walkthrough uses disabled adapters. Keep the full output private, plus an excerpt with all eight slots. Missing slots or fields you do not know mean **unverified**. They do not mean disabled. Check the exact VM ID as well as its display name.

4. **Boot that guest and inspect without contacting other machines.** Run inside the guest terminal:

```bash
ip -brief address
ip -4 route show table all
ip -6 route show table all
python3 --version
curl --version
```

Expect loopback (`127.0.0.1`, normally `::1`) and its local routes. With all adapters disabled, there should be no other interface address or default route. Stop if an extra device or route has no clear cause. Check the settings with your supervisor. Do not test the internet. A failed ping would not prove isolation. Save the output and explain why it agrees with the host settings. NAT allows outbound traffic. Host-only includes the host. Internal networking joins chosen VMs. None is the disconnected boundary used here.

5. **Create one new dummy folder in the guest.** This is the only file-edit task. Check that the name is unused. `mkdir` without `-p` refuses an existing folder. Run each line only if the last one worked. If the folder already exists, choose another numbered name. Use that name throughout.

```bash
mkdir "$HOME/workbench-attempt-01"
cd "$HOME/workbench-attempt-01"
pwd
printf 'BASELINE\n' > marker.txt
cat marker.txt
sha256sum marker.txt
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$HOME/workbench-attempt-01"
```

The final command stays in the foreground. In a **second guest terminal**, confirm the binding and make one request:

```bash
ss -ltn 'sport = :8765'
curl --noproxy '*' --max-time 3 -i http://127.0.0.1:8765/marker.txt
```

Expect a `127.0.0.1:8765` listener, HTTP 200 and `BASELINE`. If the port is already used, stop. Choose a different unused high port and use it throughout. Do not kill another process. Stop your server with Ctrl+C in its terminal. Repeat the same `curl` request. Expect connection refusal and no HTTP response. At once, record `printf 'curl exit=%s\n' "$?"`. A timeout or a reply from another HTTP service does not pass this negative check. This tests only the intended loopback service.

6. **Save the baseline snapshot.** Record the baseline hash outside the guest. You could use a host notebook with screenshots of the guest window. Shut the guest down normally through its OS menu. In VirtualBox Manager → Snapshots → Take, name it `workbench-baseline-01`. Record its ID, VM ID and powered-off state. Check that the host has enough space for snapshots before going on. Your notes and screenshots must survive a restore. Evidence kept only in the guest may be rolled back with it.
7. **Make and record a real change.** Boot the same VM. Open the guest terminal and change only the named marker:

```bash
cd "$HOME/workbench-attempt-01"
pwd
printf 'CHANGED\n' > marker.txt
cat marker.txt
sha256sum marker.txt
```

Save the changed hash. Confirm that it differs from the baseline. Shut down normally. Select the recorded baseline in Snapshots and use **Restore**. Check the VM and snapshot IDs in the dialog. Restore discards changes since that snapshot. Proceed only with this disposable VM. Deleting a snapshot is a different action. It is not the rollback command.
8. **Check the restore and finish.** Boot and repeat `cat` and `sha256sum` for the exact marker. The content and hash must match the baseline and differ from the changed state. Recheck all eight adapters, listed sharing settings and guest routes. A snapshot restore also restores VM settings. The server should be stopped, since it was stopped before taking the baseline. Keep evidence outside the guest. Then shut down the VM normally. Keep the baseline for the next approved lab. No deletion or host cleanup is needed.

## Evidence and acceptance

Save a small diagram with the scope and VM identity. Keep tool versions, all adapter settings, sharing/device checks and guest routes/addresses. Keep the successful loopback request, listener binding and refusal after your server stops. Add the snapshot ID, time, disk mode and all three file hashes: baseline, changed and restored. Name screenshots and command notes so each claim points to one exact item. Keep unexpected output and the first attempt.

A reviewer accepts the **hands-on attempt** only after checking the saved real evidence. You must also explain each boundary. Matching hashes alone cannot show that the VM was isolated. No real VM, snapshot or network workflow was run while making this package. Only the offline helper and given cases can be tested here. Snapshots depend on their storage. They do not replace a separate backup. This task uses a harmless dummy file. It is not a design for containing malware.

Handover prompt: “For VM __ at time __, record __ supports boundary __. The loopback request __ gave result __. After the server stopped, check __ gave result __. Snapshot __ restored marker hash __ after it changed to __. Still unchecked: __.”

## Primary documentation

Opened 2026-10-25; retrieval details are in `SOURCES.json`.

- [Oracle VirtualBox virtual networking](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html): eight adapters and the differences among modes.
- [Oracle working with VMs](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/working-with-vms.html): snapshot take/restore, settings restoration and normal-disk limits.
- [Oracle VBoxManage command reference](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/vboxmanage.html): read-only `showvminfo` and version commands.
- [Python `http.server`](https://docs.python.org/3/library/http.server.html): local server binding and directory options; this small server is used only for disposable local practice.
