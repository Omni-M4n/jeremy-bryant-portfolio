# Recover a benign object from your own HTTP capture

A page sent in several envelopes is usable only if every part arrives and repeated parts agree. TCP packets carry numbered pieces in a similar way.

**Question:** Are the captured object bytes complete, consistent and equal to the known dummy object?

This extends `traffic-capture`. You transfer a dummy file on your own computer, capture the traffic and export its HTTP object. Then you use separate made-up cases to study gaps and packet bytes that conflict.

## Before you start

Use Python 3.10 or later with its built-in tools, called the standard library. Your own capture also needs an existing Wireshark install on Windows. TShark, Dumpcap and Npcap loopback capture must already work. Loopback sends traffic back to the same computer. Stop and record any missing tool or access. Do not install tools or change settings for this task. Open a terminal in this lab folder. The commands use `python`. Use your own Python command if it has a different name. Read `traffic-capture` and `file-integrity` first. Allow 20-30 minutes for your own capture and 25-40 minutes for the made-up cases. Set aside ten more minutes to recall the steps later.

These materials were made for this lab. Use only the dummy data the script creates. Keep coursework, real disks and browser profiles out of this task. The program takes a case name and a new output folder name. It does not accept a path to a device or personal data.

## Useful words

- **PCAP:** a file that stores packet records.
- **TCP sequence:** a number locating bytes within a connection.
- **HTTP object:** content carried in an HTTP response.
- **overlap:** two packet pieces claiming the same byte positions.

## Required own-capture operation

Follow [LOCAL-CAPTURE.md](LOCAL-CAPTURE.md) to prepare a dummy file and save what you expect to find. Then capture one real plain-HTTP loopback transfer. Keep the capture safe, export its object and compare hashes. The guide gives the exact interface and filter to use. It also covers the evidence to keep, when to stop and how to clean up. `loopback.py` runs only the local transfer. It does not make a capture or claim that an export ran. Keep the client download and the object exported from the capture separate.

If capture tools are missing, record that limit. Your own capture remains incomplete even if the made-up cases below pass. VALIDATION.json records evidence from the machine used to prepare the lab. It does not record your progress.

## Separate simulated-packet practice

1. Run `python lab.py prepare --scenario guided --out run/attempt-01`.
2. Run `python lab.py show --case run/attempt-01/case.json`. Read the small input. It is a made-up example supplied with the lab. It does not describe your machine.
3. Save what you expect to find in `run/attempt-01/notes.txt`. Cite the evidence and name one thing you do not yet know. Fill the blank decisions in `answers.json` using the terms below. Do this before you run the reference command.
4. Run `python practice.py run --scenario guided --out run/practical-01`. This runs the made-up case described below. Keep its `receipt.json` and `output/feedback.json` closed until you save your own explanation.
5. Read only `run/practical-01/output/packet-log.json` and the exported `output/item-01.bin` first. The log lists body pieces read from packets, plus the export length and hash. Count positions in the body, not packets. Check for missing positions and overlaps. Save what you think the evidence shows in `run/practical-01/interpretation.txt`. The exported start of the body may be shorter than Content-Length, its stated size. The source PCAP was made for training.
6. After saving both answers, run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then use `python lab.py analyse --case run/attempt-01/case.json` and read `output/feedback.json`, `receipt.json` and WORKED-EXAMPLE.md.

The script makes a valid classic PCAP with made-up Ethernet/IPv4/TCP frames. It includes a plain HTTP response with a Content-Length. It reads a read-only source copy and checks the frame layout and checksums. It puts body bytes back in their stated positions. It exports only the unbroken start where all bytes agree. Record whether the body is complete as well as the exported length. The script uses no sockets or capture interfaces.

Use a new folder name for each try. The script refuses folders that already exist. Check the supplied worksheet against its model answer. Check your local task against its own receipt. Keep those two checks separate. Do not use the worksheet's made-up times in your report of the task you ran.

## What the model accepts

content_length is 1-4096. known_sha256 is the dummy object hash. Plaintext means bytes that are not encrypted. Each plaintext segment has a neutral ID, an offset and hex bytes. The offset counts from the start of the HTTP body. Exact duplicates are allowed. If bytes at the same position conflict, the model does not choose one without reporting the conflict. encrypted=true requires an empty segment list.

Check the encrypted-only case first. For plaintext, check overlaps that conflict before missing positions. Compare the known hash only when the whole body is present and all overlaps agree.

The outer JSON fields are described in `../FOUNDATION-CONTRACT.md`. Fields the model does not support cause an error. So do repeated IDs, badly formed values and inputs that conflict. `lab.py` reads evidence without changing it. The local task creates its source files in a fresh `run/` folder. It marks them read-only and checks their hashes after use. Copies and outputs stay in that same attempt. A read-only flag does not prevent all changes to file metadata.

## Complete answer vocabulary

Use these exact strings in the matching decision fields. The worksheet names each field. Explain the evidence for each choice in your own words.

| Decision value | Exact meaning |
| --- | --- |
| `complete-matches-known-object` | Every byte position is present, overlaps agree and SHA-256 matches the known object. |
| `complete-object-differs` | All byte positions are present and agree but the known hash differs. |
| `stream-incomplete` | At least one expected byte position is missing. |
| `conflicting-overlap` | Two captured segments give different values at the same position. |
| `encrypted-no-plaintext` | Only encrypted traffic is represented; no body can be recovered by this model. |

WORKED-EXAMPLE.md explains the guided answer. Use DRILLS.md to try a fresh case on your own.

## Evidence to keep

For own capture, keep every artifact listed in LOCAL-CAPTURE.md. For simulated cases, keep your first `answers.json`, notes, practical interpretation, input `case.json`, `receipt.json`, and the files in that practical's `source/` and `output/` folders. Use the neutral item IDs and exact output fields. State what the evidence shows. Give another way to explain it and one next check. A worksheet match checks your choices only. A person still needs to review your reasons.

## Verification and cleanup

Run `python test_lab.py` and `python lab.py verify` to check this package. Tests make temporary folders under this lab's `run/`. They do not edit the supplied cases. Passing tests does not assess your skill. See VALIDATION.json for the saved package checks and which local tasks ran.

The made-up cases start no service. The helper for your own capture closes its listener. Use LOCAL-CAPTURE.md to check that Dumpcap has stopped too. There is no system setting to restore. Keep the attempts until the review is done. Then use your file manager to remove only the exact attempt folders you made inside this lab's `run/`. Some dummy source copies are read-only. You may need to clear that flag on those copies first. Keep the lab source files. Do not clean up any other folder.

## Limits and unrun work

- The generated PCAP was made by the script, not collected from a network. The parser handles one small plain HTTP/1.1 response. It has Content-Length, fixed IPv4/TCP headers and no TLS.
- A complete matching object does not identify a user. Missing packets, encrypted data and overlaps that conflict need their own checks. So do chunked bodies and compressed data.

- Follow LOCAL-CAPTURE.md for the required real capture. The local HTTP transfer helper was tested. The checked capture tools were not available on the machine used to prepare the lab. Capture and TShark/Wireshark export did not run there; see VALIDATION.json.
- The small practice parser does not accept real captures. Your own capture uses existing Wireshark/TShark to read its real PCAPNG. This lesson does not build a general tool to reassemble TCP or decrypt TLS. It does not cover chunked/compressed HTTP, IPv6 or IP fragments.

## Primary references

These pages were opened to prepare this lab on 25 October 2026. SOURCES.json states why each page was used. The text and training files were made for this lab. They contain no third-party dataset or coursework.

- [Wireshark User Guide, Export Objects](https://www.wireshark.org/docs/wsug_html_chunked/ChIOExportSection.html): Required own-capture export workflow; preparation-machine capture/export remains unrun.
- [RFC 9112, HTTP/1.1 message framing](https://www.rfc-editor.org/rfc/rfc9112.html): Content-Length body framing and incomplete messages.
- [IETF PCAP format draft 05 (historical draft)](https://www.ietf.org/archive/id/draft-ietf-opsawg-pcap-05.html): Classic PCAP layout; historical draft, not presented as a final standard.
- [libpcap current public header](https://raw.githubusercontent.com/the-tcpdump-group/libpcap/master/pcap/pcap.h): Current file format version and header fields; source consulted, no code copied.

## Execution status

Your own capture and the made-up cases have separate evidence. Follow LOCAL-CAPTURE.md for the full real task. Never relabel receipts for generated packets as capture receipts. Test results do not prove that a capture or export ran. They do not assess your skill.
