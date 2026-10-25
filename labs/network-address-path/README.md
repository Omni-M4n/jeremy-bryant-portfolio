# Map addresses, subnets and a packet's route

**Question:** where does a packet go next? Use its destination, the given name records and a small route table. Explain why an Ethernet next hop can differ from the packet's IP destination.

This beginner task uses made-up records of network links and routes. It does not connect to a network. The optional final task reads the settings of an existing isolated Windows VM. It does not change them. These files and passing checks do not show that someone has done the work or can do it alone.

## Start here

Start with a basic grasp of IPv4 addresses and ports. You need Python 3.10+ and the tools that come with it, a terminal and a text editor. Run commands from this folder. The offline task needs no new install, admin rights, VM or packet capture tool. Allow **30-40 minutes**: 5 to learn terms, 15 to predict, 10 to check and 5-10 to explain. Allow a further 15-25 minutes for the changed case.

## What the address numbers mean

A **packet** is a small bundle of information sent over a network. An IPv4 address, such as `192.0.2.10`, has four whole numbers separated by dots. Each number can be 0 through 255. The dots separate the numbers; this is not a decimal fraction. The whole address matters: `192.0.2.10` and `192.0.2.200` are different addresses.

A **subnet** is a group of addresses treated as being on the same local network. An **interface** is a device's connection to that network. The part after a slash tells you the size of the address group. For example, `/24` covers 256 addresses, `/25` covers 128 and `/26` covers 64. A larger number after the slash means a smaller group. A `/32` route names just one address.

The slash number is called the **prefix length**. A computer stores an IPv4 address as 32 small values called bits; each bit is 0 or 1. `/26` says that the first 26 bits stay fixed for that group. Six bits can change, giving `2 x 2 x 2 x 2 x 2 x 2 = 64` addresses. A **prefix** names a group by its first address and this length.

Try this separate range example: `203.0.113.170/26`. Groups of 64 start at last numbers 0, 64, 128 and 192. The number 170 lies in the group that starts at 128. Its range is `203.0.113.128` through `203.0.113.191`, since `128 + 64 - 1 = 191`. The prefix is `203.0.113.128/26`. In the local networks used here, the first address names the group. The last is its broadcast address. Devices can thus use `.129` through `.190`. Check the slash number as well as the address to decide what is local.

## Where the packet goes next

The **next hop** is the next device to receive the packet on the local link. A **gateway** is a router that sends the packet on to another network. The next hop need not be a gateway. In the guided example, desk `192.0.2.200` is on the workstation's local network. The desk itself is the next hop. A packet for another network may instead go first to a gateway.

A **route** says which address group a path covers and where to send matching packets. Choose the most detailed match. A route for one address is more specific than one for a group of 256 addresses. The **default route**, `0.0.0.0/0`, is used if no more specific route matches. A **metric** is a number used to rank routes. Here, a lower number wins only when the matching prefixes are equally long.

**Name resolution** gives an IP address for a name such as `archive.test`. The route lookup can then use that address. **ARP** can find the MAC address of the next device on the local link. A MAC address is the network adapter address used to send frames on that link. The **ARP target** is the next-hop IP address being looked up. Choosing a route does not show that a packet reached its final destination.

## Guided topology

```text
              local Ethernet: 192.0.2.0/24
workstation .10 ----+---- desk .200
                   +---- gateway .1   -> default path
                   +---- gateway .254 -> 198.51.100.0/24
                   +---- gateway .253 -> 198.51.100.77/32
```

All short addresses on the local line begin `192.0.2`. Arrows show the given first-hop routes. They do not prove that later hops work. Copy this diagram into your notes. For each request, add its IP destination, chosen route and next hop. The name records are a separate input beside this diagram. They are not a gateway.

## Run the exercise

```console
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `run/attempt-01/snapshot.txt` and the case. For each request, write the destination IP and every matching route. Add the winning prefix, any metric comparison and the next hop. Use `notes.txt` for your diagram, prediction, evidence, doubts, next check and help used. In `answers.json`, fill each blank decision with one label below. Add a paragraph to `explanation`. Put exact references such as `routes.host.destination` in the `evidence` list. JSON uses double quotes and no trailing commas. Save a separate `answers-first.json` copy in your editor before checking. Keep corrections beside the first attempt.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Use the new attempt path with `show`, `check` and `analyse`. Keep `analyse`, `reference/` and the worked example closed while working on your own. `check` reveals the expected labels where yours differ. Save your prediction first. It checks labels and requires written fields. It cannot judge whether your explanation is right. `verify` checks three made-up cases. It does not assess your skills.

Output folders must be new and beneath this lab's ignored `run/`. The helper refuses existing and linked paths. Its default input is `fixtures/guided.json`. Paths you enter start from the terminal's current folder. Exit code 0 means success or a complete worksheet with matching labels. Code 1 means differences or missing work. Code 2 means bad input or a file-system error. Keep the attempt folder for review. No service or setting needs to be restored. For later cleanup, first save your evidence. Remove only spare copies of your own attempts.

## Exact teaching model

The [shared contract](../FOUNDATION-CONTRACT.md) defines the eight outer fields. `context` holds only a nonempty `question`. `data` holds exactly `interfaces`, `routes`, `names`, `requests`. JSON is the source of truth. The readable `artifacts.snapshot.txt` text must agree with it. Use the table below to check the file format. Start with the explanations and diagram above to work out the task.

| Input | Fields and restrictions |
|---|---|
| Interface | `id`, `cidr`; unique lowercase ID, IPv4 address and slash length `/24` through `/30`, usable device address. Interface ranges must not overlap. |
| Route | `id`, `destination`, `via`, `interface`, `metric`; unique ID, network prefix written with the first address of its range, known interface, integer metric 0-9999. `via: null` is the exact connected network, once per interface. Other gateways must be usable neighbours on that interface. |
| Names | Object mapping simple lowercase names such as `archive.test` to one documentation IPv4 address or `null`. Null means no address was supplied, not an asserted DNS response code. Every named request must have an entry. |
| Request | `id`, `target`; unique ID and either a documentation IPv4 address or a supplied `.test` name. Local network/broadcast destinations are rejected. |

Interface, route and request lists each hold 1-30 records. Names can hold up to 30. IDs start with a lowercase letter. They use letters, digits and hyphens, with at most 40 characters. Write address numbers without extra leading zeroes. Write slash lengths as numbers, as in `192.0.2.10/24`. The helper calls this standard spelling canonical form in its errors. IPv4 values use three blocks set aside for examples: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`. All route prefixes are within those blocks, apart from the default route. Do not set up or contact these example addresses.

First look up a given name. Then check whether the address belongs to this host. For other destinations, find all matching prefixes. Keep the longest. Among those, keep the smallest metric. If a tie remains, leave it unresolved. An on-link route uses the destination as the next hop. A gateway route uses `via`. The packet's IP destination stays the same. ARP may not be needed if the host has a saved mapping. The worksheet asks which address it would look up if needed.

| Decision | Exact meaning |
|---|---|
| `local-host` | The destination is an address assigned to this modelled host; no Ethernet next hop selected. |
| `on-link` | The unique winning route has `via: null`; next hop is the destination itself. |
| `via-gateway` | The unique winning route names an on-link gateway. |
| `name-unresolved` | A requested name has a null supplied address; route selection cannot begin. |
| `no-route` | No entry matches the known destination. |
| `equal-route-cost` | More than one route has the best prefix length and metric; this model does not choose one. |

This models one forwarding table in use. It does not model all of a vendor's route rules, dynamic routing or interface metrics. Here, a small metric cannot beat a longer matching prefix. The helper rejects invalid inputs and forms it does not support. It does not guess a result for them.

## Evidence and review

Hand in a labelled diagram and a worksheet. Use these columns: request ID, given name result, matching route IDs, chosen route or doubt, interface, IP destination, next hop/ARP target, reason and limit. Include the Python version, case ID, first prediction, corrected answer and help used. [The worked example](WORKED-EXAMPLE.md) covers only the guided case. Use [the drills](DRILLS.md) to practise with less help.

Handover prompt: "Why is this destination local or routed? Why does this route win? What else would you need to check before claiming the remote service can be reached?"

## Optional read-only VM comparison

Use only an isolated Windows lab VM already approved for this task. It must have the NetTCPIP PowerShell module. The made-up cases do **not** show that this part has been done. Run inside that VM, in a new private evidence folder. If the cmdlets are missing, record that limit and stop this optional part. You do not need to install them.

```powershell
$PSVersionTable.PSVersion
Get-NetIPAddress -AddressFamily IPv4 | Format-List InterfaceIndex,InterfaceAlias,IPAddress,PrefixLength,AddressState
Get-NetRoute -AddressFamily IPv4 | Format-List InterfaceIndex,InterfaceAlias,DestinationPrefix,NextHop,RouteMetric,InterfaceMetric
```

Save the shown output in your terminal or editor. Keep the VM identity and time in private notes. Match an interface index across the two views. Draw its local prefix and one route. Note any extra interfaces, routes or metrics outside the offline model. Do not paste real addresses into the helper. It rejects them by design. This comparison uses no ping, DNS query, added route or subnet change. The commands only read state, so no settings need to be restored. Save the evidence before tidying your copied notes.

## Limits and primary sources

A predicted first hop does not prove that a packet arrives or a service works. It does not prove there is a return route, working DNS or firewall permission. The helper leaves out IPv6, NAT, VPNs, policy routing, recursive gateways, interface failures and equal-cost load balancing. These snapshots are made-up teaching records. They are not output from a real system.

- [IETF RFC 1122, section 3.3.1: host local/remote and gateway decisions](https://www.rfc-editor.org/rfc/rfc1122.html#section-3.3.1)
- [IETF RFC 1812, section 5.2.4.3: longest matching prefix and forwarding-table pruning](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2.4.3)
- [Microsoft Get-NetIPAddress: read IP interface configuration](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipaddress?view=windowsserver2025-ps)
- [Microsoft Get-NetRoute: read destination prefixes, next hops and metrics](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netroute?view=windowsserver2025-ps)

Sources were opened while making this lab on 2026-10-25. They explain the concepts and read-only commands. The lab's labels and tie rule were chosen for this small teaching model.
