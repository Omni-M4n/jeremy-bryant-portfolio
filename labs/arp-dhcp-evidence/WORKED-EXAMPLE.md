# Worked example: one allocation and one ARP exchange

Use this only after saving your first guided prediction. The made-up capture point sees frames 1 through 6. This is a summary of chosen fields, not a real capture.

## Follow the DHCP transaction

All four DHCP frames use client MAC `02:00:00:00:00:10` and xid `1001`. Those two fields link the messages within this case.

| Frame | Observation | What it contributes |
|---|---|---|
| 1 | Discover, ciaddr and yiaddr both zero | The start of the supplied allocation attempt. |
| 2 | Offer: server `192.0.2.1`, yiaddr `192.0.2.20`, lease 3600 | A proposed configuration; not by itself a completed allocation. |
| 3 | Request: requested IP `192.0.2.20`, server ID `192.0.2.1` | The observed client selection. |
| 4 | ACK: same server and yiaddr `192.0.2.20`, lease 3600 | A matching acknowledgement to the selected request. |

For query `lease-a`, the label is `allocation-ack-observed`. The Offer, Request and ACK agree on server and address. Both first steps are present. Useful references are `lease-a frames 1-4 client_mac/xid`, `frame 3 requested_ip/server_id` and `frame 4 yiaddr/server_id/lease_seconds`.

Do not call this result "the internet is working". The records show no app traffic, forwarded packets or service reached through a router. The positive lease value also gives no exact expiry time in this summary.

## Follow ARP to the local next hop

Frame 5 asks for the mapping of `192.0.2.1`. Its sender is `192.0.2.20` / `02:00:00:00:00:10`. Frame 6 replies with sender `192.0.2.1` / `02:00:00:00:00:01`. Its target IP is `192.0.2.20`. Its target MAC is `02:00:00:00:00:10`. The sought address and the reply's two target fields match the query. Frame 5 comes before frame 6.

Thus `gateway` is `exchange-observed`. The mapping in view is `192.0.2.1 -> 02:00:00:00:00:01`. This shows a matching request and reply. It does not prove the sender's identity or that later packets arrive.

For `gateway-lease-link`, frame 5 comes after ACK frame 4. The ARP requester uses the ACK's `192.0.2.20` address and the same client MAC. The result is `same-client-address-observed`. These fields fit a client using the address from the ACK. They do not prove that this ACK set up this host.

## Write the handover

A guided answer could say: "Frames 1-4 match for client MAC ending 10 and xid 1001. They form a full first-lease exchange. Request frame 3 selects 192.0.2.20 from server 192.0.2.1. ACK frame 4 agrees. ARP frames 5-6 match on requester/target IPs and requester MAC. The later request uses the client address from the ACK. This excerpt cannot prove the lease is valid now. It cannot prove address ownership or a working route beyond this link. A client lease record from the same time would be a small next check if needed."

Keep your first answer, checked result and any correction. A person should assess the field references and limits. Three matching labels do not show that you can do this work alone.
