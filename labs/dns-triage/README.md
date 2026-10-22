# DNS triage: a small offline packet puzzle

**Guided practice material. All packets are SYNTHETIC. Independent mastery: NOT assessed.**

Two invented clients ask an invented resolver for five names. Some replies contain an IPv4 address, one reply reports that a name does not exist, and one question has no visible reply. Your job is to support each conclusion with packet numbers and explain what the capture cannot establish.

This is a new portfolio exercise, with a newly constructed scenario, packet sequence, generator, worksheet and drills. It uses no coursework task sheet, submission, data, screenshot or assessment answer. It is not a renamed submission, a record of a real incident, or a claim that Jeremy has independently completed the exercise. Common DNS protocol concepts are shared knowledge; the references below identify their sources.

## What you will practise

- Find a DNS question and match its reply using the client, resolver, UDP ports, DNS ID, name and question type.
- Distinguish an A answer, an NXDOMAIN response, and an unanswered question **within this file**.
- Group a retry with its original question without assuming the network dropped a packet.
- Measure the interval from the first observed request to its response and state its limits.

An **A question** asks for an IPv4 address. A **resolver** answers DNS questions for a client. **NXDOMAIN** is response code 3, meaning the reply reports that the queried name does not exist. A response is still a response when it reports an error.

## Start here

You need Python 3.9 or later and Wireshark for visual inspection. The generator and checker use Python's standard library only. No capture interface, administrator rights, VM, account or network connection is needed. Do not start a live capture; open the supplied file.

From this directory, run:

```sh
python lab.py --help
python lab.py verify
python lab.py exercise
```

If your Windows Python launcher is `py`, use `py -3` in place of `python`. `verify` checks the retained guided case. `exercise` creates `run/worksheet-37.json`; keep your own answers there. If that worksheet already exists, supply a fresh `--out run/worksheet-37-second.json` to preserve it.

Open [`fixtures/guided/SYNTHETIC-dns.pcap`](fixtures/guided/SYNTHETIC-dns.pcap) in Wireshark with **File > Open**. There are 11 packets. The client addresses are `192.0.2.10` and `192.0.2.11`; the resolver is `192.0.2.53`. All names begin with `synthetic-` and end in `.test`.

Choose a packet and expand **Internet Protocol**, **User Datagram Protocol** and **Domain Name System** in its details. Read the IP addresses, UDP ports, transaction ID, response flag, question and answer fields. Frame numbers are the numbers in the original file; applying a display filter does not renumber them. For timing, use the frame's **Time since reference or first frame** in seconds and subtract the first request time from the reply time. Multiply seconds by 1,000 to obtain milliseconds.

## Small filter toolkit

Enter these in Wireshark's **display filter** bar after opening the file. They hide unrelated rows; they do not change or capture packets.

| Purpose | Display filter |
| --- | --- |
| All DNS packets | `dns` |
| Questions | `dns.flags.response == 0` |
| Replies | `dns.flags.response == 1` |
| NXDOMAIN replies | `dns.flags.response == 1 && dns.flags.rcode == 3` |
| Replies containing an A address | `dns.flags.response == 1 && dns.flags.rcode == 0 && dns.a` |
| One guided question, including its replies | `dns.qry.name == "synthetic-violet.test"` |
| Reused transaction ID in the guided case | `dns.id == 0x800f` |

Filter fields are documented in the [Wireshark DNS display filter reference](https://www.wireshark.org/docs/dfref/d/dns.html). A DNS ID alone is not a unique conversation: check endpoints, ports and question too. For an unanswered question, inspect all its matching rows in the whole file; an individual request row is not evidence that no reply exists elsewhere.

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

The checker reports fields to revisit without printing the answers. A pass means 20 objective fields match the fixture. It does **not** assess your explanations, independence or professional competence. Review those with a person. The manifest contains the answer key, so leave it closed during independent practice.

## Repeat with a changed dataset

```sh
python lab.py generate --seed 91
python lab.py verify --case run/case-91
python lab.py exercise --case run/case-91
python lab.py check --case run/case-91 --answers run/worksheet-91.json
```

Open `run/case-91/SYNTHETIC-dns.pcap`. The seed changes the names assigned to outcomes, IDs, ports, answer addresses and timing. Each variant keeps the same small learning structure; changing the seed is repeated practice, not proof of broad expertise. All `run/` files are ignored by Git. The generator refuses to replace differing existing case files; choose another output directory when needed.

## Verification and boundaries

```sh
python -m unittest -v test_lab
```

`lab.py` is the maintained entry point for generation, verification and worksheets. Its parser verifies the PCAP records, Ethernet/IPv4/UDP structure, IPv4 and UDP checksums, DNS questions and compressed answer names, response codes, timing order and request/reply relationships. SHA-256 hashes detect changes to the fixture files; the verifier also regenerates the expected bytes from the seed. File integrity is separate from a learner's interpretation.

The retained deterministic case is in `fixtures/guided/`: the capture, a short `case.json`, and a `manifest.json` containing synthetic provenance, hashes and expected evidence. Timestamps and MAC addresses are invented. Addresses use the [RFC 5737 documentation blocks](https://www.rfc-editor.org/info/rfc5737/), and names use the [reserved `.test` domain](https://www.rfc-editor.org/info/rfc2606/).

This deliberately small format covers Ethernet, IPv4, UDP and A questions only. It does not cover TCP fallback, encrypted DNS, IPv6, caching, CNAME chains, DNSSEC or NOERROR replies with no A answer. In real traffic, NOERROR alone does not guarantee an A record; inspect the answer section. The NXDOMAIN reply is intentionally minimal and carries no SOA authority record, so this exercise does not model negative caching. The verifier is for this generated format, not an arbitrary-PCAP forensic tool.

An unanswered question here does not locate a fault or prove a timeout, firewall block, resolver outage or packet loss. An A answer does not establish that a website loaded. A late response cannot establish which repeated datagram prompted it, or measure resolver processing time separately from transit time. The file provides no observation after its final packet and no independent confirmation that a reply's DNS claim is correct.
