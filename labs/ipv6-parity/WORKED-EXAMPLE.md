# Address notebook 1: worked example

The access goal is deny for both paths. For s01-ipv4, the listener is present and the probe times out. The rule summary says deny. Save `not-reachable-cause-unproven`. The result fits the goal. It does not prove that the rule caused the failure.

For s01-ipv6, a connection succeeds and the rule has not been reviewed. Save `reachable-outside-intent`. The IPv4 result cannot override that result. For s01-parity use `unequal-observed-reachability`.

Draw `client -> IPv4 address -> service` with a timeout label and `client -> IPv6 address -> service` with a connected label. A revised design would need an IPv6 rule that meets the access goal. It would also need fresh tests from this client. That is a proposed action, not an applied fix. Inspect the IPv6 rules and binds before choosing a change.
