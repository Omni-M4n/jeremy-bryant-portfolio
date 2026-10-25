# Check IPv4 and IPv6 exposure parity

A building can have a front entrance and a side entrance. Closing one does not close the other. A computer may also have two address paths to the same service. This lab asks **whether the observed IPv4 and IPv6 paths match the intended access rule**.

This is a separate lab. First complete network-address-path and controlled-nmap. Allow 25 minutes for supplied evidence. Allow 20 more for an optional read-only check on a prepared pair of isolated VMs.

## Words before fields

**IPv4** and **IPv6** are two address systems. **Dual stack** means a device uses both. **Exposure** means a service can be reached from a stated place. **Parity** here means checking both paths against the same access goal. A **listener** is the waiting program. A **rule family** says which address system a firewall condition covers. A **timeout** means no useful reply arrived before a time limit. It does not tell you the cause.

## Run the supplied exercise

Python 3.10+ on Windows, Linux or macOS, standard library only:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use the Answer vocabulary tables below to write labels. Keep the reference answers closed. Draw two arrows from the client to the service, one per family. Make a table with the address, listener and rule evidence. Add the connection result, intended result and doubts. Save a first attempt and `answers.json` before revealing answers:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

Keep new attempts in new run folders. `check` compares fields. A person must review your written reasons. The supplied cases are made up. The helper does not test a live system.

## Answer vocabulary: use before opening any reference

For each service, the worksheet has a family entry ending in `-ipv4` and another ending in `-ipv6`. A third entry ends in `-parity` and compares them. The labels below cover all cases, not just those supplied. Choose each family's label from its own evidence. Then compare the two.

A not-tested path is always `unverified`. For a connection, first check the intended allow/deny setting. Then check the rule summary. If the summary says deny, use the full label with the disagreement suffix. This is the extra text at the end of the label. For a failed connection, check the intended setting. The rule summary does not prove what caused the failure. A semicolon joins parts of one label. Do not put spaces around it.

| Exact family label | When to use it |
| --- | --- |
| `unverified` | This family was not tested. |
| `reachable-as-intended` | A connection succeeds, allow was intended, and the rule summary does not say deny. |
| `reachable-as-intended;rule-observation-disagreement` | A connection succeeds and allow was intended, but the rule summary says deny. |
| `reachable-outside-intent` | A connection succeeds, deny was intended, and the rule summary does not say deny. |
| `reachable-outside-intent;rule-observation-disagreement` | A connection succeeds, deny was intended, and the rule summary also says deny. |
| `allowed-path-not-working` | The tested path is refused or times out when allow was intended. |
| `not-reachable-cause-unproven` | The tested path is refused or times out when deny was intended. Its cause remains unproven. |

For the parity entry, first check for an untested family. That takes priority over all other labels. Otherwise compare whether the connections worked. Do not compare rule names or assume two failures have the same cause.

| Exact comparison label | When to use it |
| --- | --- |
| `comparison-incomplete` | Either family was not tested. |
| `unequal-observed-reachability` | Both were tested, and exactly one connection succeeded. |
| `both-observed-reachable` | Both connections succeeded. This may still differ from the intended access. |
| `both-observed-not-reachable` | Both were tested and neither connection succeeded. This does not prove equal firewall enforcement. |

## Exact small model

`services` contains one to twelve service rows. Each has its own ID/port and one `intended` value: allow or deny. That value applies to both families. Each family has its own address from a range reserved for examples. It has a listener boolean, which is true or false. It also has a supplied `configured_rule` summary and an outcome. The outcomes are connect, refused, timeout and not-tested. The helper rejects unknown fields, repeated ports and the wrong address family. It also rejects a connected path without a listener. Forwarding is excluded.

A connection shows that this client could reach the service at that time. If deny was intended, that is reachability outside intent. If a connection works but the rule summary says deny, the evidence conflicts. Keep that conflict and check it. A failed connection shows only that this attempt did not reach the service. Even a deny summary does not prove that the rule caused the failure. When allow was intended, failure means the intended path is not working. Not-tested stays unverified.

The parity label compares successful connections only. If one path worked and one failed, their observed reachability is unequal. If both failed, both were observed not reachable. Their causes may differ. Any untested path makes the comparison incomplete. Two working paths are still outside intent if the goal was to deny access. This does not judge the whole network's safety.

An nftables `inet` table can hold both families. But `ip saddr` applies only to IPv4 and `ip6 saddr` only to IPv6. A socket is a program's network endpoint. A dual-stack socket may accept both families, based on its settings and those of the operating system. Inspect the real binds and test the real addresses. Neither the table name nor `[::]` alone proves equal exposure.

## Optional personal check: not run for this package

Use only two owned, disposable Linux VMs that are already set up for dual stack. They must use an internal-only virtual switch. There must be no bridge, NAT, uplink, forwarding or default route. Use their local consoles. Tools must already be present: `ip`, `ss`, `curl`, and `nft` if the VM uses nftables. Stop if either family lacks a prepared route or address. This lab does not set up addresses, open ports or alter rules.

1. Save the agreed target service and exact internal IPv4/IPv6 addresses from its console. Record intended allow/deny behaviour from the same client for both paths. Do not use public targets or derive a target from a fixture address.
2. On the target save `ip -br address`, `ss -ltnp` and, with authorised read access, `sudo nft list ruleset`. Inspect the service's exact bind(s) and every relevant address-specific match. On the client save `ip -4 route` and `ip -6 route`.
3. For an already running HTTP practice service on port 8000, replace the placeholders with the two verified target addresses. Run one probe per family and retain output and exit status. IPv6 literal URLs require square brackets:

```sh
mkdir -p run/parity-session
curl -4 --noproxy '*' --connect-timeout 2 --max-time 4 -v http://TARGET_V4:8000/ > run/parity-session/ipv4.txt 2>&1
echo $? >> run/parity-session/ipv4.txt
curl -6 --noproxy '*' --connect-timeout 2 --max-time 4 -g -v 'http://[TARGET_V6]:8000/' > run/parity-session/ipv6.txt 2>&1
echo $? >> run/parity-session/ipv6.txt
```

4. Check the TCP connection and HTTP status as two separate results. A TCP connection followed by an HTTP error still shows network reachability. Record missing tests as missing. Draw two separate arrows. Label each with its family and actual outcome. If the result differs from intent, add a proposed fix and a test plan. Do not apply that fix in this read-only exercise.
5. Close the terminals after saving evidence. No settings were changed here, so no firewall rollback is needed. If you started a service under another lab, use that lab's cleanup steps.

These VM steps have not been run for this package. The offline table cannot replace evidence that you collected from real connections. Handover: give a reviewer both paths. Ask what else needs testing before you can claim that both enforce the rules equally.

## Primary references

Opened 2026-10-25:

- [RFC 9099, operational IPv6 security considerations](https://datatracker.ietf.org/doc/html/rfc9099)
- [nftables families and family-specific conditions](https://wiki.nftables.org/wiki-nftables/index.php/Nftables_families)
- [Linux IPv6 API and IPV6_V6ONLY](https://man7.org/linux/man-pages/man7/ipv6.7.html)
