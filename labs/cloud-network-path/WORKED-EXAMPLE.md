# Worked example: Library endpoint map

Open this after your guided prediction.
Draw q1 as `192.0.2.8 -> public address 203.0.113.5 -> e1:443`.
e1 has a public address. Its 0.0.0.0/0 route sends replies to external
traffic through igw. The inbound rule covers 192.0.2.8 and port 443.
Use `reachable-in-model`. State the model assumptions with that answer.

q2 comes from 198.51.100.8. Its address and return route checks still pass.
The inbound rule covers only 192.0.2.0/24, so use `inbound-not-allowed`.

q3 targets e2 from outside. e2 has no public address. The first failed check
is `no-public-address`. This does not rule out all internal or forwarded
paths. The guided file lists no relay.

You have drawn a path and reached a result based on the model assumptions.
You have not tested a real connection. Make that clear in your handover.
