# Read ARP and DHCP exchanges

**Question:** which DHCP messages and ARP replies belong together? What can a short excerpt show about a client getting and using an address?

Work from made-up packet summaries. Match fields and frame order. Tell a lease renewal apart from an incomplete first lease exchange. Explain why a reply from another exchange does not fill a gap. This task is offline. The files are **not PCAPs**, and no packets are sent. These files do not show use of a real capture tool or work that a learner has done alone.

## Before starting

First complete [addresses and routes](../network-address-path/README.md). Learn the client, packet and capture terms in [traffic capture](../traffic-capture/README.md). You need Python 3.10+ and its built-in tools, a terminal and a text editor. Run commands from this folder. You need no admin rights, VM, DHCP server or new software. Allow **30-45 minutes** for the guided pass. Allow a further 20-30 minutes for a changed case or one you try alone.

## Two kinds of address

An **IP address**, such as `192.0.2.20`, helps a packet reach its destination across networks. It has four numbers, each from 0 through 255. A **MAC address**, such as `02:00:00:00:00:10`, is used to send a frame to a network adapter on the local link. It has six pairs of symbols. Each pair can use digits and the letters a to f. IP and MAC addresses have different jobs. Neither tells you which person is using a device.

Think about sending to another network. The final IP destination may be far away, but the local frame goes first to the gateway's MAC address. **ARP** asks which MAC address goes with a particular IP address on the local link. An ARP request means, "Who has this IP address? Tell me your MAC address." A reply supplies a claimed mapping between those two addresses.

**Broadcast** means a message sent to all devices on the local network. **Unicast** means a message sent to one device. `255.255.255.255` is the IPv4 broadcast address used here. `0.0.0.0` in a DHCP client-address field gives no current address to use.

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

Some field names come from the packet format. **xid** is a transaction number. It helps link a request and reply. Check **Client MAC** too. One matching number alone is not enough. **ciaddr** is the client's current-address field. **yiaddr** is the address offered or given to the client. **Server identifier** names the DHCP server. **Frame** is the saved packet's number. Use it to find the packet and check order. A **capture gap** means a message is missing from the saved view. It does not tell us whether that message was ever sent.

A DHCP server need not be the gateway that forwards traffic. The guided case uses the same made-up IP for both roles. The field checks still work when those roles use different addresses.

## Prepare and predict

```console
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `run/attempt-01/packets.txt` and the case JSON, which is the source of truth. Build a table with these columns: query ID, matching frames, ignored frames and why, address fields, result, doubts and next check. For each ARP query, also fill its `-lease-link` entry. Check whether an earlier matched DHCP exchange supports a link to the address in the ARP request.

Edit `answers.json` using the exact labels below. Add a paragraph to `explanation`. Add frame and field references to `evidence`, such as `lease-a frame 3 requested_ip`. Use `notes.txt` for predictions, limits and help used. Save a separate `answers-first.json` copy in your editor before checking. Keep corrections beside the first attempt.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Repeat `show`, `check` and `analyse` with the new attempt paths. Keep answer files, tests, the worked example and `analyse` closed while working alone. `check` reveals expected labels where yours differ. Save your prediction first. It requires written fields but cannot judge whether the reason is right. `verify` compares three made-up cases with fixed answers. It does not assess a learner.

Prepare writes only below this lab's ignored `run/`. It refuses linked paths and needs a new folder. Paths you enter start from your current working folder. The default input is `fixtures/guided.json`. Exit code 0 means success or a complete worksheet with matching labels. Code 1 means differences or missing work. Code 2 means bad input or a file-system problem. Keep attempts for review. No service, adapter or lease changes, so no network state needs to be restored. For cleanup, keep your first attempt and correction. Remove only spare copies of your own practice evidence.

## Exact supported evidence model

The [shared contract](../FOUNDATION-CONTRACT.md) defines the eight outer case fields. `context` has only a nonempty `question`. `data` holds exactly `capture_note`, `dhcp_sessions`, `arp_exchanges`. Each list holds 1-10 queries. Each query holds 1-30 packets. JSON is the source of truth. `artifacts.packets.txt` must match it exactly. Each frame is a whole number from 1 to 1000000. Frame numbers are unique across the case and rise within each excerpt. All excerpts share one capture point and frame sequence. Lists may group packets by query, not by time across the whole case. The tables below describe the file format. Start with the plain explanation above to learn how the exchanges work.

Query IDs use lowercase letters, digits and hyphens. They start with a letter and have at most 40 characters. DHCP and ARP output IDs must be unique. This includes the added `-lease-link` IDs. Addresses use the three IPv4 blocks set aside for examples. `0.0.0.0` and `255.255.255.255` have only the special roles listed below. MACs are made-up unicast values in lowercase, with six pairs of hex digits. They start with `02:`. A request's target MAC is `00:00:00:00:00:00` in this file format.

### DHCP inputs and matching

A session has `id`, `client_mac`, integer `xid` from 0 to 4294967295, and `packets`. Each DHCP packet has exactly `frame`, `message`, `xid`, `client_mac`, `ciaddr`, `yiaddr`, `requested_ip`, `server_id`, `ip_destination`, `lease_seconds`. A null option means it is absent from this teaching summary. Valid fields alone do not link a packet to the client exchange you are checking.

| Message form | Fields required by this model |
|---|---|
| Discover | Zero ciaddr/yiaddr, null requested IP/server/lease, broadcast destination. |
| Selecting-state allocation Request (client has chosen an Offer) | Zero ciaddr/yiaddr, requested IP and selected server present, null lease, broadcast destination. |
| Unicast renewal Request | Existing ciaddr, zero yiaddr, null requested IP/server/lease, unicast destination naming the server. |
| Offer | Zero ciaddr, nonzero yiaddr, server identifier and positive integer lease seconds (maximum 4294967295), no requested-IP option. Destination is broadcast or yiaddr. |
| ACK | Nonzero yiaddr, server identifier and positive integer lease seconds (maximum 4294967295), no requested-IP option. When its Request is observed, ciaddr must be zero or copied from that Request, and delivery follows the rules below. |
| NAK | Zero ciaddr/yiaddr, server identifier, no requested-IP or lease value; broadcast destination because this model has no relay. |

Match both client MAC and xid. Ignore other packets but keep their frame numbers as evidence. Matching packets have at most one of each message. The ending reply can be ACK or NAK, not both. Their order is Discover, Offer, Request, ACK/NAK, with gaps allowed. This small model rejects repeats and multiple offers. It also rejects both ending replies in one attempt, or renewal mixed with first-lease steps. The Request fields identify a renewal. The learner's label does not.

For a first-lease Request, compare the ACK server and address with `server_id`/`requested_ip`. For renewal, compare them with the Request's `ip_destination`/`ciaddr`. A first-lease ACK may be broadcast or sent to its yiaddr. This summary leaves out the broadcast flag, so it allows both forms. A renewal ACK must go to the Request's current client address. Its ciaddr may copy that address or be zero. The helper rejects ciaddr or destination fields that conflict with these rules. A full first-lease exchange also needs Discover and a matching Offer. A NAK must match the expected server.

Without a matching Request in the records, the helper cannot check two ACK fields against it. It cannot check whether ciaddr was copied correctly or whether the destination follows the Request. It checks only the address format for those fields. The result stays `request-not-observed`, with no established lease link. The records omit relay fields, the broadcast flag, Ethernet destination and UDP ports. The helper does not check those fields. The task assumes no relay. Even a matching ACK shows only a reply. It does not prove the client took the address or still has the lease now.

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

An exchange has `id`, `requester_ip`, `requester_mac`, `target_ip`, `related_dhcp` and `packets`. The linked DHCP ID must exist and use the same client MAC. Each ARP packet has `frame`, `opcode` (`request`/`reply`), `sender_ip`, `sender_mac`, `target_ip`, `target_mac`. Requester and target IPs must differ. This model leaves out probes with a zero sender address. It also leaves out announcements with the same sender and target IP.

Match a request using the requester IP, requester MAC and target IP being sought. For a reply, first check that its sender IP is the sought address. Its target IP must be the requester's IP. Its target MAC must be the requester's MAC. Other frames stay visible but do not complete this exchange. Matching replies show claims about an IP-to-MAC mapping. They do not prove who owns the address.

| ARP decision | Exact meaning |
|---|---|
| `exchange-observed` | At least one matching request precedes a matching reply, and replies agree on one sender MAC. |
| `request-no-reply-observed` | Matching request exists, but no matching reply appears. |
| `reply-without-prior-request` | Matching reply exists without an earlier matching request. |
| `no-matching-frames` | Neither request nor reply matches the query. |
| `mapping-disagreement` | Matching replies give more than one MAC for the target; cause is undetermined. |

An excerpt may have an early reply, then a matching request and a later reply. The later pair counts as `exchange-observed`. The early reply stays listed as having no earlier matching request in view. Different claimed MACs take priority as `mapping-disagreement`. This holds even when a request/reply pair is present. An early unpaired reply thus cannot hide a later exchange.

Each ARP query also gives a `query-id-lease-link` decision. `same-client-address-observed` needs a matched DHCP Request/ACK. The ARP request must come after the ACK. ACK yiaddr must match the ARP requester's address. `lease-address-disagreement` means a later ARP request uses a different address. `arp-precedes-ack` means the earliest matching ARP request came before the ACK. That reply cannot explain the earlier address use. `lease-link-not-established` means the matched ACK or matching ARP request is missing. These checks link fields and order. They do not prove identity, acceptance or cause.

## Deliverable and handover

Save your marked exchange table, case ID, Python version, first worksheet, correction and help notes. Explain one missing message. Show why "not seen" differs from "did not happen". Choose one small next check. This could be a longer approved capture window or a client-side lease record. Use [the worked example](WORKED-EXAMPLE.md) only for the guided case. Use [the drills](DRILLS.md) to practise with less help.

Handover prompt: "Which exact fields link these frames, which tempting frame did you exclude, and what remains unknown after the link?"

## Optional saved-capture comparison

Use this part only if you already have Wireshark and a safe, reviewed capture from an isolated lab you own. Open a **copy** with File > Open. Do not start capture or renew or release a lease. Select one ARP packet and one DHCP packet. Expand their protocol details. Compare the real fields with this simple summary format. Record frame numbers and note missing or more complex fields. If the file has no such traffic, write that down. Do not make up an exchange. The given text files cannot be opened as PCAPs. Running the helper tests has not performed this optional comparison. Close the file when done. No settings need to be restored. Keep the original capture and keep marked copies private.

## Limits and primary sources

The helper is not a DHCP server, ARP cache, packet decoder or full protocol state machine. It leaves out relays, broadcast rebinding, INIT-REBOOT, DHCPINFORM, retransmissions, multiple Offers, ARP probes and announcements. Frame order does not measure elapsed time. A positive lease length alone cannot show that the lease is valid now. Capture position, lost packets and the start/end window can leave gaps. A mapping or address mismatch does not prove an attack, intent or cause of a fault. This is no poisoning, spoofing or attack task.

- [IETF RFC 826: ARP request/reply fields and address resolution](https://www.rfc-editor.org/rfc/rfc826.html)
- [IETF RFC 2131, sections 3.1, 4.1 and 4.4.5: allocation, transaction matching and renewal](https://www.rfc-editor.org/rfc/rfc2131.html)
- [IETF RFC 5737: IPv4 documentation address blocks](https://www.rfc-editor.org/rfc/rfc5737.html)
- [Wireshark User's Guide: viewing previously captured packets and protocol fields](https://www.wireshark.org/docs/wsug_html_chunked/ChapterWork.html)

Sources were opened while making this lab on 2026-10-25. They explain the protocols. The limited input forms and labels were chosen for teaching.
