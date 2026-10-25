# Build and verify a disposable lab workbench

Can you show the intended connectivity boundary, then make and undo one harmless change? Begin with fictional saved evidence. The optional real workflow uses one **separately created disposable Ubuntu VM in VirtualBox 7.x on Windows**, with every network adapter disabled. Its intended connection is an HTTP request from the guest to its own loopback interface. This is a deliberately narrow first workbench, suitable before adding a second VM.

Allow 25 minutes for the supplied case and 30-45 minutes for the real workflow once the VM exists. Prerequisites: a basic introduction to virtual machines, folders, a terminal, and Python 3.10+ for the offline helper. The real workflow assumes Ubuntu 22.04/24.04, Bash, `ip`, `ss`, `curl`, `sha256sum` and Python 3 already available in the guest. Installation, choosing an OS image and creating the VM are separate supervised setup tasks. If any prerequisite is unavailable, complete the supplied case and record hands-on work as **not performed**.

**Vocabulary:** host = the computer running the VM software; guest = the operating system inside a VM; loopback = a connection back to the same operating system; adapter = a virtual network device. A **default route** is the usual path to other networks when no more specific path is listed. A **wildcard binding** listens on all local IPv4 addresses (`0.0.0.0`) or IPv6 addresses (`::`).

A **snapshot** saves a VM's state; **restore** means returning to that state. A **normal virtual disk** stores the VM's files and includes its changes in snapshots. A **write-through disk** keeps its changes when a snapshot is restored. A **hash** is a fingerprint of a file's bytes. A **UUID** is a unique ID for a VM or snapshot. **Passthrough** lets a guest use a host device directly. The **boundary** is the exact set of connections and shared resources allowed for this exercise.

## Start with supplied evidence

From this lab folder:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `inventory.txt`, `connectivity.txt` and `restore.txt`. Draw a host box containing one guest box. Draw the loopback request inside the guest. Record the evidence for each of `scope`, `network`, `host-paths`, `connectivity`, `rollback` and `review` in `answers.json`; save a prediction and limitations in `notes.txt` before revealing the reference.

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python test_lab.py
python lab.py verify
```

`check` compares decision strings and requires written explanation/evidence fields. A person must judge the reasoning. `verify` checks the materials; neither command assesses real VM operation. Exit codes are 0 for success, 1 for incomplete/different answers or reference differences, and 2 for invalid input. Preserve each first attempt and use a new `run/` folder for another case.

## Exact offline model

Every case uses the shared foundation envelope. `data` contains the fixed boundary `disconnected-loopback`, a fictional VM ID, a boolean disposable declaration, adapter records (`slot` 1-8 and mode), listed host transfer settings, guest route/address counts, a loopback transcript summary and snapshot/hash evidence. `null` means an observation was not supplied. The program reads these fields only. It does not execute commands, parse real hypervisor output, query a host, or inspect a VM.

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

Use only a VM created separately for disposable practice. Do not repurpose a coursework VM or a VM with personal data. Keep the host's firewall, networking and security settings as they are. This workflow changes only the named disposable VM and its dummy file; it needs no scan or external connection.

1. **Identify the VM while it is shut down normally.** Record its exact name and UUID, VirtualBox version, guest version, time and purpose. Check that its disks contain no work you need and use normal virtual disk images. It must not use a real host disk directly, a disk shared with another VM, a write-through disk whose changes survive restore, or a mounted host folder. In VirtualBox Manager, select only this VM and open Settings. Disable all four visible Network adapters. Inspect the complete adapter list as described below; if an enabled adapter exists in slots 5-8, stop and ask the setup supervisor to prepare the disposable VM correctly.
2. **Review the other paths.** General → Advanced: Shared Clipboard and Drag and Drop disabled. Shared Folders: empty. USB: no host USB devices attached or automatic attachment filters; do not attach a USB network adapter. Check Storage for only this VM's normal virtual disk and the intended OS media. Keep remote display and serial host connections disabled. Record screenshots or the visible settings. These are evidence requirements, not a security certification.
3. **Read all adapter slots on the Windows host.** In PowerShell, replace the example VM name with the verified disposable name. The standard installation path below is a program path, not a script to download. If it differs, locate the installed application through its shortcut rather than installing anything.

```powershell
& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' --version
& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' showvminfo 'Practice Ubuntu' --machinereadable
```

Confirm `nic1` through `nic8` each report `none` (disabled). VirtualBox `null` corresponds to Not attached; the offline case accepts it, but this walkthrough deliberately uses disabled adapters. Keep the full output privately and an excerpt showing all eight slots. Missing slots or unfamiliar fields mean **unverified**, not disabled. Look at the exact VM identifier as well as its display name.

4. **Boot that guest and inspect without contacting other machines.** Run inside the guest terminal:

```bash
ip -brief address
ip -4 route show table all
ip -6 route show table all
python3 --version
curl --version
```

Expect loopback (`127.0.0.1`, normally `::1`) and its local routes. With all adapters disabled, there should be no non-loopback interface address and no default route. Stop on an unexplained extra device/route; inspect configuration with the supervisor rather than testing the internet. A failed ping would not prove isolation. Save the outputs and explain why they agree with the host settings. NAT permits outbound connectivity; host-only includes the host; internal networking joins selected VMs. None is the disconnected boundary used here.

5. **Create one new dummy folder in the guest.** This is the only file-edit exercise. Check that the name is unused; `mkdir` without `-p` refuses an existing directory. Run each line only if the preceding one succeeded. If it already exists, choose another numbered name and substitute it throughout.

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

Expect a `127.0.0.1:8765` listener, HTTP 200 and `BASELINE`. If the port is already used, stop and use a different unused high port consistently; do not kill another process. Stop your server with Ctrl+C in its terminal and repeat the same `curl` request. Expect connection refusal and no HTTP response; immediately record `printf 'curl exit=%s\n' "$?"`. A timeout or an unrelated HTTP answer does not satisfy this negative check. This demonstrates the intended loopback service only.

6. **Save the baseline snapshot.** Record the baseline hash outside the guest, for example in a host notebook with screenshots of the guest window. Shut the guest down normally using its OS menu. In VirtualBox Manager → Snapshots → Take, name it `workbench-baseline-01` and record its ID, VM ID and powered-off state. Ensure adequate host storage for snapshots before proceeding. The screenshot/notebook must survive restoration; evidence left only in the guest may be rolled back with it.
7. **Demonstrate a real change.** Boot the same VM, open the guest terminal, and change only the named marker:

```bash
cd "$HOME/workbench-attempt-01"
pwd
printf 'CHANGED\n' > marker.txt
cat marker.txt
sha256sum marker.txt
```

Save the changed hash and confirm it differs from the baseline. Shut down normally. Select the recorded baseline in Snapshots and use **Restore**, verifying the VM and snapshot identity in the dialog. Restore discards changes since that snapshot; proceed only with this disposable VM. Snapshot deletion is a different operation and is not the rollback command.
8. **Verify restoration and finish.** Boot and repeat `cat` and `sha256sum` for the exact marker. The content and hash must match the recorded baseline and differ from the changed state. Recheck all eight adapters, listed sharing settings and guest routes because restoring a snapshot also restores VM settings. The server should be stopped because the baseline was taken after stopping it. Keep the evidence outside the guest, then shut down the disposable VM normally. Keep the baseline for the next approved lab; no deletion or host cleanup is required.

## Evidence and acceptance

Save a small diagram, scope/VM identity, tool versions, all adapter settings, sharing/device review, guest routes/addresses, successful loopback request, listener binding, refusal after your server stops, snapshot ID/time/disk mode, and baseline/changed/restored file hashes. Name screenshots and command notes so each claim points to one exact item. Preserve unexpected output and the first attempt.

A reviewer accepts the **hands-on attempt** only after checking the actual retained evidence and hearing an explanation of each boundary. Matching hashes alone cannot establish the VM was isolated. No real VM, snapshot or network workflow was exercised when this package was authored; only the offline helper and supplied cases are mechanically testable here. Snapshots depend on their underlying storage and are not a replacement for a separate backup. This is benign practice, not a malware containment design.

Handover prompt: “For VM __ at time __, evidence __ supports boundary __. The intended loopback request __ and stopped-server check __ behaved as __. Snapshot __ restored marker hash __ after it changed to __. Still unverified: __.”

## Primary documentation

Opened 2026-10-25; retrieval details are in `SOURCES.json`.

- [Oracle VirtualBox virtual networking](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html): eight adapters and the differences among modes.
- [Oracle working with VMs](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/working-with-vms.html): snapshot take/restore, settings restoration and normal-disk limits.
- [Oracle VBoxManage command reference](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/vboxmanage.html): read-only `showvminfo` and version commands.
- [Python `http.server`](https://docs.python.org/3/library/http.server.html): local server binding and directory options; this small server is used only for disposable local practice.
