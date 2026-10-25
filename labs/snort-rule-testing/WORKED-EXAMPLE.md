# Worked reasoning: marker rule

These are guided predictions from the packet plan and rule text. They are not a record of a Snort run. Save your first prediction before reading this. Keep your real evidence in a fresh run folder.

The original rule needs both a matching header and exact bytes. In `positive.pcap`, frame 4 goes from `192.0.2.10:45000` to `198.51.100.20:18080`. The HTTP request has the uppercase marker. Predict one SID 1000001 alert. Then inspect the actual alert object and its packet number. Do not report a prediction as something you saw.

`near-miss.pcap` has the same endpoints and port. Its marker is lowercase. Without `nocase`, it does not match the content. Predict zero. The controls were set before the engine ran. The packet writer does not read the rule to make up an expected result.

`negative.pcap` has `ORDINARY-BOOKING-42`. This harmless text differs from the rule's content. Predict zero. `wrong-port.pcap` has the exact uppercase marker. But it sends to port 18081, which the rule's header does not match. Predict zero there too. A search for the marker alone would miss the port condition.

For the changed test, close this answer. Use the rule options to make your own prediction for each file. Save it before you run the engine. Check any mismatch against the exact rule and command. If all four cases show zero, check the positive control. Read the exit codes, stderr and rule identity. An engine that failed to run gives no detection evidence.

The wrapper stores `version.txt`, the final rule and `result.json`. It also stores `command.json`, `stdout.txt`, `stderr.txt` and `input.pcap` for each case. The command reads offline PCAP input. It does not open a capture interface. Matching counts support this exact test. They do not prove the rule can detect all attacks.

A useful guided finding is: "I used rule revision ___ and Snort version ___. The positive control produced ___ SID 1000001 alerts. The near-miss produced ___. The other controls produced ___. The raw output in ___ supports these counts. These are harmless test markers." Fill this with your real results.

If Snort is absent, report only work you actually did. You could write: "I generated the made-up packet files and checked their structure. I predicted the rule outcomes. Snort execution is pending." Do not fill blanks with expected counts as if you saw them.
