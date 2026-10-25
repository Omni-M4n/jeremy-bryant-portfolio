# Run a scoped Nmap service inventory

A room has three numbered doors. One opens, one is shut, and one gives no clear reply. The number on a door does not tell you who is inside. Network ports do not work just like doors. But the same care helps here. An open port and a guessed service name tell you different things.

This extends [asset-discovery](../asset-discovery/README.md). It adds a scan that you collect within strict limits. You then compare it with the waiting programs on the target. First complete asset-discovery, tcp-handshake and isolated-lab-workbench. Allow 20 minutes for supplied evidence and 30-45 minutes for the VM session.

## Words before fields

A **port** is a numbered point where a program can connect. A **listener** is a program waiting there. A **bind address** limits which local address a listener uses. **Loopback** reaches the same machine. **Nmap** is a tool that checks networks. A **TCP connect scan** asks the operating system to try normal TCP connections. **Open**, **closed** and **filtered** describe what the scanner sees from its place. Filtered means the replies do not let Nmap decide open versus closed. A **service probe** sends a small request to learn what a service may be. A table label is only a guess based on a port number.

## Supplied evidence exercise

Python 3.10+ on Windows, Linux or macOS; no added libraries. From this folder:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use the Answer vocabulary table below to write labels. Keep the reference answers closed. Save predictions, local notes and doubts in `notes.txt`; fill `answers.json`. Keep the first attempt, then run:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The helper only compares supplied JSON. It cannot run your scan or prove that you ran it. `analyse` and reference files reveal answers. A person must review your written reasons.

## Personally collected workflow: separate, unrun session

Use two disposable Linux VMs. These are spare virtual machines that you can reset. The target needs Python 3.10+. The client needs Nmap already present. You also need `ss` from iproute2 and local VM consoles. No tool install is part of this lab. Use an internal-only virtual switch, with no NAT, bridge, physical uplink or default route. Check the target's console to prove that the chosen IP belongs to it. Do not scan a public address, shared network, hostname, subnet or address range. The case addresses are examples, not live targets.

1. Save a scope note naming the owned client and target, their internal addresses, the switch, TCP ports 8000/8001/8002, and permission to test. Confirm isolation on both VM consoles. On the client run `ip -br address` and `ip route`; retain their output. Stop if isolation or ownership is unclear.
2. On the target, create a new empty lab directory and start two terminals there. Use a harmless empty directory so no personal files are served. Replace `TARGET_IP` below with the one confirmed internal IPv4 address.

```sh
mkdir -p run/inventory-session/empty
python3 -m http.server 8000 --bind TARGET_IP --directory run/inventory-session/empty
```

In the second target terminal:

```sh
python3 -m http.server 8001 --bind 127.0.0.1 --directory run/inventory-session/empty
```

In a third target terminal, save `ss -ltnp` output and the exact start commands. Confirm 8000 binds only to TARGET_IP, 8001 only to 127.0.0.1, and no listener uses 8002. If any port is already used, stop this session and choose a fresh disposable VM. Do not kill an unknown service.

3. On the client, create `run/inventory-session`. Write exactly the confirmed target IP as the only line of `run/inventory-session/scope.txt`. Read it back before running the scan. Save `nmap --version`. Run only this bounded command; save the exact command in your notes:

```sh
nmap -sT -sV --version-light -Pn -n -p 8000,8001,8002 --max-retries 1 --host-timeout 60s -iL run/inventory-session/scope.txt -oA run/inventory-session/scan
```

`-sT` tries to connect. `-sV` requests service probes. `--version-light` uses fewer probes. `-Pn` skips the host discovery check. `-n` avoids name lookups. `-p` limits ports. The retry and time limits may leave gaps in the results. Note those gaps. No exploit scripts are requested. Version checks still send requests to the service. That is why the target must be owned and isolated.

4. Compare `.nmap` and `.xml` output with the target's saved listener list and server logs. Without filtering, 8000 can be open from this client. Loopback-only 8001 and unused 8002 would be closed. Do not force that answer. Record what you see. If a firewall blocks a probe, keep the result. Read its settings only with permission; this lab does not change them. XML service `method="table"` is a port-name guess. `method="probed"` means the label came from a probe. Copy it as `probe` only when making a helper case. Neither proves an exact software version or a security flaw.
5. Stop both HTTP servers with Ctrl+C in their own terminals. Save a second `ss -ltnp` snapshot showing those two listeners are gone. Retain scope, command, version, scan files, listener snapshots and logs. Revert the disposable VMs if desired. Do not delete first attempts.

These tool/VM steps have **not been run for this package**. Mark personal evidence as missing until you collect it. The offline cases cannot take its place.

## Answer vocabulary: use before opening any reference

Use one exact label below for each scan ID in `answers.json`. This guide gives every supported label. It includes labels that no supplied case needs. It does not give any case's answers.

Read the scan state first. A filtered row stops at the first label. For a closed row, use the listener's bind. For an open row, first check for a listener bound to the target address. Then compare the label source. A loopback-only listener does not count as target-bound. The words joined by a semicolon form one full label. Do not add spaces around that semicolon.

| Exact decision label | When to use it |
| --- | --- |
| `inconclusive-filtered` | The scan state is filtered, regardless of the local listener note. |
| `snapshot-disagreement` | The scan is closed while a listener is recorded as bound to the target address. |
| `closed-consistent-with-snapshot` | The scan is closed and the snapshot has no target-bound listener. A loopback-only listener belongs here. |
| `open-listener-corroborated;label-probe-consistent` | The scan is open, a target-bound listener exists, and a probe label matches its recorded service. |
| `open-listener-corroborated;label-disagreement` | The scan is open and a target-bound listener exists, but a probe label differs from its recorded service. |
| `open-listener-corroborated;label-unconfirmed` | The scan is open and a target-bound listener exists, but the label comes from a port table or there is no label. |
| `open-needs-listener-review;label-unconfirmed` | The scan is open without a target-bound listener in the snapshot, whatever the label source. |

After choosing a label, explain the evidence and uncertainty in your own words. A label match alone does not verify your explanation.

## Exact small model and limits

`targets` and `ports` are fixed lists. Each listener has a target, port and bind (`target` or `loopback`). It also has a known service name. Each scan row has its own neutral ID and target/port pair. It has a state, method (`none`, `table`, `probe`) and label too. Only the three listed TCP connect states are supported. Non-open rows have no label in this model. The helper rejects unknown fields, repeated rows and data outside the listed scope.

An open target-bound listener is corroborated: the two records support each other. A closed port with such a listener is a snapshot disagreement. A closed port with only a loopback listener, or none, fits that snapshot. Filtered leaves the result unclear. An open port without the target-bound listener needs local review. Probe labels are compared only when the listener is corroborated. A matching label fits the evidence but is not proof. Table labels remain unconfirmed. The records may come from different times. Forwarding or changed programs may also explain a result. The helper does not read raw Nmap XML or prove that you own the target.

Handover: give a reviewer your scope file, actual command/version, scan output and a table of port, bind, scan state, label source, evidence and next check. State which rows remain uncertain.

## Primary references

Opened 2026-10-25:

- [Nmap connect scan and state interpretation](https://nmap.org/book/man-port-scanning-techniques.html)
- [Nmap service and version detection](https://nmap.org/book/man-version-detection.html)
- [Nmap explicit port selection](https://nmap.org/book/man-port-specification.html)
- [Python's temporary HTTP server and bind option](https://docs.python.org/3/library/http.server.html)
