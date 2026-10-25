# Worked example: guided first-hop decisions

Read this after saving your first prediction. It explains only `guided`. Keep it closed while working on your own.

The host is `192.0.2.10/24`. Its connected network is `192.0.2.0/24`. This range runs from `.0` through `.255`. Hosts can use `.1` through `.254` on this network. The three gateways `.1`, `.254` and `.253` are on this link. The default route's metric is 5. Check prefix length before using the metric.

| Request | Evidence and reasoning | Decision | Next hop |
|---|---|---|---|
| `desk` | `192.0.2.200` matches `link` `/24` and `default` `/0`; `/24` wins. | `on-link` | `192.0.2.200` |
| `archive` | `names.archive.test` supplies `198.51.100.77`. Matches `host` `/32`, `remote` `/24`, `default` `/0`. The host route wins even with metric 999. | `via-gateway` | `192.0.2.253` |
| `remote-general` | `198.51.100.88` is in `remote` `/24`, but it is not the `/32` host address. | `via-gateway` | `192.0.2.254` |
| `docs` | `names.docs.test` supplies `203.0.113.8`; only the default entry matches. | `via-gateway` | `192.0.2.1` |
| `unknown` | `names.lost.test` is null. There is no destination IP for the route lookup. This does not identify a DNS error code or cause. | `name-unresolved` | Not established |
| `self` | `192.0.2.10` equals `interfaces.eth0.cidr`'s address. | `local-host` | No Ethernet next hop |

For `archive`, draw `host .10 -> gateway .253 -> destination 198.51.100.77`. The packet still has IP destination `198.51.100.77`. Its local Ethernet frame would go to the gateway's MAC address. If that address needs to be found, the ARP target would be `192.0.2.253`. The gateway's IP is given here. Its MAC address and later route are not.

An example guided answer is: "The given name record maps archive.test to 198.51.100.77. The host route, remote subnet route and default route match. Prefix length 32 is more specific than 24 or 0. The host route wins before we compare metrics. The next hop is 192.0.2.253 on eth0. This predicts the first hop. It does not show that the router will forward the packet or that the service will reply."

Useful references are `names.archive.test`, `routes.host.destination`, `routes.host.via`, `routes.remote.destination` and `interfaces.eth0.cidr`. Point to these case fields or their matching snapshot rows. A claim that "the network looks right" gives no such evidence.

After checking, keep the first answer and add any correction. For a useful negative check, look at `unknown`. A default route cannot fill in a missing name-to-address mapping. Ask a person to review both your label and your reason before moving past guided practice.
