# TCP handshake investigation

Read packet order and flags, then work out the next sequence numbers. Use them to tell a seen opening handshake from a reset or a gap in the evidence. These made-up cases were written for practice. They are not copied coursework. They do not show work done in a job.

## Before starting

Know client and server roles, IP addresses and ports first. Basic Wireshark skills may help, but you can start without them. This lab does not install or use a packet capture tool. Use Python 3.10+ with its built-in library. Run each command from this lab folder. Read the evidence, choose labels and fill in a worksheet. You do not need to write code.

Allow **35-45 minutes** for the first guided case. Spend 5 minutes on terms and scope, then 15 on your first choices. Allow 10 minutes to check and correct them. Spend 5-15 minutes on your reasons. Do the changed case and recall tasks as separate practice. No one has yet assessed your work or skill.

## Vocabulary

**SYN** starts the exchange of sequence numbers. **ACK** says the acknowledgement field has meaning. **RST** signals a reset. **SEQ** is the sequence number. A **retransmission** is another copy of the same opening segment seen in the capture. A **capture gap** means traffic is missing from the view you have.

## Evidence and exact input model

You get made-up packet summaries. They list flow IDs, endpoints, frame order, direction and flags. They also show raw 32-bit sequence and acknowledgement numbers.

Each case needs `schema_version: 1` and `lab_id: "tcp-handshake"`. The `case_id` is `guided`, `changed` or `challenge`. It also needs `title`, `synthetic: true`, `context`, `data` and `artifacts`. No other top-level fields are allowed. `context.question` must contain text. Each object must have the listed fields and no others. Each record ID must be a unique lowercase name. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). The files use UTF-8 JSON and are small. Where needed, prepare also makes a copy of the evidence that you can read.

`data.flows` must have at least one flow. Each flow has only `id`, `client`, `server`, `server_port`, `capture_note` and `packets`. The client and server must use different IPv4 addresses reserved for examples. The server port is from 1 to 65535. The capture note is text.

Each packet has `frame`, `direction`, `flags`, `seq` and `ack`. Frame numbers are positive whole numbers. They must rise within each flow. Direction is `c2s` or `s2c`. Sequence numbers range from 0 to 4294967295. The ack uses the same range, or null for SYN. Only these flags are allowed: `SYN`, `SYN-ACK`, `ACK`, `RST-ACK`. SYN and ACK go from client to server. SYN-ACK and RST-ACK go from server to client. The JSON packets are the source used for results. `artifacts.packets.csv` must match them exactly.

Each flow holds one opening attempt with no payload. The initial SYN may repeat. After it, an optional SYN-ACK may repeat with the same values. At most one final ACK follows. A reset ends the excerpt. The tool rejects separate attempts in one flow, repeats that differ, and other packet orders.

A capture may start late. In that case, it accepts one or more identical SYN-ACKs, with or without one final ACK. It also accepts a lone ACK or a lone RST-ACK. It rejects other late-capture orders and SYN-ACK repeats that differ. This still applies when the initial SYN is missing. Without that first SYN, the capture remains incomplete even if the later packets look right.

## Decision vocabulary

| Label | Exact meaning |
|---|---|
| `handshake-observed` | SYN, matching SYN-ACK and matching final ACK are all present. |
| `reset-observed` | A server-direction RST-ACK acknowledges the initial SYN. |
| `no-response-observed` | Only one or more identical client SYNs appear. |
| `final-ack-not-observed` | Matching SYN-ACK is present, but final ACK is absent. |
| `initial-syn-not-observed` | No initial client SYN is in the excerpt. |
| `acknowledgement-mismatch` | A response ACK or final SEQ/ACK differs from the expected numbers. |

A SYN uses one sequence number. Work out the next number as `(sequence + 1) modulo 4294967296`. This wraps 4294967295 back to 0. You need more than a flag to choose a label. The labels describe only this excerpt. They do not tell you the final connection state or its cause.

## Run the practice

Use a new attempt number if that folder already exists. Prepare writes only inside this lab's ignored `run/` folder. It rejects paths that already exist or use links.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and its evidence. Save your first choices before you view the analysis. Edit `run/attempt-01/answers.json`. Fill each blank decision with an exact label from the table. Write a paragraph in `explanation`. In the `evidence` list, cite the records, fields or lines you used. One entry can give a record ID and its field name. In `notes.txt`, keep your first choices, doubts, next check and help used. JSON text strings need double quotes. Do not add comments or a comma after the last item.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Repeat show/check/analyse with the path for your new attempt. The default case is `fixtures/guided.json`, beside the script. Input paths that you supply start from your current folder. The prepare output path starts from this lab folder.

Exit 0 means the command worked or your decision fields match. Exit 1 means a choice differs or your worksheet is incomplete. Exit 2 means the input is invalid or there is a file error. Analyse shows the set answers and reasons. Keep it closed until you save your first choices. Verify compares the three supplied cases with fixed expected outputs. It does not assess your skill. Check requires written reasons and sources. It cannot judge whether they are right.

## Deliverable and handover

Make a flow table. For each choice, cite the exact packets and show how you worked out the expected ACK numbers. Add one limit of the capture. Keep your first choices and any corrections in the notes. State what help you used. Use [the worked example](WORKED-EXAMPLE.md) for the guided case. Use [the drills](DRILLS.md) to try tasks with less help over time.

In your handover, answer: "What did you see? Which exact evidence supports it? What is still unknown? What small check should happen next?" Ask someone to review your reasons and your work on a new case. Until then, your skill without help has not been assessed.

## Limits and primary references

- Missing packets may be due to where the capture was taken, packet loss or a short capture. They do not prove a firewall or server fault.
- Each flow supports one ordinary opening attempt with no payload. The tool does not decode packets or model the full TCP state.

The lab runs offline. It contacts no outside target, sends no packets or email, and changes no host settings. All names and addresses are reserved for made-up examples. The rules were chosen for this lesson. The sources explain the ideas behind them. They do not certify this tool.

- [IETF RFC 9293, section 3.5: establishing a TCP connection](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.5)
