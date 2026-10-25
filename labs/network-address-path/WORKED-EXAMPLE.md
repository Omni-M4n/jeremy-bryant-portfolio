# Worked example: guided first-hop decisions

Read this after recording an initial guided prediction. It explains only `guided`; keep it closed during independent practice.

The host is `192.0.2.10/24`. Its connected network is `192.0.2.0/24`, containing addresses from `.0` through `.255`; ordinary usable hosts are `.1` through `.254`. The three gateways `.1`, `.254` and `.253` are on this link. The default route's metric is 5, but metric is considered only after prefix length.

| Request | Evidence and reasoning | Decision | Next hop |
|---|---|---|---|
| `desk` | `192.0.2.200` matches `link` `/24` and `default` `/0`; `/24` wins. | `on-link` | `192.0.2.200` |
| `archive` | `names.archive.test` supplies `198.51.100.77`. Matches `host` `/32`, `remote` `/24`, `default` `/0`. The host route wins even with metric 999. | `via-gateway` | `192.0.2.253` |
| `remote-general` | `198.51.100.88` is in `remote` `/24`, but it is not the `/32` host address. | `via-gateway` | `192.0.2.254` |
| `docs` | `names.docs.test` supplies `203.0.113.8`; only the default entry matches. | `via-gateway` | `192.0.2.1` |
| `unknown` | `names.lost.test` is null. There is no destination IP for the route lookup. This does not identify a DNS error code or cause. | `name-unresolved` | Not established |
| `self` | `192.0.2.10` equals `interfaces.eth0.cidr`'s address. | `local-host` | No Ethernet next hop |

For `archive`, draw `host .10 -> gateway .253 -> destination 198.51.100.77`. The outgoing packet still has IP destination `198.51.100.77`. Its local Ethernet frame would go to the gateway's MAC address; if resolution is needed, the ARP target would be `192.0.2.253`. Naming an IP gateway does not mean its MAC address or downstream route is present in this evidence.

An example guided worksheet paragraph is: "The supplied name mapping resolves archive.test to 198.51.100.77. The host route, remote subnet route and default route match. Prefix length 32 is more specific than 24 or 0, so the host route wins before metric comparison. The next hop is 192.0.2.253 on eth0. I can predict the first hop, but I cannot establish that the router will forward the packet or that the service will respond."

Useful references are `names.archive.test`, `routes.host.destination`, `routes.host.via`, `routes.remote.destination` and `interfaces.eth0.cidr`. Point to the actual case fields or matching snapshot rows, not merely "the network looks right".

After checking, keep the first answer and write one correction if needed. A useful negative check is `unknown`: having a default route does not supply an absent name-to-address mapping. A person should review both the selected label and the explanation before recording progress beyond guided practice.
