# Capture and export your own dummy HTTP transfer

You must make your own capture for this lab. The three made-up cases in
`practice.py` teach gaps and overlaps as a separate task. The PCAP files they
create do not prove that you made a real capture.

Use Windows PowerShell and Python 3.10+. You also need an **existing** Wireshark
install with Dumpcap, TShark and working Npcap loopback capture. Loopback sends
traffic back to the same computer. Allow 20-30 minutes. Do not install tools or
seek admin rights for this task. Do not change the firewall or a VM, or use an
external site. Stop if a tool or the loopback interface is missing. Also stop if
your current account lacks capture access. Record the limit. The made-up cases
alone do not complete this stage.

The helper sends one dummy text file from `127.0.0.1:8765` to a client on the
same computer. It then closes the server. It serves only `/dummy.txt`. It cannot
serve a folder, choose another host, use a proxy or fetch a third-party URL.
The client copy proves that the transfer arrived. The object you export from
the capture shows what you recovered from it. Keep these two files separate.

## 1. Prepare, predict and inspect the existing tools

Open two PowerShell terminals in this lab folder. In terminal A:

```powershell
python loopback.py prepare --out run/capture-01
$dumpcap = 'C:\Program Files\Wireshark\dumpcap.exe'
$tshark = 'C:\Program Files\Wireshark\tshark.exe'
Test-Path -LiteralPath $dumpcap
Test-Path -LiteralPath $tshark
```

If either result is false, check where the tool is already installed. Use that
verified path, or stop if you cannot find it. If `capture-01` exists, use a new
attempt name in every step. Edit `run/capture-01/prediction.txt` before the
transfer. Predict which evidence would show that an exported object is complete.
State what a missing packet could change. Explain what a matching hash cannot prove.

```powershell
& $dumpcap --version | Out-File run/capture-01/dumpcap-version.txt
& $tshark --version | Out-File run/capture-01/tshark-version.txt
& $dumpcap -D | Tee-Object -FilePath run/capture-01/interfaces.txt
Get-NetTCPConnection -State Listen -LocalPort 8765 -ErrorAction SilentlyContinue
```

Stop if anything already listens on port 8765. Do not stop that process or
change the port in only one command. In `-D`, find the **loopback** entry
whose device name is `\Device\NPF_Loopback`. Stop if that exact entry is missing
or capture access is denied. Never use Ethernet, Wi-Fi, VPN or the default
interface in its place. Interface names and numbers can differ between computers.

## 2. Capture first, then make one real transfer

In terminal A, check that `source/transfer.pcapng` does not exist. This command
captures only IPv4 TCP traffic with both endpoints `127.0.0.1` and port 8765.
It writes at most 256 packets and stops after 45 seconds. Keep the console log.
It records the packet count and any message about drops or errors.

```powershell
if (Test-Path run/capture-01/source/transfer.pcapng) { throw 'Use a fresh attempt' }
& $dumpcap -i '\Device\NPF_Loopback' -f 'ip and src host 127.0.0.1 and dst host 127.0.0.1 and tcp port 8765' -s 0 -c 256 -a duration:45 -w run/capture-01/source/transfer.pcapng 2>&1 | Tee-Object -FilePath run/capture-01/capture-log.txt
```

Wait until terminal A reports that capture has started. While it is running,
run this in terminal B from the same lab folder:

```powershell
python loopback.py transfer --out run/capture-01
```

The helper sends a real plain HTTP request and response. It prints the receipt
path only after the local server is closed. If it reports an error, stop the
capture with Ctrl+C. Keep the partial evidence and explain the failure. Do not
call a failed capture complete. A capture with no packets is also incomplete.
Do not kill another listener or change host settings. Do not reuse this attempt
to hide a failed try.

Let terminal A finish within 45 seconds. Do not leave a capture running.
Use Ctrl+C if you need to stop early. The helper closes its server if stopped.
Check that no port-8765 listener remains before you go on.

## 3. Preserve the capture and inspect a copy

In terminal A, after Dumpcap has exited:

```powershell
Get-FileHash run/capture-01/source/transfer.pcapng -Algorithm SHA256 | Format-List | Out-File run/capture-01/capture-before.txt
(Get-Item run/capture-01/source/transfer.pcapng).IsReadOnly = $true
Copy-Item -LiteralPath run/capture-01/source/transfer.pcapng -Destination run/capture-01/output/transfer.pcapng
& $tshark -n -r run/capture-01/output/transfer.pcapng -d tcp.port==8765,http -Y 'tcp.port == 8765' -T fields -E header=y -e frame.number -e frame.time_epoch -e ip.src -e ip.dst -e tcp.stream -e tcp.len -e http.request.method -e http.request.uri -e http.response.code -e http.content_length | Out-File run/capture-01/output/packet-table.txt
```

Check that the exit code (`$LASTEXITCODE`) is zero after each TShark command.
Inspect `packet-table.txt`. Both IP endpoints must be `127.0.0.1`. Find the
GET `/dummy.txt`, its response and the expected Content-Length in the same TCP
stream. Content-Length is the stated body size in bytes. If you use Wireshark,
open only the copied capture. Use **Analyze > Decode As** to read TCP port 8765
as HTTP. Then inspect the response and stream. Do not pass this real PCAPNG to
`practice.py`. Its parser reads only the Ethernet frames it creates for practice.
Npcap loopback uses a different format for this layer of the packet.

## 4. Export the object, compare evidence, then save your explanation

Export through TShark, keeping the destination new and empty:

```powershell
New-Item -ItemType Directory -Path run/capture-01/output/http-objects
& $tshark -n -r run/capture-01/output/transfer.pcapng -d tcp.port==8765,http --export-objects http,run/capture-01/output/http-objects -q 2>&1 | Tee-Object -FilePath run/capture-01/output/export-log.txt
Get-ChildItem -LiteralPath run/capture-01/output/http-objects -File | Select-Object Name,Length | Out-File run/capture-01/output/export-inventory.txt
Get-FileHash run/capture-01/source/dummy.txt,run/capture-01/output/client-dummy.txt,run/capture-01/output/http-objects/dummy.txt -Algorithm SHA256 | Format-List | Out-File run/capture-01/output/object-hashes.txt
Get-FileHash run/capture-01/source/transfer.pcapng,run/capture-01/output/transfer.pcapng -Algorithm SHA256 | Format-List | Out-File run/capture-01/capture-after.txt
```

The expected export name is `dummy.txt`. If it is missing, stop and inspect the
packet table and export log. Do not use `client-dummy.txt` in its place. Do not
rename a different object to force a match. A tool version may choose another
name. In that case, record the name and link it to the `/dummy.txt` HTTP response
before you hash it. This task has one transfer, so the export folder should
contain one object.

You can use the Wireshark window in place of the TShark export command. Open the
copied capture and choose **File > Export Objects > HTTP**. Select the response
to `/dummy.txt` and save the object to a fresh `output/http-objects/` folder.
Keep the Wireshark version. Take a screenshot of the export dialog that shows
the object. Use the same byte count and hash checks. Do not run both exports
into the same folder.

Save `interpretation.txt` now. Name the actual stream, source size and exported
size. Cite all three object hashes. Also cite the capture hashes from before,
the copy and after. Explain whether these values show that you recovered this
whole known object. Name a capture limit. Check the capture log for errors and
drops. One matching object does not prove that every packet was captured.
It does not identify a user. Keep your first prediction. This real capture has
no answer key or automatic skill grade.

## 5. Stop and retain evidence

Keep your prediction and explanation, plus `setup.json`. Keep the tool versions,
interface list and capture log. Save `transfer-receipt.json`, the original
capture and the copy you inspected. Keep the packet table, exported object,
file lists and hashes too. Record each stage on its own: transfer, capture and
export. Note any step that failed or did not run. The helper's receipt does not
prove that a capture or export took place.

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8765 -ErrorAction SilentlyContinue
```

The helper should have closed its listener. Dumpcap should have exited. If an
unrelated listener now appears, record that fact. Do not stop it. Once review is
complete, use your file manager to remove only your exact attempt folder.
Clear read-only flags on dummy copies if needed. This task installs no service
and adds no firewall rule. There is no interface setting or VM change to undo.

## Limits and primary documentation

Tests of the local transfer helper are separate from tests of capture tools.
The package checks record which steps ran on the machine used to prepare the
lab. A real capture and export need their own saved evidence. Plain HTTP exposes
this dummy content. This task does not recover TLS plaintext or decrypt traffic.
It does not solve packet loss or rebuild all forms of TCP traffic.

- [Dumpcap manual](https://www.wireshark.org/docs/man-pages/dumpcap.html): interface selection, capture filter, snapshot length and automatic stop.
- [TShark manual](https://www.wireshark.org/docs/man-pages/tshark.html): reading a file, Decode As, disabled name resolution and object export.
- [Wireshark Export Objects](https://www.wireshark.org/docs/wsug_html_chunked/ChIOExportSection.html): GUI object export.
- [Npcap loopback documentation](https://npcap.com/guide/npcap-devguide.html): loopback device name and DLT_NULL framing.
