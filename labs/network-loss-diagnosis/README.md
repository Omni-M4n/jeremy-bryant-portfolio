# Diagnose latency, loss and failed connections

A camera misses part of a delivery. The missing picture does not mean the parcel was lost. A network capture also records only what its collection point saw. This lab asks **what repeated bytes, replies and time gaps show without jumping to a cause**.

This extends [tcp-handshake](../tcp-handshake/README.md) by following data after a connection begins. It adds byte ranges, request times, resets and gaps in the saved traffic. First complete tcp-handshake and traffic-capture. Allow 30 minutes now and 10 minutes for later recall.

## Words before fields

**Latency** is delay. **Loss** means traffic failed to reach a point where it was needed. A **capture** is a saved record of packets. **Capture drops** are packets the capture system reports missing from its record. These differ from network loss. A **sequence number** marks a byte's place. An **ACK**, or acknowledgement, tells the sender the next byte expected. **Retransmission** is sending bytes again. A **reset** ends a TCP connection at once. **Milliseconds**, written ms, are thousandths of a second.

## Run the supplied extract

Python 3.10+ on Windows, Linux or macOS, standard library only. No traffic is sent or captured.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `data.packets` in the displayed case as the only packet evidence. Use the Answer vocabulary table below to write labels. Keep the reference answers closed. Draw time down the page with one column per endpoint. An endpoint is one end of the connection. Add the byte ranges and ACK values. Save your first view and complete `answers.json` before opening references:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The JSON rows are a made-up packet extract. They are not a PCAP capture file or real collected data. `data.packets` is the sole packet evidence. The `artifacts` object must be empty. The analyser rejects a case that has a second artifact copy. It does not choose between copies that might conflict. A person still needs to review your written reasons. Do not claim that these checks show you captured packets yourself.

## Answer vocabulary: use before opening any reference

The worksheet has five fixed entries. Choose a value for each on its own. A repeated range, missing packet and reset can appear together. This guide gives every valid label spelling. It does not give a case's answers.

| Worksheet entry | Exact label or template | Meaning |
| --- | --- | --- |
| `repetition` | `repeated-range-observed` | At least one exact byte range appears more than once from the same side. |
| `repetition` | `no-repeat-in-extract` | No exact repeated range appears in this extract. |
| `acknowledgement` | `unseen-bytes-acknowledged` | At least one ACK extends beyond the other side's contiguous captured bytes at that point. |
| `acknowledgement` | `no-unseen-ack-in-extract` | No such ACK appears in the extract. |
| `termination` | `reset-observed` | A reset row appears. |
| `termination` | `no-reset-in-extract` | No reset row appears in the extract. |
| `timing` | `request-ack-to-response:<N>ms` | Both required events exist and the first server data is at or after the first complete request ACK. Replace `<N>` with their time difference as a whole number, including zero. Do not include angle brackets or spaces. |
| `timing` | `insufficient-timing-evidence` | Either required event is absent, or the first server data comes before the complete request ACK. |
| `capture` | `capture-drops-reported:<N>` | The supplied capture-drop count is positive. Replace `<N>` with that whole count, without angle brackets or spaces. |
| `capture` | `no-local-drops-reported` | The supplied capture-drop count is zero. |
| `capture` | `drop-count-unavailable` | The supplied capture-drop count is null, meaning unavailable. |

No label overrides another worksheet entry. The timing check uses the complete-request boundary described below. No label proves network loss or its cause. Combining labels does not prove it either. Add frame references and written reasons.

## Exact small model

One TCP flow is already set up. Its two starting data sequence numbers are `client_start` and `server_start`. `request_bytes` marks the full request size. The capture has one clock. Its drop count is a whole number of zero or more, or null if unknown. There are at most 60 rows. Each has its own neutral frame ID and a client/server side. Times use whole milliseconds and never move backwards. Each row shows a data, acknowledgement or reset event. Real packets can combine these roles. This teaching format splits them.

Data has a starting `seq`, positive `length`, and null `ack`. It covers `[seq, seq + length)`. So a 100-byte range starting at 1000 ends just before 1100. ACK rows have null `seq`, zero length and an `ack` value for the other side's stream. Reset rows have null seq/ack and zero length. Client data and its acknowledgements cannot go past the one supplied request boundary. Numbers have set limits. Wrapping, where a sequence number starts again at zero, is rejected. So are SYN/FIN bytes, which mark the start/end of a connection, and window updates, which change how much data may be sent. Partial overlaps and rows after reset are rejected too. Exact repeated ranges are allowed. Ranges may be out of order if they do not overlap.

The helper marks a repeated exact range. It does not decide if the sender sent it again or the capture recorded it twice. It sorts seen byte ranges to find the first gap. An ACK may go past the unbroken range of captured bytes. This marks bytes that were acknowledged but not captured before that ACK. It does not prove that bytes were lost on the way. The ACK is evidence that those bytes reached the receiver. The capture may have dropped packets or used a different path. Packets may have reached the capture point out of order. The extract may also be incomplete.

For timing, the helper finds the first server ACK that reaches the request boundary. It also finds the first server data row. If the data comes at or after that ACK, it subtracts the times. This gap includes work at the endpoints and time spent moving data. It is not just a delay within the program. It is not an RTT, the time for a round trip, either. If the data comes first or either event is missing, the timing evidence is not enough. A reset is recorded without saying which device sent it or why. A zero local drop count does not prove that the capture is complete.

## Edit one authoritative packet input

1. Prepare a fresh attempt folder using the commands above, keeping earlier attempts unchanged. In a text editor, open its `case.json` and use Save As to create `case-edited.json` beside it.
2. Change only one `at_ms` number inside `data.packets`, keeping times in order. Leave `artifacts` as `{}`. Save your predicted interval in a separate note before running the analyser. Do not create a CSV or another packet copy inside the case.
3. Read back the edited input, then compare your prediction. For an attempt in `run/attempt-01`, the commands are:

```text
python lab.py show --case run/attempt-01/case-edited.json
python lab.py analyse --case run/attempt-01/case-edited.json
```

The displayed rows and analysed rows now come from the same input. Keep `case.json`, its original answers and your first prediction intact. If you want to check an edited worksheet, save it as `answers-edited.json` and pass that filename with the edited case to `check`.

Older attempt folders may contain `frames.csv` and a matching artifact entry. Keep those first attempts as past evidence. The current analyser rejects their extra packet copy, even when the copies match. Prepare a fresh case for this version. Do not delete evidence from the old attempt. If an old case is missing or rejected, that is not a learner error. It says nothing about the old answer.

## Investigate without changing a network

Use the supplied `data.packets` rows first. Make a three-column table: possible cause, evidence for/against it, next check. A proposed cause is called a hypothesis. For repeated bytes, consider a sender retry and a capture made twice. For a delay, compare endpoint logs and the time taken to process requests. For an unseen range, check the capture counts and where it was taken. Do this before claiming network loss. For a reset, seek matching endpoint evidence.

You may already have a saved capture from your owned isolated lab, with permission to use it. If so, open a copy in an already installed Wireshark. Keep the original. Use `tcp.stream == N` for one stream selected in the packet details. N must come from that capture. Inspect `tcp.analysis.retransmission`, `tcp.analysis.ack_lost_segment`, `tcp.analysis.lost_segment` and `tcp.flags.reset == 1` one at a time. Save frame numbers, sequence/ACK values and the capture's location. Keep any known drop counts too. Tool flags are clues based on the order of seen packets. They do not prove a cause. Do not open unrelated personal or third-party traffic. This optional saved-capture review has not been run for this package. No live capture or network change is required.

## Evidence and handover

Save the flow timing chart, byte ranges and first predictions. Keep the hypothesis table, evidence against your view and one small next check. Label made-up, personal and missing evidence clearly. Handover: ask another learner which claim would fail if the capture were incomplete. Keep first attempts. You may remove your own duplicate run files once you have saved the evidence you need.

## Primary references

Opened 2026-10-25:

- [Wireshark TCP analysis and sequence-based flags](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html)
- [RFC 9293, TCP sequence, acknowledgement and reset behaviour](https://www.rfc-editor.org/info/rfc9293/)
