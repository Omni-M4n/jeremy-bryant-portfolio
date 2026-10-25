# Route notebook 1: worked example

For f01, 198.51.100.20 uses the local IPv4 default before the change. After it, 198.51.100.0/24 is a more specific match and selects the tunnel. Record `before:local;after:tunnel;intent:met`.

f02, 203.0.113.20, has no matching specific route, so it stays local as intended. f03 is IPv6. The IPv4 subnet route cannot match it; it stays on the local IPv6 default, which does not meet its tunnel intent. Save `before:local;after:local;intent:unmet` for f03.

For q01, files.office.test matches the office.test suffix after the change. That selects resolver 198.51.100.53, whose specific /24 route uses the tunnel. Its intent is met. q02, not-office.test, does not match office.test at a domain boundary. It uses the root rule and resolver 192.0.2.53 on the local default, also as intended.

Draw the resolver selection and its address route as two steps. This models split routing for these examples. It does not prove that a tunnel has been established or that a resolver replied. No actual VPN or DNS request was used.
