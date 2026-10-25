# Asset discovery and inventory

Compare a made-up Nmap XML scan with an approved list of devices. Decide what to check next about each device owner or service. These made-up cases were written for practice. They are not copied coursework. They do not show work done in a job.

## Before starting

Know the basics of IP addresses, TCP ports and services first. The DNS lab may help. You do not need Nmap installed or any job experience. Use Python 3.10+ with its built-in library. Run each command from this lab folder. Read the evidence, choose labels and fill in a worksheet. You do not need to write code.

Allow **35-45 minutes** for the first guided case. Spend 5 minutes on terms and scope, then 15 on your first choices. Allow 10 minutes to check and correct them. Spend 5-15 minutes on your reasons. Do the changed case and recall tasks as separate practice. No one has yet assessed your work or skill.

## Vocabulary

An **asset** is a device or service being tracked. A **port** is a numbered point used for network traffic. The **inventory** is the approved record. **Open** means the saved scan saw a service listening on a port. **Filtered** means the probe could not tell if the port was open or closed. **Scope** means the addresses allowed in this made-up review.

## Evidence and exact input model

You get a small XML export in Nmap form. You also get an approved scope and a list of expected TCP ports.

Each case needs `schema_version: 1` and `lab_id: "asset-discovery"`. The `case_id` is `guided`, `changed` or `challenge`. It also needs `title`, `synthetic: true`, `context`, `data` and `artifacts`. No other top-level fields are allowed. `context.question` must contain text. Each object must have the listed fields and no others. Each record ID must be a unique lowercase name. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). The files use UTF-8 JSON and are small. Where needed, prepare also makes a copy of the evidence that you can read.

`data` has only three fields: `scope`, `approved` and `nmap_xml`. In `scope`, use unique IPv4 text strings reserved for examples. Each `approved` record has `ip`, `owner` and `expected_tcp_ports`. The owner is a made-up lowercase name. The port list uses unique whole numbers from 1 to 65535. `nmap_xml` holds text. This XML is the source used for results. `artifacts.scan.xml` must be an exact copy you can read.

The XML starts with `nmaprun scanner="nmap"`. It contains `host` elements. Each host needs `status state="up|down"` and `address addr="..." addrtype="ipv4"`. It may also have `ports/port protocol="tcp" portid="..."/state state="open|closed|filtered"`. Keep the order: status, address, then ports. No extra attributes are allowed. Declarations, DTDs, entities, service names and UDP are also rejected. A down host must have no port results. All scan and inventory hosts must be in scope. A repeated host or port is an error.

## Decision vocabulary

| Label | Exact meaning |
|---|---|
| `not-observed-in-scan` | An approved IP has no scan host record. |
| `not-observed-up` | The saved record says down; removal is not established. |
| `unregistered-host-observed` | An up host has no approved inventory record. |
| `unapproved-service-observed` | An approved up host has at least one unexpected open TCP port. |
| `expected-service-not-observed` | No unexpected open port, but at least one expected port was not observed open. |
| `expected-services-observed` | Observed open ports equal expected ports, including an empty expected set. |

Use the rules in the order shown. An unexpected open port takes priority over an expected port that was not seen open. Keep both facts in your notes. A closed, filtered or unlisted port does not show the expected service open. These three states still mean different things. Keep those details from the evidence.

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

Make an inventory table with one row for each decision. Show the open ports seen, the expected ports and the source. Add what is unknown and what you would check with the owner. Keep your first choices and any corrections in the notes. State what help you used. Use [the worked example](WORKED-EXAMPLE.md) for the guided case. Use [the drills](DRILLS.md) to try tasks with less help over time.

In your handover, answer: "What did you see? Which exact evidence supports it? What is still unknown? What small check should happen next?" Ask someone to review your reasons and your work on a new case. Until then, your skill without help has not been assessed.

## Limits and primary references

- A saved scan shows what was seen at one time. It does not prove who owns a host, that it has a security flaw, or that the scan saw all hosts and ports.
- The tool reads only the XML form described here. It accepts the TCP states open, closed and filtered. It does not run a scan.

The lab runs offline. It contacts no outside target, sends no packets or email, and changes no host settings. All names and addresses are reserved for made-up examples. The rules were chosen for this lesson. The sources explain the ideas behind them. They do not certify this tool.

- [Nmap: XML output](https://nmap.org/book/output-formats-xml-output.html)
- [Nmap: port scanning basics and port states](https://nmap.org/book/man-port-scanning-basics.html)
