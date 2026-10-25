# Review VPN routes and DNS scope

A school bus carries some trips while other trips use a local road. Choosing a route does not decide where someone asks for directions. In the same way, a VPN route and a DNS lookup path need separate checks. This lab asks **which route serves each address and each name query**. It also asks **whether those choices match the stated goal**.

This is a separate lab. First complete network-address-path and dns-cache-records. Allow 30 minutes and a later 10-minute recall session. No VPN account, login details or connection is needed.

## Words before fields

A **VPN tunnel** carries traffic through an extra connection. A **route** chooses where traffic goes next. A **prefix** describes a group of addresses, such as one subnet. A longer prefix is a more specific match. A **metric** is a rank used here when routes are equally specific. The smaller metric wins. A **default route** catches addresses without a more specific route. **Split routing** sends selected traffic through the tunnel. **Full routing** is a goal to carry the relevant traffic through it. You must still check routes for both address families and any exceptions. A **DNS resolver** answers name lookups. A **suffix rule** picks a resolver for names ending in a given domain.

## Run the supplied exercise

Python 3.10+ on Windows, Linux or macOS, standard library only:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Save a before/after route map and a separate DNS-path table. Predict every row and record the winning prefix or suffix before opening answers. Then use:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

Keep the first attempt and use new run folders. `analyse` and reference files reveal the answer. Matching labels do not assess your written reasons. They do not show that you used a real VPN.

## Exact small model

The case has route and DNS-rule lists from before and after a change. It also has traffic flows and name queries. Every route has a strict network prefix. This means it names the start of a network, not a host within it. It has a metric of zero or more and a path of `local` or `tunnel`. For each address, choose the longest matching prefix in its own address family. Then choose the lowest metric from those equally specific routes. The helper rejects ties with the same prefix and metric. Routing across multiple tied paths is outside the model. A higher metric on a more specific route can still win. No matching route produces `none`.

The allowed addresses are the IPv4 blocks reserved for examples and `2001:db8::/32`. Routes may use smaller ranges within them or a family default. Domains are lowercase `.test` names. A DNS rule has a suffix and a resolver address. The root suffix `.` is a fallback match. Otherwise match a whole domain or a suffix split off by a dot. For example, `not-office.test` is not a child of `office.test`. Select the longest suffix. If several servers share that best suffix, this model sends to every one. It then uses the route table for each resolver address. A mixed result is `local+tunnel`. This does not meet a tunnel-only goal. No matching DNS rule produces `none`.

This model uses **unbound resolvers**: their queries are not tied to a network link. It is **not a systemd-resolved emulator**. It does not copy how that real DNS service works. Real resolvers may tie queries to links, use default-route rules or use saved answers. They may try another server if one fails. A program may also send its own encrypted DNS query and skip the system's resolver. The source documents explain why DNS can have its own scope. This exercise uses the simpler rules stated here. It does not treat real per-link settings as unbound addresses.

`before:<path>;after:<path>;intent:met` means the chosen after-path equals the row's stated goal. `unmet` includes no route, no resolver, a wrong path or mixed DNS paths. Choosing a route does not prove that the tunnel is connected or that traffic was encrypted. It does not prove that the resolver answered or that the far end can be reached. The model excludes policy rules, multiple routing tables and source routing. These can choose a path using rules beyond this model. It also excludes interface binding, which ties traffic to a network link. ECMP spreads traffic across equal-cost paths; that and tunnel transport details are outside the model too. The helper rejects unknown fields, invalid addresses, repeated entries and unsupported ties.

## Practical evidence and bounded next checks

Work with the made-up snapshots first. Draw one arrow per traffic destination. Draw a separate arrow from the client to each chosen resolver. Mark IPv4 and IPv6 on their own. On a copy, change one prefix or DNS suffix. Save a prediction and rerun the helper. This is a local file exercise, with no network activity.

For an optional read-only comparison, use an owned isolated Linux VM that is already set up. You must have an existing lab VPN setup with permission to use it. Do not connect a provider VPN or install software. Do not change routes, supply login details or alter DNS for this exercise. If that setup does not exist, leave this section unrun. With iproute2 and systemd-resolved already present, save:

```sh
mkdir -p run/route-session
ip -4 route show > run/route-session/routes-v4.txt
ip -6 route show > run/route-session/routes-v6.txt
ip rule show > run/route-session/rules-v4.txt
ip -6 rule show > run/route-session/rules-v6.txt
resolvectl status > run/route-session/resolvers.txt
```

Choose one exact owned internal destination. `ip route get DESTINATION_V4` or `ip -6 route get DESTINATION_V6` reads the kernel's route choice without sending a probe. The kernel is the core of the operating system. Save the chosen interface, source address and route. Inspect each link's DNS domains and default-route settings in `resolvectl status`. A route query to the server may not copy a DNS request tied to an interface. If policies, interface binding or a program's own DNS are present, note that this helper cannot copy the setup. Plan a later test, with permission, to record the real path and name-query destination. No such live test is part of this package.

These optional commands have not been run for this package. Do not use made-up outputs as personal evidence. No live settings are changed. Cleanup is limited to keeping or removing your own copies. Handover: supply the two route maps, DNS table and intended scope. Include evidence against your view and a small plan to check it. Remove private addresses or names before sharing personal evidence publicly.

## Primary references

Opened 2026-10-25:

- [Linux ip-route, destination route selection and route get](https://man7.org/linux/man-pages/man8/ip-route.8.html)
- [systemd-resolved, domain and per-link DNS routing](https://www.freedesktop.org/software/systemd/man/latest/systemd-resolved.service.html)
- [RFC 9099, separate IPv6 operational considerations](https://datatracker.ietf.org/doc/html/rfc9099)
