# Test firewall enforcement and rollback

Suppose one classroom door should stay open while another is closed for a repair. Testing only the closed door does not show whether people can still use the hall. A useful network rule test checks a path that should work and one that should be blocked. It then checks that both work again after cleanup.

This extends [firewall-review](../firewall-review/README.md). The earlier exercise asks you to reason about rules. This one adds a real test on spare virtual machines, called VMs. You check which paths work, count packets and undo the change. First complete firewall-review, network-address-path and isolated-lab-workbench. Allow 20 minutes for supplied evidence and 40 minutes for a separate VM session.

## Words before fields

A **firewall** applies rules to network traffic. **Allow** lets matching traffic pass. **Drop** discards it without a reply. A **listener** is a waiting service. A **counter** counts matching packets. A **control** is a path you expect to keep working while you test another. A **baseline** records the starting state. **Rollback** removes the change and checks that the starting state works again. **nftables** is the Linux firewall system used in the optional VM steps. `nft` is its command. A **table** groups rules and a **chain** sets when rules run. A **hash** is a file fingerprint. It does not prove that the file's contents are correct.

## Supplied evidence exercise

Python 3.10+ on Windows, Linux or macOS, standard library only:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Use the Answer vocabulary tables below to write labels. Keep the reference answers closed. Write a first prediction, evidence and doubts in `notes.txt`; complete `answers.json`. Only then open the worked example and run:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

These commands do not inspect or change the machine's firewall. The cases are made up. A matching worksheet does not show that you ran a real test. It does not assess your written reasons.

## Separate learner VM procedure: not run for this package

Use a disposable Linux target VM with systemd, nftables, Python 3.10+, iproute2 and a local console. You also need a second owned Linux VM with curl. Tools must already be installed. Use an internal-only virtual switch with no uplink, NAT, bridge or default route. Never run these rule commands on your normal computer or an original coursework VM. Do not use a remote-only machine or a shared service. Save a VM snapshot and keep its console open. From both consoles, confirm who owns the VMs and their exact client/target IPv4 addresses. `CLIENT_IP` and `TARGET_IP` below are placeholders. Replace them with the confirmed addresses.

**Baseline gate.** These steps support an empty nftables ruleset only. There must be no active firewall manager, containers, forwarding or iptables-legacy rules. Inspect `ip route` and `sudo nft list ruleset`. Inspect `sudo iptables-save` and `sudo ip6tables-save` if the legacy tools exist. Record versions. Stop if a manager is active or another rule system is present. Also stop if you cannot prove this clean state. Do not clear old rules to make the lab fit. Use a fresh disposable VM instead.

On the target, create a new folder. All commands must succeed before continuing:

```sh
mkdir -p run/firewall-session/empty
sudo nft list ruleset > run/firewall-session/rules-before.nft
test ! -s run/firewall-session/rules-before.nft
sha256sum run/firewall-session/rules-before.nft
```

`test` must return zero and the saved file must be empty. Save the hash. Start one server in each of two target terminals, bound only to the target's internal address:

```sh
python3 -m http.server 8000 --bind TARGET_IP --directory run/firewall-session/empty
```

```sh
python3 -m http.server 8001 --bind TARGET_IP --directory run/firewall-session/empty
```

Save `ss -ltnp` in a third terminal. Stop if either port was already in use. Do not stop unknown programs. On the client create `run/firewall-session`. Run each probe and save its exit status at once:

```sh
curl --noproxy '*' --connect-timeout 2 --max-time 4 -sS -o /dev/null -w '%{http_code}\n' http://TARGET_IP:8000/ > run/firewall-session/before-8000.txt 2>&1
echo $? >> run/firewall-session/before-8000.txt
curl --noproxy '*' --connect-timeout 2 --max-time 4 -sS -o /dev/null -w '%{http_code}\n' http://TARGET_IP:8001/ > run/firewall-session/before-8001.txt 2>&1
echo $? >> run/firewall-session/before-8001.txt
```

Both should return HTTP 200 and exit zero. Record the results in your matrix, which is a table of tests. Do not proceed on failure.

**One temporary rule.** On the target save this as `run/firewall-session/lesson.nft`, replacing only CLIENT_IP with the verified client address:

```text
table inet lesson {
    chain input {
        type filter hook input priority 0; policy accept;
        ip saddr CLIENT_IP tcp dport 8001 counter log prefix "lesson-drop " drop
    }
}
```

The `ip saddr` condition makes this rule IPv4-only even inside an `inet` table. This lab tests that one path. See ipv6-parity for a check of both address systems. Check the rule's syntax. Before loading it, set a timed rollback that can run without the console:

```sh
sudo nft --check --file run/firewall-session/lesson.nft
sudo systemd-run --unit=lesson-rollback --on-active=10m "$(command -v nft)" delete table inet lesson
systemctl status lesson-rollback.timer
sudo nft --file run/firewall-session/lesson.nft
sudo nft list table inet lesson > run/firewall-session/rules-during.nft
```

Stop on any error. Verify that the timer is active and the one rule exists. Finish testing within five minutes. If the timer fires, preserve that fact and do not reload the rule without restarting a fresh timed session.

**Positive and negative checks.** Repeat the same two client curl commands using filenames `during-8000.txt` and `during-8001.txt`. Expected: 8000 still returns 200; 8001 times out. Save the exit codes. On the target, save `ss -ltnp`. Save `sudo nft list table inet lesson` again to see the counter change. Save `sudo journalctl -k --since '5 minutes ago'` and find the `lesson-drop` lines. If logs are missing, record the gap. Do not invent them. Counter hits count packets, including retries. They do not count successful attacks or whole connections. A timeout alone does not prove that the rule caused it. You also need the working control, the listener evidence and a rise in the matching counter.

**Rollback and verify.** At the target's local console, before the timer fires:

```sh
sudo nft delete table inet lesson
sudo systemctl stop lesson-rollback.timer
sudo nft list ruleset > run/firewall-session/rules-after.nft
sha256sum run/firewall-session/rules-after.nft
cmp run/firewall-session/rules-before.nft run/firewall-session/rules-after.nft
```

If the timer already removed the table, record the deletion error. Check that the table is absent. Do not remove any other table. Repeat the client probes with `after-8000.txt` and `after-8001.txt`; both must work again. Keep both listeners running until these checks finish. Then use Ctrl+C for each server and save a final `ss -ltnp` snapshot. The before/after exports must be empty and byte-equal. If you cannot confirm rollback, use the VM console to restore the saved disposable snapshot. Keep the failure evidence. Never flush another machine's firewall.

## Answer vocabulary: use before opening any reference

Use one exact probe label for each probe ID. Add one rollback label for the `rollback` entry in `answers.json`. These tables give every supported label. They do not give any case's answers.

Check the baseline first. If that probe did not connect before the change, use `baseline-not-established`. Later results do not change that choice. Otherwise follow its intended allow/deny result. Check rollback on its own after all probes. Evidence that the rule worked does not prove that rollback worked.

| Exact probe label | When to use it after checking the baseline |
| --- | --- |
| `baseline-not-established` | This probe did not connect before the change. This takes precedence over all other probe labels. |
| `permitted-supported` | Allow was intended and this probe still connects during the change. |
| `permitted-path-failed` | Allow was intended but this probe is refused or times out during the change. |
| `deny-not-enforced` | Deny was intended but this probe still connects during the change. |
| `deny-supported-by-control-and-counter` | Deny was intended; this probe times out while its listener remains; its matching drop counter rises; and every allow control connected both before and during the change. |
| `failure-needs-cause-check` | Deny was intended and the probe fails, but one or more of the preceding support conditions is missing. |

| Exact rollback label | When to use it |
| --- | --- |
| `rollback-supported` | The exports have matching hashes, the temporary rule is removed, and every probe connected both before the change and after rollback. |
| `rollback-not-confirmed` | Any one of those rollback conditions is missing. |

Use the actual observations even when they differ from the intended behaviour. Explain what each label establishes and what still needs checking.

## Exact small model and evidence

The helper accepts `baseline_hash`, `restored_hash`, `rule_removed` and two to eight `probes`. Each probe has its own ID/port and intended allow/deny result. It records the listener and outcome before, during and after the change. It also records the matching drop-counter increase during its attempt. Only `connect`, `refused` and `timeout` are supported. The model excludes forwarding and reuse of a connection. Unrelated probes must not run at the same time. The helper rejects a connection without a listener or a successful probe with matching drop hits. It also rejects repeated ports, unknown fields and invalid counts.

A failed baseline is not enough. An allowed path must still connect. A denied path needs all five checks: it connected before; its listener remains; it times out; matching drop hits rise; every allowed control still works. Other failures need cause checks. Rollback needs matching export hashes and removal of the rule. All paths must connect both before the change and again after rollback. Matching hashes alone are not enough.

Save exports, command/version notes and the before/during/after matrix. Keep listener snapshots, counters, any logs and cleanup results too. Mark real VM evidence missing until you collect it. Handover: ask a reviewer to explain one other possible cause. Ask them to check rule effects and rollback as two separate claims.

## Primary references

Opened 2026-10-25:

- [nftables tables, chains, counters and rules](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes)
- [nftables address families and family-specific matches](https://wiki.nftables.org/wiki-nftables/index.php/Nftables_families)
- [systemd-run timer units and on-active scheduling](https://www.freedesktop.org/software/systemd/man/latest/systemd-run.html)
- [Python temporary HTTP server](https://docs.python.org/3/library/http.server.html)
