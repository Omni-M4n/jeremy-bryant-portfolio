# DNS triage: a small offline packet puzzle

**Guided practice material. All packets are SYNTHETIC. Independent mastery: NOT assessed.**

Which DNS questions got a reply? Two made-up clients ask a made-up resolver for five names. Some replies give an IPv4 address. One says that a name does not exist. One question has no reply in this file. Use packet numbers to support each finding. Explain what the file cannot prove.

This is a new portfolio exercise. Its case, packet sequence, generator, worksheet and drills are new. It uses no coursework task sheet, submission, data, screenshot or assessment answer. It is not a renamed submission or a real incident record. It does not claim that Jeremy completed it without help. DNS concepts are shared knowledge. The links below name their sources.

## What you will practise

- Find a DNS question and match its reply. Check the client, resolver, UDP ports, DNS ID, name and question type.
- Tell three outcomes apart **within this file**: an A answer, an NXDOMAIN response, and no reply.
- Group a retry with its first question. A retry does not prove that the network dropped a packet.
- Measure the time from the first seen request to its reply. State the limits of that measure.

| Term | Meaning |
| --- | --- |
| **A question** | A request for an IPv4 address |
| **Resolver** | A service that answers DNS questions for a client |
| **NXDOMAIN** | Response code 3: the reply says the requested name does not exist |

A reply still counts as a reply when it reports an error.

## Start here

You need Python 3.9 or later. Use Wireshark to view the packets. The generator and checker use Python's standard library only. You need no capture interface, administrator rights, VM or account. You need no network connection. Do not start a live capture. Open the supplied file.

From this directory, run:

```sh
python lab.py --help
python lab.py verify
python lab.py exercise
```

If your Windows Python launcher is `py`, use `py -3` in place of `python`. `verify` checks the saved guided case. `exercise` creates `run/worksheet-37.json`. Keep your own answers there. If it already exists, use a fresh `--out run/worksheet-37-second.json`. This keeps your first attempt intact.

Open [`fixtures/guided/SYNTHETIC-dns.pcap`](fixtures/guided/SYNTHETIC-dns.pcap) in Wireshark with **File > Open**. There are 11 packets.

| Detail | Value |
| --- | --- |
| Client addresses | `192.0.2.10` and `192.0.2.11` |
| Resolver address | `192.0.2.53` |
| Name pattern | Starts with `synthetic-`; ends in `.test` |

Choose a packet. Expand **Internet Protocol**, **User Datagram Protocol** and **Domain Name System** in its details. Read the IP addresses, UDP ports and transaction ID. Then read the response flag, question and answer fields. Frame numbers come from the original file. A display filter does not renumber them.

For timing, find **Time since reference or first frame**. This field uses seconds. Subtract the first request time from the reply time. Multiply the result by 1,000 to get milliseconds.

## Small filter toolkit

Open the file, then use Wireshark's **display filter** bar. These filters hide rows you do not need. They do not change or capture packets.

| Purpose | Display filter |
| --- | --- |
| All DNS packets | `dns` |
| Questions | `dns.flags.response == 0` |
| Replies | `dns.flags.response == 1` |
| NXDOMAIN replies | `dns.flags.response == 1 && dns.flags.rcode == 3` |
| Replies containing an A address | `dns.flags.response == 1 && dns.flags.rcode == 0 && dns.a` |
| One guided question, including its replies | `dns.qry.name == "synthetic-violet.test"` |
| Reused transaction ID in the guided case | `dns.id == 0x800f` |

Find field details in the [Wireshark DNS display filter reference](https://www.wireshark.org/docs/dfref/d/dns.html). A DNS ID alone does not identify one exchange. Check endpoints, ports and the question too. An endpoint is an address and port at one end. Before marking a question unanswered, search the whole file. Check all rows that match it. A request on its own does not prove that no reply exists elsewhere.

## Record and check your evidence

Start with the [worked example](WORKED-EXAMPLE.md), then follow the [progressive drills](DRILLS.md). The worksheet lists the five names and clients. Fill each entry's fields:

| Field | What to enter |
| --- | --- |
| `request_frames` | Original-file frame numbers, in order, including a repeated request |
| `response_frames` | Matching reply frame numbers, or `[]` if none is visible |
| `outcome` | Exactly `answer`, `nxdomain`, or `unanswered` |
| `first_response_ms` | Reply time minus **first** request time, in milliseconds; `null` if unanswered |
| `explanation` | A short evidence-based explanation with a limitation |
| `limits` | Your overall statement of what this capture cannot establish |

Keep JSON quotes and commas intact. Do not change the seed, capture hash, question names or clients. Then run:

```sh
python lab.py check --answers run/worksheet-37.json
```

The checker names fields to revisit. It does not print the answers. A pass means 20 fact fields match the fixture. It does **not** assess your explanations or skill. It cannot show that you worked without help. Review those points with a person. The manifest holds the answer key. Leave it closed when practising without help.

## Repeat with a changed dataset

```sh
python lab.py generate --seed 91
python lab.py verify --case run/case-91
python lab.py exercise --case run/case-91
python lab.py check --case run/case-91 --answers run/worksheet-91.json
```

Open `run/case-91/SYNTHETIC-dns.pcap`. The seed changes which names get each outcome. It also changes IDs, ports, answer addresses and timing. Each case keeps the same small learning structure. A new seed gives more practice, not proof of broad skill. Git ignores all `run/` files. The generator will not replace case files with different contents. Choose a new output folder when needed.

## Verification and boundaries

```sh
python -m unittest -v test_lab
```

Use `lab.py` to create cases, check files and make worksheets. It is the maintained entry point. Its parser reads the capture and checks these parts:

| Part | Checks |
| --- | --- |
| Capture | PCAP records; Ethernet/IPv4/UDP structure |
| Checksums | IPv4 and UDP checksums |
| DNS | Questions, compressed answer names and response codes |
| Sequence | Time order and request/reply matches |

SHA-256 hashes help detect changed fixture files. A hash is a value made from file bytes. The verifier also rebuilds the expected bytes from the seed. These checks test the files, not the learner's reasoning.

The saved case is in `fixtures/guided/`. The same seed always makes the same case. It holds the capture and a short `case.json`. Its `manifest.json` records the made-up source, hashes and expected evidence. Times and MAC addresses are made up. Addresses use the [RFC 5737 documentation blocks](https://www.rfc-editor.org/info/rfc5737/). Names use the [reserved `.test` domain](https://www.rfc-editor.org/info/rfc2606/).

| Format scope | What this means |
| --- | --- |
| Included | Ethernet, IPv4, UDP and A questions only |
| Not included | TCP fallback, encrypted DNS, IPv6, caching, CNAME chains, DNSSEC or NOERROR replies with no A answer |
| Minimal NXDOMAIN reply | No SOA authority record; this exercise does not model negative caching |

In real traffic, NOERROR alone does not promise an A record. Read the answer section. The verifier supports only this generated format. It is not a forensic tool for any PCAP file.

An unanswered question does not locate a fault. It does not prove that a timeout, firewall block, resolver outage or packet loss occurred. An A answer does not prove that a website loaded. A late reply cannot show which repeated datagram prompted it. A datagram is one UDP message. The measured interval cannot separate resolver processing time from network travel time. The file shows nothing after its final packet. It also cannot confirm that a reply's DNS claim is true.
