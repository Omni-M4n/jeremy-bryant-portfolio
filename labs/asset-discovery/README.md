# Asset discovery and inventory

Compare a saved synthetic Nmap XML excerpt with an approved asset inventory and identify the next ownership or service check. These are original fictional practice cases, not copied coursework or completed professional work.

## Before starting

Prerequisites: Basic IP addresses, TCP ports and services; the DNS investigation lab is useful. No Nmap installation or previous professional experience is needed. Use Python 3.10+ with the standard library. Run the commands from this lab folder. The learner reads evidence, makes decisions and edits a worksheet; programming is not required.

Allow **30-45 minutes** for the first guided pass: 5 minutes for vocabulary and scope, 15 for prediction, 10 for checking and correction, and 5-15 for explanation. Changed and later recall exercises are separate practice. Personal completion and independent competence have not been assessed.

## Vocabulary

**Asset:** a device or service being tracked. **Port:** a numbered transport endpoint. **Inventory:** the approved record. **Open:** the saved probe observed a listening service. **Filtered:** the probe could not determine the usual open/closed state. **Scope:** the addresses included in this fictional review.

## Evidence and exact input model

A small Nmap-shaped XML export, an explicit authorised scope and an inventory of expected TCP ports.

Each case has exactly `schema_version: 1`, `lab_id: "asset-discovery"`, `case_id` (`guided`, `changed`, `challenge`), `title`, `synthetic: true`, `context`, `data`, `artifacts`. `context.question` is nonempty text. Objects reject unknown/missing fields; record IDs are unique lowercase names. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). Files are small UTF-8 JSON; readable artifacts are supplied through prepare where relevant.

`data` has exactly `scope` (unique documentation IPv4 strings), `approved` (records with `ip`, a lowercase fictional `owner`, and unique integer `expected_tcp_ports` from 1 to 65535), and `nmap_xml` (text). The XML is authoritative; `artifacts.scan.xml` must be an exact readable mirror. The supported XML grammar is `nmaprun scanner="nmap"` containing `host` elements with `status state="up|down"`, `address addr="..." addrtype="ipv4"`, and optional `ports/port protocol="tcp" portid="..."/state state="open|closed|filtered"`. Element order is status, address, ports. No extra attributes, declarations, DTDs, entities, service names or UDP are accepted. A down host has no port results. All scan/inventory hosts must be in scope; duplicate hosts or ports are errors.

## Decision vocabulary

| Label | Exact meaning |
|---|---|
| `not-observed-in-scan` | An approved IP has no scan host record. |
| `not-observed-up` | The saved record says down; removal is not established. |
| `unregistered-host-observed` | An up host has no approved inventory record. |
| `unapproved-service-observed` | An approved up host has at least one unexpected open TCP port. |
| `expected-service-not-observed` | No unexpected open port, but at least one expected port was not observed open. |
| `expected-services-observed` | Observed open ports equal expected ports, including an empty expected set. |

Evaluate in that order. Unexpected open ports take precedence over missing expected ports, but observations retain both gaps. Closed, filtered and omitted ports all fail to demonstrate an expected open service; their underlying states still differ in the evidence.

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

An inventory table with one row per decision, observed open ports, expected ports, a source reference, uncertainty and a proposed owner check. Keep your first prediction and correction in the notes. Include an honest help-used statement. Use [the worked example](WORKED-EXAMPLE.md) for the guided case and [the drills](DRILLS.md) to reduce prompts over time.

Handover prompt: "What did you observe, which exact evidence supports it, what remains uncertain, and what narrow check should happen next?" A person should review your reasoning and an unfamiliar case before treating the practice as independently demonstrated.

## Limits and primary references

- A saved scan is a time-limited observation, not proof of ownership, vulnerability or complete coverage.
- Only this documented XML subset and TCP states open, closed and filtered are supported; no scanning occurs.

Runtime is offline: no external target, packet transmission, email action or host configuration change occurs. All addresses and names are reserved fictional examples. The local decision rules are teaching choices; the references explain underlying concepts, not a claim of tool certification.

- [Nmap: XML output](https://nmap.org/book/output-formats-xml-output.html)
- [Nmap: port scanning basics and port states](https://nmap.org/book/man-port-scanning-basics.html)
