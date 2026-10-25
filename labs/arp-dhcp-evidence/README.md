# Read ARP and DHCP exchanges

**Question:** which DHCP messages and ARP replies belong together, and what can a short excerpt establish about a client obtaining and using an address?

Work from original fictional packet summaries. You will match fields and frame order, distinguish a renewal from an incomplete allocation, and explain why an unrelated reply does not fill a gap. This is an offline evidence exercise: the supplied files are **not PCAPs** and no packets are sent. They do not demonstrate actual capture-tool operation or anyone's independent completion.

## Before starting

Prerequisites: [addresses and routes](../network-address-path/README.md), plus the client/packet/capture concepts in [traffic capture](../traffic-capture/README.md). You need Python 3.10+ with the standard library, a terminal and a text editor. Run commands from this folder. No administrator access, VM, DHCP server or software installation is needed. Allow **30-45 minutes** for the guided pass and a separate 20-30 minutes for a changed or independent case.

## Two kinds of address

An **IP address**, such as `192.0.2.20`, helps a packet travel to its destination across networks. It has four numbers, each from 0 through 255. A **MAC address**, such as `02:00:00:00:00:10`, is used to deliver a frame to a network adapter on the local link. It has six pairs of symbols; those pairs can use digits and the letters a to f. An IP address and a MAC address have different jobs. Neither one tells you which person is using a device.

Think about sending to another network. The final IP destination may be far away, but the local frame goes first to the gateway's MAC address. **ARP** asks which MAC address goes with a particular IP address on the local link. An ARP request means, "Who has this IP address? Tell me your MAC address." A reply supplies a claimed mapping between those two addresses.

**Broadcast** means a message addressed to all devices on the local network. **Unicast** means a message addressed to one device. `255.255.255.255` is the IPv4 broadcast destination used in these examples. `0.0.0.0` in a DHCP client-address field means that field does not give a current address to use.

## What the DHCP messages say

**DHCP** lets a client ask a server for an IP address and other settings. A **lease** gives permission to use an address for a period of time. A simple first exchange has these meanings:

| Message | Sender and plain meaning |
|---|---|
| Discover | Client: "Is there a DHCP server that can give me an address?" |
| Offer | Server: "I can offer you this address and these settings." An offer is not yet the client's accepted choice. |
| Request | Client: "I would like to use the address offered by this server." A client already using an address can also Request more time to keep it. |
| ACK | Server: "Yes. Here is the agreed address and lease time." We must still check that this reply matches the Request. |
| NAK | Server: "No. You cannot use the requested configuration; start the address request process again." This is not an ACK. |

Asking for more time is called **renewal**. It can use Request and ACK without repeating Discover and Offer. Read what the Request fields say before deciding which kind of exchange you are seeing.

Some field names are short because they come from the packet format. **xid** is the transaction number used to link a request and reply. **Client MAC** is another field checked alongside it here; one matching number alone is not enough. **ciaddr** is the client's current-address field. **yiaddr** is the address offered or assigned to the client. **Server identifier** names the DHCP server. **Frame** is the saved packet's number, used to find it again and compare order. A **capture gap** means an observation is absent from the saved view; it does not tell us whether the message was ever sent.

A DHCP server is not necessarily the gateway that forwards traffic. The guided example happens to use the same fictional IP for both roles. Matching these fields does not depend on the two roles sharing an address.

## Prepare and predict

```console
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `run/attempt-01/packets.txt` and the authoritative case JSON. Build a table with columns: query ID, relevant frames, ignored frames and why, address fields, result, uncertainty and next check. For each ARP query also fill its `-lease-link` worksheet entry: does the earlier matched DHCP exchange support a link to the address used in the observed ARP request?

Edit `answers.json` using the exact labels below. Add a paragraph to `explanation` and frame/field references to `evidence`, such as `lease-a frame 3 requested_ip`. Use `notes.txt` for predictions, limits and help used. Save a separate `answers-first.json` copy in your editor before checking. Keep corrections alongside the initial attempt.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Repeat `show`, `check` and `analyse` with the new attempt paths. Keep reference files, tests, the worked example and `analyse` closed during independent practice. `check` reveals expected labels for differences, so preserve your prediction first. It requires written fields but cannot judge the accuracy of their explanation. `verify` compares three authored fixtures with fixed reference outputs; it does not assess a learner.

Prepare writes only below this lab's ignored `run/`, refuses linked paths and requires a fresh destination. Explicit input paths are relative to your current working directory; default input is `fixtures/guided.json`. Exit codes: 0 success/matching completed worksheet, 1 differences/incomplete worksheet, 2 invalid input/filesystem problem. Preserve attempts for review. No service, adapter or lease is changed, so there is no network rollback. Any later cleanup is limited to disposable copies of your own practice evidence after retaining the first attempt and correction.

## Exact supported evidence model

The [shared contract](../FOUNDATION-CONTRACT.md) defines the eight case-envelope fields. `context` has only a nonempty `question`. `data` contains exactly `capture_note`, `dhcp_sessions`, `arp_exchanges`. The two lists each contain 1-10 queries, each with 1-30 packets. JSON is authoritative; `artifacts.packets.txt` must mirror it exactly. Every frame is an integer 1-1000000, unique across the case and strictly increasing within its own excerpt. All excerpts share one observation point and frame-number sequence. Their lists may be grouped by query rather than global time. The following tables describe the file format; the plain-language explanation above is the starting point for understanding the exchanges.

Query IDs use lowercase letters, digits and hyphens, start with a letter and have at most 40 characters. DHCP and ARP output IDs, including generated `-lease-link` IDs, must be unique. Addresses use the three documentation IPv4 blocks; `0.0.0.0` and `255.255.255.255` have only the special roles listed below. MACs are lowercase six-octet synthetic unicast values starting `02:`; a request target MAC is `00:00:00:00:00:00` in this fixture format.

### DHCP inputs and matching

A session has `id`, `client_mac`, integer `xid` from 0 to 4294967295, and `packets`. Each DHCP packet has exactly `frame`, `message`, `xid`, `client_mac`, `ciaddr`, `yiaddr`, `requested_ip`, `server_id`, `ip_destination`, `lease_seconds`. Null option values mean absent from this teaching summary. Valid packet fields do not by themselves establish that the packet belongs to the queried client transaction.

| Message form | Fields required by this model |
|---|---|
| Discover | Zero ciaddr/yiaddr, null requested IP/server/lease, broadcast destination. |
| Selecting-state allocation Request (client has chosen an Offer) | Zero ciaddr/yiaddr, requested IP and selected server present, null lease, broadcast destination. |
| Unicast renewal Request | Existing ciaddr, zero yiaddr, null requested IP/server/lease, unicast destination naming the server. |
| Offer | Zero ciaddr, nonzero yiaddr, server identifier and positive integer lease seconds (maximum 4294967295), no requested-IP option. Destination is broadcast or yiaddr. |
| ACK | Nonzero yiaddr, server identifier and positive integer lease seconds (maximum 4294967295), no requested-IP option. When its Request is observed, ciaddr must be zero or copied from that Request, and delivery follows the rules below. |
| NAK | Zero ciaddr/yiaddr, server identifier, no requested-IP or lease value; broadcast destination because this model has no relay. |

Match both client MAC and xid. Ignore other packets, retaining their frame numbers as evidence. For matching packets there is at most one of each message and one ending reply, either ACK or NAK; order follows Discover, Offer, Request, ACK/NAK with gaps allowed. Retransmissions, multiple offers, both ACK and NAK for the same attempt, or renewal mixed with initial-allocation steps are outside this small model and rejected. A renewal is recognised from the Request fields, not from a label supplied by the learner.

For an allocation Request, compare ACK server/address with `server_id`/`requested_ip`. For renewal, compare them with Request `ip_destination`/`ciaddr`. An allocation ACK may be broadcast or sent to its yiaddr; the summary omits the broadcast flag, so both delivery forms are allowed. A renewal ACK must be sent to the Request's current client address. Its ciaddr field may copy that address or be zero. Contradictory ciaddr or destination fields are rejected. A complete initial allocation additionally needs Discover and a matching Offer. A NAK must match the expected server.

Without a matching observed Request, the helper cannot check whether an ACK's ciaddr was copied correctly or whether its destination follows that Request. Those two fields receive address-format checks only, and the result remains `request-not-observed`, with no established lease link. Relay fields, the broadcast flag, Ethernet destination and UDP ports are not supplied or validated. The whole exercise assumes no relay. Even a matching ACK is evidence of a reply, not proof that the client accepted the address or that the address remains leased now.

| DHCP decision | Exact meaning |
|---|---|
| `allocation-ack-observed` | All four initial steps are present, with matching selected Offer, Request and ACK fields. |
| `allocation-ack-with-gaps` | Allocation Request and ACK match, but Discover or the selected Offer is absent. |
| `renewal-ack-observed` | A supported unicast renewal Request and matching ACK are present. |
| `ack-not-observed` | Matching Request is present; no matching ACK/NAK is in this excerpt. |
| `request-not-observed` | No Request matches this client/xid; an Offer or lone ACK is not enough for the comparison. |
| `reply-mismatch` | A client/xid-matched ACK or NAK has the wrong expected server, or an ACK has a different address. |
| `nak-observed` | A matching Request is followed by a NAK from the expected server. |

### ARP inputs and matching

An exchange has `id`, `requester_ip`, `requester_mac`, `target_ip`, `related_dhcp` and `packets`. The related DHCP ID must exist and have the same client MAC. Each ARP packet has `frame`, `opcode` (`request`/`reply`), `sender_ip`, `sender_mac`, `target_ip`, `target_mac`. Requester and target IPs differ. Probes with a zero sender address and announcements with identical sender/target IPs are deliberately excluded.

Match a request on requester IP, requester MAC and sought target IP. Match a reply on sender IP equal to the sought address, target IP equal to the requester and target MAC equal to the requester MAC. Other frames stay visible but do not complete this exchange. Matching replies describe observed mapping claims; they are not authenticated ownership records.

| ARP decision | Exact meaning |
|---|---|
| `exchange-observed` | At least one matching request precedes a matching reply, and replies agree on one sender MAC. |
| `request-no-reply-observed` | Matching request exists, but no matching reply appears. |
| `reply-without-prior-request` | Matching reply exists without an earlier matching request. |
| `no-matching-frames` | Neither request nor reply matches the query. |
| `mapping-disagreement` | Matching replies give more than one MAC for the target; cause is undetermined. |

If an excerpt contains an early reply followed by a matching request and a later reply, the later pair counts as `exchange-observed`. The earlier reply remains listed as having no earlier observed matching request. Different claimed MACs take priority as `mapping-disagreement`, even when a request/reply pair is also present. This prevents one early unpaired reply from hiding a later observed exchange.

Each ARP query also produces a `query-id-lease-link` decision. `same-client-address-observed` requires a matched DHCP Request/ACK, an ARP request later than the ACK, and agreement between ACK yiaddr and the ARP requester's address. `lease-address-disagreement` reports a later ARP request using a different address. `arp-precedes-ack` reports that the earliest matching ARP request predates the ACK, so this reply cannot explain earlier use. `lease-link-not-established` means the matched ACK or matching ARP request is missing. This is field/time correlation, not proof of identity, acceptance or causality.

## Deliverable and handover

Save your annotated exchange table, case ID, Python version, first worksheet, correction and help-used notes. Include one missing-message explanation that distinguishes "not seen" from "did not happen", and one proportional next check such as extending an authorised capture window or comparing a client-side lease record. Use [the worked example](WORKED-EXAMPLE.md) only for the guided case and [the drills](DRILLS.md) to reduce help.

Handover prompt: "Which exact fields link these frames, which tempting frame did you exclude, and what remains unknown after the link?"

## Optional saved-capture comparison

If you already have Wireshark and a benign, reviewed capture from an isolated owned lab, open a **copy** with File > Open. Do not start capture or renew/release a lease for this activity. Select one ARP packet and one DHCP packet in the packet list; expand their protocol details and compare the actual fields with this simplified summary format. Record actual frame references and what is absent or more complex. If the saved file has no such traffic, record that limitation instead of manufacturing an exchange. The supplied text files cannot be opened as PCAPs, and this optional comparison has not been performed by running the helper tests. Closing the file needs no configuration rollback; preserve the original capture and keep any annotated copy private.

## Limits and primary sources

The helper is not a DHCP server, ARP cache, packet decoder or complete protocol state machine. It excludes relays, broadcast rebinding, INIT-REBOOT, DHCPINFORM, retransmissions, multiple Offers, ARP probes and announcements. Frame order has no elapsed-time measurement; a positive lease duration alone cannot establish current validity. Capture position, packet loss and the start/end window can leave missing messages. A disagreeing mapping or address does not establish an attack, intent or fault cause. There is no poisoning, spoofing or attack exercise.

- [IETF RFC 826: ARP request/reply fields and address resolution](https://www.rfc-editor.org/rfc/rfc826.html)
- [IETF RFC 2131, sections 3.1, 4.1 and 4.4.5: allocation, transaction matching and renewal](https://www.rfc-editor.org/rfc/rfc2131.html)
- [IETF RFC 5737: IPv4 documentation address blocks](https://www.rfc-editor.org/rfc/rfc5737.html)
- [Wireshark User's Guide: viewing previously captured packets and protocol fields](https://www.wireshark.org/docs/wsug_html_chunked/ChapterWork.html)

Sources were opened during preparation on 2026-10-25. The sources explain protocol concepts; the finite input forms and decision labels here are teaching choices.
