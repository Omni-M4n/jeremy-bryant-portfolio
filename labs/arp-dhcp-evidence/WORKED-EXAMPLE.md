# Worked example: one allocation and one ARP exchange

Use only after saving your first guided prediction. The fictional observation point sees frame numbers 1 through 6. It is a summary of selected fields, not a real capture.

## Follow the DHCP transaction

All four DHCP frames use client MAC `02:00:00:00:00:10` and xid `1001`. Those two fields link the messages within this case.

| Frame | Observation | What it contributes |
|---|---|---|
| 1 | Discover, ciaddr and yiaddr both zero | The start of the supplied allocation attempt. |
| 2 | Offer: server `192.0.2.1`, yiaddr `192.0.2.20`, lease 3600 | A proposed configuration; not by itself a completed allocation. |
| 3 | Request: requested IP `192.0.2.20`, server ID `192.0.2.1` | The observed client selection. |
| 4 | ACK: same server and yiaddr `192.0.2.20`, lease 3600 | A matching acknowledgement to the selected request. |

For query `lease-a`, the label is `allocation-ack-observed`. The Offer, Request and ACK agree on server and address, and both initial steps are present. Useful references are `lease-a frames 1-4 client_mac/xid`, `frame 3 requested_ip/server_id` and `frame 4 yiaddr/server_id/lease_seconds`.

Do not replace that result with "the internet is working". No application traffic, router forwarding or downstream service evidence is supplied. The positive lease value also gives no absolute expiry timestamp in this summary.

## Follow ARP to the local next hop

Frame 5 asks for the mapping of `192.0.2.1`. Its sender is `192.0.2.20` / `02:00:00:00:00:10`. Frame 6 replies with sender `192.0.2.1` / `02:00:00:00:00:01`, target IP `192.0.2.20` and target MAC `02:00:00:00:00:10`. The requested address and the reply's two target fields agree with the query. Frame 5 precedes frame 6.

Therefore `gateway` is `exchange-observed`. The observed mapping is `192.0.2.1 -> 02:00:00:00:00:01`. This shows a corresponding request and reply; it does not authenticate the sender or prove later packet delivery.

For `gateway-lease-link`, frame 5 occurs after ACK frame 4. The ARP requester uses the ACK's `192.0.2.20` address and the same client MAC. The result is `same-client-address-observed`. That is evidence consistent with the client using the acknowledged address, while the causal claim "this ACK definitely configured this host" is stronger than the supplied fields support.

## Write the handover

A suitable guided explanation is: "Frames 1-4 form a matching initial transaction for client MAC ending 10 and xid 1001. Request frame 3 selects 192.0.2.20 from server 192.0.2.1, and ACK frame 4 agrees. ARP frames 5-6 match on requester/target IPs and requester MAC. The later request uses the acknowledged client address. I cannot establish current lease validity, sender ownership or downstream connectivity from this excerpt. A narrow next check would be a contemporaneous client lease record if that stronger claim were needed."

Keep your initial response, the checked result and any correction. A person should assess the field references and limits, rather than treating three matching worksheet labels as independent competence.
