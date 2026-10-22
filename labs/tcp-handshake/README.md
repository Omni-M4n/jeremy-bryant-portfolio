# TCP handshake investigation

Use packet order, flags and sequence arithmetic to distinguish an observed opening handshake, an observed reset and incomplete evidence. These are original fictional practice cases, not copied coursework or completed professional work.

## Before starting

Prerequisites: Client/server roles, IP addresses and ports; basic Wireshark familiarity helps but is not required. No packet capture tool is installed or used. Use Python 3.10+ with the standard library. Run the commands from this lab folder. The learner reads evidence, makes decisions and edits a worksheet; programming is not required.

Allow **30-45 minutes** for the first guided pass: 5 minutes for vocabulary and scope, 15 for prediction, 10 for checking and correction, and 5-15 for explanation. Changed and later recall exercises are separate practice. Personal completion and independent competence have not been assessed.

## Vocabulary

**SYN:** begins sequence synchronisation. **ACK:** marks an acknowledgement field as meaningful. **RST:** a reset indication. **SEQ:** the sequence number. **Retransmission:** another observation of the same opening segment. **Capture gap:** traffic absent from the supplied view.

## Evidence and exact input model

Synthetic packet summaries with flow IDs, endpoints, frame order, direction, flags and raw 32-bit sequence/acknowledgement numbers.

Each case has exactly `schema_version: 1`, `lab_id: "tcp-handshake"`, `case_id` (`guided`, `changed`, `challenge`), `title`, `synthetic: true`, `context`, `data`, `artifacts`. `context.question` is nonempty text. Objects reject unknown/missing fields; record IDs are unique lowercase names. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). Files are small UTF-8 JSON; readable artifacts are supplied through prepare where relevant.

`data.flows` is a nonempty list. Each flow has exactly `id`, `client`, `server` (different documentation IPv4 addresses), `server_port` (1-65535), `capture_note` (text), and `packets`. Each packet has `frame` (strictly increasing positive integer within its flow), `direction` (`c2s` or `s2c`), `flags`, `seq` (0-4294967295), and `ack` (same range, or null for SYN). Flags are only `SYN`, `SYN-ACK`, `ACK`, `RST-ACK`; SYN/ACK are client direction and SYN-ACK/RST-ACK server direction. JSON packets are authoritative; `artifacts.packets.csv` mirrors them exactly. Each flow is one opening attempt with no payload: initial SYN repeats, optional identical SYN-ACK repeats, then at most one final ACK; a reset ends the excerpt. Distinct attempts, inconsistent retransmissions and unsupported ordering are rejected. Supported late-capture suffixes are one or more identical SYN-ACKs with an optional single final ACK, a lone ACK, or a lone RST-ACK. Other suffix orders and inconsistent SYN-ACK repeats are rejected even when the initial SYN is absent. A supported capture without its initial SYN remains incomplete even if later packets look plausible.

## Decision vocabulary

| Label | Exact meaning |
|---|---|
| `handshake-observed` | SYN, matching SYN-ACK and matching final ACK are all present. |
| `reset-observed` | A server-direction RST-ACK acknowledges the initial SYN. |
| `no-response-observed` | Only one or more identical client SYNs appear. |
| `final-ack-not-observed` | Matching SYN-ACK is present, but final ACK is absent. |
| `initial-syn-not-observed` | No initial client SYN is in the excerpt. |
| `acknowledgement-mismatch` | A response ACK or final SEQ/ACK differs from the expected numbers. |

A SYN consumes one sequence number; compute next as `(sequence + 1) modulo 4294967296`. A flag alone is insufficient. These labels describe this excerpt, not the eventual connection state or cause.

## Run the practice

Use a new attempt number if the destination already exists. Prepare writes only beneath this lab's ignored `run/` folder and refuses existing or linked paths.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and its readable evidence. Before viewing the analysis, edit `run/attempt-01/answers.json`: replace every blank decision with an exact label above, write `explanation` as a paragraph, and put record/field/line references in the `evidence` list. Keep predictions, uncertainty, next check and help used in `notes.txt`. JSON strings use double quotes; do not add comments or trailing commas. An evidence entry can be a record ID plus the relevant field name.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Repeat show/check/analyse with the new attempt path. Default case is `fixtures/guided.json` beside the script. Explicit input paths are relative to your current directory; prepare output is relative to this lab. Exit 0 means command success or matching decision fields, 1 means differences/incomplete worksheet, and 2 means invalid input or a filesystem error. Analyse shows the reference reasoning and should stay closed until a prediction is saved. Verify compares three shipped fixtures with fixed reference outputs; it does not assess a learner. Check requires prose and references but cannot judge their accuracy.

## Deliverable and handover

A flow table with each decision, exact packet references, expected acknowledgement arithmetic and a capture limitation. Keep your first prediction and correction in the notes. Include an honest help-used statement. Use [the worked example](WORKED-EXAMPLE.md) for the guided case and [the drills](DRILLS.md) to reduce prompts over time.

Handover prompt: "What did you observe, which exact evidence supports it, what remains uncertain, and what narrow check should happen next?" A person should review your reasoning and an unfamiliar case before treating the practice as independently demonstrated.

## Limits and primary references

- Missing packets can reflect capture position, loss or a short capture; they do not prove a firewall or server fault.
- Only one ordinary, payload-free opening attempt per flow is supported; this is not a packet decoder or TCP state implementation.

Runtime is offline: no external target, packet transmission, email action or host configuration change occurs. All addresses and names are reserved fictional examples. The local decision rules are teaching choices; the references explain underlying concepts, not a claim of tool certification.

- [IETF RFC 9293, section 3.5: establishing a TCP connection](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.5)
