# Offline firewall rule review

This original guided exercise asks a small question: **which rule decides a packet's outcome, and does that outcome preserve the access people need?** The lab uses fictional hosts and policies. You read requirements, predict outcomes, and edit a small JSON policy. You do not need to write Python.

This is useful preparation for thinking about cloud network controls, but the simulator is not a cloud firewall or a vendor policy checker. It never connects to a host, sends packets, changes your computer's firewall, or needs an account. All addresses are synthetic documentation addresses. The work is separate practice material, not a university assessment or evidence of professional security experience.

## Command contract

Use Python 3.10+ from this folder. Only the standard library is required. `lab.py` is the maintained entry point.

| Command | Result | Exit codes |
| --- | --- | --- |
| `python lab.py generate` | Creates a fresh `run/` with requirements, probes, starting policy, editable practice policy, packets and supplied solution | `0` created; `2` invalid input, protected fixture path, or nonempty output folder |
| `python lab.py check` | Checks every scenario probe against the practice policy; identifies missing access and excess access | `0` probes match; `1` mismatches; `2` invalid input |
| `python lab.py evaluate --policy PATH --packets PATH` | Reports each packet's outcome, first matching rule ID and one-based rule position; no expected-answer comparison | `0` evaluated; `2` invalid input |
| `python lab.py manifest --verify` | Verifies the shipped source and fixture SHA-256 inventory | `0` matches; `1` changed/missing/additional files; `2` invalid or unreadable manifest |

Use `--help` after any command. Every command accepts `--json` for structured standard output; input errors go to standard error. `generate` accepts `--case` and `--seed`. `generate` and `check` accept `--run PATH`; the default is the `run/` beside this script, even when invoked from another working directory. `check --policy PATH` selects an alternative policy. Explicit paths are relative to your current working directory.

`generate` requires an absent or completely empty destination. It refuses a folder containing notes or any other file, and refuses destinations inside the reference `fixtures/`. Choose a new folder for a new attempt. `check` and `evaluate` only read inputs. The answer keys are supplied learning aids, not proof of an independent attempt.

## Exact model

1. The policy is an **ordered list**. For each packet, the first rule whose five traffic fields all match decides `allow` or `deny`. Later rules do not override it. A more specific rule has no special priority. A packet matching no rule is denied.
2. Each rule names exactly one lowercase transport: `tcp` or `udp`. The same numeric port in another transport is a separate match. There is no `any` protocol.
3. Source and destination each match an exact IPv4 address or a canonical CIDR, such as `192.0.2.20` or `192.0.2.0/24`. An exact address is equivalent to `/32`. CIDRs must use prefix lengths and have no host bits set. There are no hostnames, address wildcards, lists, IPv6, or groups.
4. Every address and entire CIDR must be inside one of `192.0.2.0/24`, `198.51.100.0/24`, or `203.0.113.0/24`. Broader ranges and real addresses are rejected. CIDR membership is mathematical: the simulator does not decide whether an address is usable as a network host, so network/broadcast addresses are not treated specially.
5. Source and destination ports each match an integer from `1` through `65535`, or `"*"` for any port in that range. Packet files need exact addresses and integer ports. There are no port ranges or lists; port zero is intentionally outside this teaching model. The destination port usually identifies the intended service in these cases; it is not interchangeable with the source port.
6. This is a stateless, one-direction packet decision. There is no implicit permission for response traffic, connection tracking, routing, NAT, interface selection, application inspection, TCP flags, ICMP or connection establishment. An `allow` result does not prove a service is listening or that a complete connection would succeed.
7. Unknown or missing fields, duplicate JSON keys, duplicate IDs, unsupported values, noncanonical addresses, booleans used as numbers, malformed JSON and files over 1 MB are errors. Maximums are 64 rules and 256 packets/probes. Invalid input is never silently counted as a valid denial. An empty rule list is valid and denies everything.

A policy has this shape; replace sample addresses with those in your generated requirements:

```json
{
  "schema_version": 1,
  "rules": [
    {
      "id": "portal",
      "action": "allow",
      "protocol": "tcp",
      "source": "192.0.2.0/24",
      "destination": "198.51.100.10",
      "source_port": "*",
      "destination_port": 443
    }
  ]
}
```

This one rule admits client-subnet TCP traffic to one service. It lacks the restricted-host exception and other legitimate services in the exercises, so it is not a complete solution.

## Worked example: a deny that never gets a chance

```console
python lab.py generate --case shadowed-deny --seed 17
python lab.py check
python lab.py evaluate --policy run/practice-policy.json --packets run/packets.json
```

Read `run/scenario.json` first. Its written requirements permit the client subnet to reach the portal over TCP port 443, permit one administrator to reach a separate management host over TCP port 22, and permit one exporter to reach a telemetry host over UDP port 5514. One restricted client must be denied. Everything else has no stated need.

The starting policy puts the portal allowance ahead of the restricted-host denial. The restricted host is a member of the allowed client subnet. The probe named `restricted-portal` is therefore allowed by rule 1, `portal`, even though a later rule says deny. The evaluator stops at that first matching rule. The initial check exits with `1`: **one excess probe, zero missing probes; all eight legitimate probes remain allowed**.

In `run/practice-policy.json`, move the restricted TCP denial ahead of the portal allowance. Check again. The restricted packet should now match the denial first, while ordinary portal clients still reach the portal. Keep the management and telemetry permissions. Deleting all allow rules removes the excess but blocks eight legitimate probes and fails the task.

Before opening the answer key, record the old and new first matching rule for `restricted-portal`, plus one legitimate packet that remained allowed. Then compare with the supplied solution:

```console
python lab.py check --policy run/solution-policy.json
python lab.py evaluate --policy run/solution-policy.json --packets run/packets.json
```

The solution check exits with `0` for 22 probes: eight allowed and 14 denied. This confirms the expected sample outcomes, not that you have explained the rule order independently. Another policy may pass these samples while allowing untested traffic; compare every remaining rule with the written requirements too.

## Drills that change the reasoning

| Case | Starting mistake | What to explain before checking |
| --- | --- | --- |
| `shadowed-deny` | A subnet allow appears before a restricted-host deny | Why the later, more specific deny does not win; which legitimate traffic survives the reorder |
| `narrow-service` | The portal rule allows any TCP destination port across the service subnet | Why source restriction alone is insufficient; how one destination and port preserve portal access without admitting management or other services |
| `missing-access` | A new, explicitly required backup path is omitted | Why denial can be a defect; which exact sender, destination, protocol and port should be added without admitting other clients |
| `protocol-mix` | The telemetry permission uses TCP where UDP is required | Why the correct port number is insufficient; which UDP traffic is missing and which TCP traffic is excess |

```console
python lab.py generate --case narrow-service --seed 29 --run run-narrow
python lab.py check --run run-narrow
python lab.py generate --case missing-access --seed 71 --run run-backup
python lab.py check --run run-backup
python lab.py generate --case protocol-mix --seed 93 --run run-transport
python lab.py check --run run-transport
```

Each initial check is expected to fail with code `1`. Work through the cases one at a time and edit the selected run's `practice-policy.json`. A seed changes fictional host addresses deterministically. It does not change the security model; selecting a different case changes the defect, and the backup case also adds a business requirement.

For a guided attempt, read the worked example and trace one rule at a time. For a hints-only attempt, close the worked example and use this checklist: **source, destination, transport, source port, destination port, rule order, default outcome**. For an unfamiliar attempt, select another case and seed, predict all missing and excess access before running the checker, and justify each edit without looking at the solution.

For an extra challenge, copy a generated `packets.json` to a new file and add a packet with a unique lowercase ID. Keep its five traffic fields exact. Change one thing at a time: source address, destination host, protocol or port. Run `evaluate` with your copied file, predict the outcome first, and identify the first matching rule. `evaluate` reports the policy's result; it does not judge whether that result is appropriate. Record your expectation and rationale separately.

Useful teach-back prompts:

- Why can a later deny fail to block a packet?
- Why would removing every allow rule fail this exercise?
- Which rule preserves the administrator's work, and which probe catches accidentally granting that access to ordinary clients?
- Why is UDP port 5514 different from TCP port 5514 here?
- What happens to a response packet, and why does that limit this simulator's claim about complete connections?
- What untested packet could expose an overly broad rule that passes the supplied probes?

## Files, provenance and checks

- `lab.py`: generator, validators, ordered evaluator, probe checker and manifest command.
- `test_lab.py`: tests rule precedence, source/destination/port distinctions, CIDR edges, necessary access, malformed input, overwrite protection, reproducibility and CLI exit codes.
- `fixtures/<case>/`: four reproducible seed-17 cases, each with written requirements and independently declared expected probe outcomes, starting and solution policies, an editable practice copy, packet inputs and a short guide. Keep these references intact; generate a run before editing.
- `PROVENANCE.json`: synthetic-origin statement, fixture recipes and SHA-256 inventory of source and reference files. Hashes establish file identity, not authorship, originality against every existing exercise, educational validity or competence.
- `run/` and `run-*/`: ignored local attempts. Put your notes here, not in fixtures.

```console
python -m unittest discover -s . -p test_lab.py -v
python lab.py manifest --verify
```

All authored and generated files use UTF-8 and LF line endings; local Git attributes preserve those bytes. Maintainers deliberately revising shipped files can refresh the manifest with `python lab.py manifest --write` after review. This does not replace reviewing the requirements, outcomes or explanation. The tests compare newly generated fixtures byte for byte with the shipped references.

These materials are learning scaffolds. Independent completion and explanation of unfamiliar cases have not been assessed. There is no learner score, professional credential or claim of production firewall experience. A checked personal practice note should state the case, change made, legitimate access preserved, evidence observed and limitations understood.
