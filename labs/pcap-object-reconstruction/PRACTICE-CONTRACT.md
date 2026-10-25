# Maintained local entry point

Read this before changing or running `practice.py`.

- Command: `python practice.py run --scenario guided --out run/practical-01` (also changed/challenge).
- Inputs: choose one of the three supplied cases. The script will not accept your own source, drive, profile, URL or device.
- Output: a new folder directly inside this lab's `run/`. No existing folder is replaced. Read-only dummy sources go in `source/`. Working files go in `output/`. The evidence goes in `receipt.json`.
- Safety: reject paths that escape the allowed folder (traversal). Reject symlinks/reparse paths, which can redirect a path. Reject hard-linked input files, which share stored bytes with another name. Also reject files that are too large and names that are not safe. The script does not install tools, use the network or capture traffic. It does not change host settings or start child processes.
- Operation: make a valid classic PCAP with made-up Ethernet/IPv4/TCP frames. It has a plain HTTP response with a Content-Length. Read it from a read-only source copy. Check the frame layout and checksums. Put body bytes back in their stated positions. Export only the unbroken start where all bytes agree. Record whether the body is complete as well as the exported length. Use no sockets or capture interfaces.
- Receipt: save the actual times and values from the task. Include source SHA-256 before and after. A matching source hash checks the bytes. It does not check every metadata field, such as a file time.
- First evidence: `output/packet-log.json` holds only the input segments read from the packets and the export length/hash. Keep `output/feedback.json` and `receipt.json` closed until the learner saves their own account of the results.
- Exit: 0 means the task was recorded. A code of 2 means the input was not valid or the task had an error. A training result can be incomplete or contain a conflict. That result is evidence to inspect; it does not mean the script failed.
- Keep first attempts. Remove only the exact attempt folders the script made when you clean up. There are no system changes to undo.

## Separate real-transfer entry point

Read LOCAL-CAPTURE.md before running `loopback.py`.

- Commands: `python loopback.py prepare --out run/capture-01`, then `python loopback.py transfer --out run/capture-01`. Run the second command while the separate capture is active.
- Inputs: use one fresh attempt name. You cannot choose the host, port, URL, folder to serve or device. The helper serves only the fixed dummy bytes it creates.
- Operation: bind IPv4 `127.0.0.1:8765`. Use a direct local HTTP client to request `/dummy.txt`. Write a separate client copy, then close the server. Do not reuse or stop existing listeners. There are time limits on connection and handler waits.
- Capture/export: use existing Dumpcap and TShark/Wireshark by hand. Follow the exact loopback and filter steps in LOCAL-CAPTURE.md. The Python helper does not capture traffic or make a fake capture. It does not check that an export took place.
- Output: save the dummy file and blank forms for the learner's prediction and explanation. Save `setup.json`, the local client copy and `transfer-receipt.json`. Do not replace an existing successful transfer.
- Safety: this command uses loopback sockets only. It cannot serve a folder, use a proxy or reach an external host. It does not install tools, change user rights or change host settings. Capture and export tools must already work.
- Exit: 0 means the named prepare or transfer step finished. A code of 2 means the input or task had an error. Ctrl+C closes the active listener. Keep any partial capture. Record steps that failed or did not run.
