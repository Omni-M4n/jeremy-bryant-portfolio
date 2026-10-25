# Map addresses, subnets and a packet's route

**Question:** given a destination, supplied name evidence and a small route table, which address is the next hop? Explain why an Ethernet next hop can differ from the packet's IP destination.

This original beginner exercise uses fictional interface and route snapshots. It does not connect to a network. The optional final activity reads an existing isolated Windows VM's configuration; it does not change it. Prepared materials and passing checks do not establish anyone's completion or independent competence.

## Start here

Prerequisites: recognise an IPv4 address and a port. Python 3.10+ with its standard library, a terminal and a text editor are enough. Run commands from this folder. No installation, administrator access, VM or packet capture software is needed for the offline exercise. Allow **30-40 minutes**: 5 for vocabulary, 15 for a prediction, 10 for correction and 5-10 for explanation. Keep the changed case for a separate 15-25 minute session.

## What the address numbers mean

A **packet** is a small bundle of information sent over a network. An IPv4 address, such as `192.0.2.10`, has four whole numbers separated by dots. Each number can be 0 through 255. The dots separate the numbers; this is not a decimal fraction. The whole address matters: `192.0.2.10` and `192.0.2.200` are different addresses.

A **subnet** is a group of addresses treated as being on the same local network. An **interface** is a device's connection to that network. The part after a slash tells you the size of the address group. For example, `/24` covers 256 addresses, `/25` covers 128 and `/26` covers 64. A larger number after the slash means a smaller group. A `/32` route names just one address.

The slash number is called the **prefix length**. A computer stores an IPv4 address as 32 small values called bits; each bit is 0 or 1. `/26` says that the first 26 bits stay fixed for that group. Six bits can change, giving `2 x 2 x 2 x 2 x 2 x 2 = 64` addresses. A **prefix** names a group by its first address and this length.

Here is a separate example for practising the range calculation: `203.0.113.170/26`. Groups of 64 begin at last numbers 0, 64, 128 and 192. The number 170 lies in the group starting at 128. Its range is therefore `203.0.113.128` through `203.0.113.191`, because `128 + 64 - 1 = 191`. The prefix is `203.0.113.128/26`. In the ordinary local networks used here, the first address names the group and the last is its broadcast address, so devices use `.129` through `.190`. Use the slash number as well as the address when deciding what is local.

## Where the packet goes next

The **next hop** is the next device that receives the packet on the local link. A **gateway** is a router used to send the packet onwards to another network. These are not always the same thing. In the guided example, desk `192.0.2.200` is on the workstation's local network, so the desk itself is the next hop; it does not need to be a router. A packet for another network may instead go first to a gateway.

A **route** is an instruction saying which address group a path covers and where to send matching packets. Choose the most detailed matching instruction: a route for one address is more specific than a route for a group of 256 addresses. The **default route**, `0.0.0.0/0`, is the fallback if no more specific route matches. A **metric** is a preference number; this exercise uses the lower number only when the matching prefixes are equally long.

**Name resolution** supplies an IP address for a name such as `archive.test`. That gives the route lookup a destination to work with. **ARP** can then find the MAC address of the next device on the local link. A MAC address is the network adapter address used for local delivery. The **ARP target** is the next-hop IP address being looked up. A route choice alone does not show that a packet reached its final destination.

## Guided topology

```text
              local Ethernet: 192.0.2.0/24
workstation .10 ----+---- desk .200
                   +---- gateway .1   -> default path
                   +---- gateway .254 -> 198.51.100.0/24
                   +---- gateway .253 -> 198.51.100.77/32
```

All abbreviated addresses on the local line begin `192.0.2`. Arrows represent the supplied first-hop routes, not verified downstream connectivity. Copy this diagram into your notes and label each request with its IP destination, chosen route and next hop. The name evidence is a separate input beside this diagram, not a gateway.

## Run the exercise

```console
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `run/attempt-01/snapshot.txt` and the case. For each request, write the destination IP, every matching route, the winning prefix, any metric comparison and the next-hop address. Use `notes.txt` for your diagram, prediction, evidence, uncertainty, next check and help used. In `answers.json`, replace each blank decision with one label below, add a paragraph to `explanation` and put exact references such as `routes.host.destination` in the `evidence` list. JSON uses double quotes and no trailing commas. Save a separate `answers-first.json` copy in your editor before checking; retain corrections beside the first attempt.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Use the new attempt path with `show`, `check` and `analyse`. Keep `analyse`, `reference/` and the worked example closed during independent attempts. `check` also reveals expected labels for differences, so run it only after preserving the prediction. It checks labels and the presence of prose, not the correctness of the explanation. `verify` checks three authored cases, not learner performance.

Output folders must be fresh and beneath this lab's ignored `run/`; existing and linked paths are refused. Default input is `fixtures/guided.json`; explicit input paths are relative to the terminal's current directory. Exit codes: 0 successful command/matching completed worksheet, 1 differences or incomplete worksheet, 2 invalid input/filesystem error. Leave the attempt folder intact for review. No services or settings need rollback; any later cleanup is limited to disposable copies of your own attempts after preserving evidence.

## Exact teaching model

The [shared contract](../FOUNDATION-CONTRACT.md) defines the eight envelope fields. `context` contains only a nonempty `question`. `data` contains exactly `interfaces`, `routes`, `names`, `requests`. The authoritative JSON must agree with the readable `artifacts.snapshot.txt` text. The table below is a file-format reference; use the explanations and diagram above to reason about the task first.

| Input | Fields and restrictions |
|---|---|
| Interface | `id`, `cidr`; unique lowercase ID, IPv4 address and slash length `/24` through `/30`, usable device address. Interface ranges must not overlap. |
| Route | `id`, `destination`, `via`, `interface`, `metric`; unique ID, network prefix written with the first address of its range, known interface, integer metric 0-9999. `via: null` is the exact connected network, once per interface. Other gateways must be usable neighbours on that interface. |
| Names | Object mapping simple lowercase names such as `archive.test` to one documentation IPv4 address or `null`. Null means no address was supplied, not an asserted DNS response code. Every named request must have an entry. |
| Request | `id`, `target`; unique ID and either a documentation IPv4 address or a supplied `.test` name. Local network/broadcast destinations are rejected. |

Interface/route/request lists contain 1-30 records; names contain up to 30. IDs start with a lowercase letter and use letters, digits and hyphens, at most 40 characters. Write address numbers without extra leading zeroes and slash lengths as numbers: for example, `192.0.2.10/24`. This standard spelling is called canonical form in the helper's error messages. IPv4 values use the three documentation blocks `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`. Route prefixes are within those blocks, with the default route as the only exception. These numbers are examples, not addresses to configure or contact.

First resolve a supplied name; then recognise a host's own address. For other destinations, collect all matching prefixes, keep the longest, and among those keep the smallest metric. A remaining tie stays unresolved. An on-link route selects the destination as next hop; a gateway route selects `via`. The IP destination remains the resolved destination. ARP may be unnecessary if an appropriate mapping is already cached; the worksheet asks which address would need resolution.

| Decision | Exact meaning |
|---|---|
| `local-host` | The destination is an address assigned to this modelled host; no Ethernet next hop selected. |
| `on-link` | The unique winning route has `via: null`; next hop is the destination itself. |
| `via-gateway` | The unique winning route names an on-link gateway. |
| `name-unresolved` | A requested name has a null supplied address; route selection cannot begin. |
| `no-route` | No entry matches the known destination. |
| `equal-route-cost` | More than one route has the best prefix length and metric; this model does not choose one. |

This models a single installed forwarding table. It does not emulate a vendor's entire routing policy, dynamic routing protocol or interface-metric rules. A small metric cannot override a longer matching prefix in this exercise. Invalid or unsupported inputs are rejected rather than silently assigned a result.

## Evidence and review

Deliver an annotated diagram and a worksheet with columns: request ID, supplied name result, matching route IDs, selected route or uncertainty, interface, IP destination, next hop/ARP target, reason and limit. Include Python version, case ID, first prediction, corrected answer and help used. [The worked example](WORKED-EXAMPLE.md) covers only guided evidence; [the drills](DRILLS.md) remove prompts gradually.

Handover prompt: "Show why this destination is local or routed, why this route wins, and what evidence would be required before claiming the remote service is reachable."

## Optional read-only VM comparison

Use only an already authorised isolated Windows lab VM with the NetTCPIP PowerShell module available. This part has **not** been demonstrated by the supplied synthetic fixtures. Run inside that VM, in a fresh private evidence folder. If the cmdlets are absent, record that limit and stop this optional part; installation is not required.

```powershell
$PSVersionTable.PSVersion
Get-NetIPAddress -AddressFamily IPv4 | Format-List InterfaceIndex,InterfaceAlias,IPAddress,PrefixLength,AddressState
Get-NetRoute -AddressFamily IPv4 | Format-List InterfaceIndex,InterfaceAlias,DestinationPrefix,NextHop,RouteMetric,InterfaceMetric
```

Save the displayed output locally using your terminal/editor and record the VM identity and observation time privately. Match an interface index across the two views. Draw its observed local prefix and one route; identify any extra interfaces, routes or metrics outside the offline model. Do not paste real addresses into the synthetic helper, which intentionally rejects them. No ping, DNS query, route addition or subnet change is part of this comparison. No configuration rollback is needed because these commands only read state; preserve the evidence before tidying your own copied notes.

## Limits and primary sources

A predicted first hop does not prove packet delivery, service availability, return routing, DNS availability or firewall permission. The helper excludes IPv6, NAT, VPNs, policy routing, recursive gateways, interface failures and equal-cost load balancing. The snapshots are invented teaching records, not actual operating-system transcripts.

- [IETF RFC 1122, section 3.3.1: host local/remote and gateway decisions](https://www.rfc-editor.org/rfc/rfc1122.html#section-3.3.1)
- [IETF RFC 1812, section 5.2.4.3: longest matching prefix and forwarding-table pruning](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2.4.3)
- [Microsoft Get-NetIPAddress: read IP interface configuration](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipaddress?view=windowsserver2025-ps)
- [Microsoft Get-NetRoute: read destination prefixes, next hops and metrics](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netroute?view=windowsserver2025-ps)

Sources were opened during preparation on 2026-10-25. They support underlying concepts and read-only commands; this lab's bounded labels and tie rule are explicit teaching choices.
