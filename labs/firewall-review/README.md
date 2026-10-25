# Offline firewall rule review

**Which rule decides what happens to a packet?** Does that rule keep the access people need? This new guided exercise uses made-up hosts and policies. Read the needs, predict the outcomes, and edit a small JSON policy. JSON stores named fields in a text file. You do not need to write Python.

This lab helps you think about cloud network controls. The simulator is not a cloud firewall or a vendor policy checker. It never connects to a host or sends packets. It does not change your computer's firewall or need an account. All addresses come from ranges reserved for examples. The work is separate practice material. It is not a university assessment or proof of professional security experience.

## Command contract

Use Python 3.10+ from this folder. Only the standard library is needed. `lab.py` is the maintained entry point.

| Command | Result | Exit codes |
| --- | --- | --- |
| `python lab.py generate` | Creates a fresh `run/` with requirements, probes, starting policy, editable practice policy, packets and supplied solution | `0` created; `2` invalid input, protected fixture path, or nonempty output folder |
| `python lab.py check` | Checks every scenario probe against the practice policy; identifies missing access and excess access | `0` probes match; `1` mismatches; `2` invalid input |
| `python lab.py evaluate --policy PATH --packets PATH` | Reports each packet's outcome, first matching rule ID and one-based rule position; no expected-answer comparison | `0` evaluated; `2` invalid input |
| `python lab.py manifest --verify` | Verifies the shipped source and fixture SHA-256 inventory | `0` matches; `1` changed/missing/additional files; `2` invalid or unreadable manifest |

Use `--help` after any command. Every command accepts `--json` for structured standard output. Input errors go to standard error. `generate` accepts `--case` and `--seed`. `generate` and `check` accept `--run PATH`. Its default is `run/` beside this script. That stays the same when you run it from another folder. `check --policy PATH` selects another policy. Explicit paths start from your current working folder.

For `generate`, choose a folder that does not exist or is fully empty. A folder with notes or any other file is refused. A path inside the reference `fixtures/` is also refused. Choose a new folder for a new attempt. `check` and `evaluate` only read inputs. The answer keys are learning aids. They do not prove an attempt was made without help.

## Exact model

The policy is an **ordered list**. Start at the top for each packet. Check all five traffic fields in each rule. The first rule that matches all five decides `allow` or `deny`. Stop there. Later rules do not override it. A more specific rule has no extra priority. If no rule matches, the packet is denied. An empty rule list is valid and denies everything.

Use this table to check the five traffic fields:

| Field or constraint | Exact rule |
| --- | --- |
| Transport | Exactly one lowercase `tcp` or `udp`; no `any` protocol. The same port number under a different transport is a separate match. |
| Source and destination address | An exact IPv4 address or canonical CIDR, such as `192.0.2.20` or `192.0.2.0/24`. An exact address means `/32`. A CIDR must use a prefix length and have no host bits set. |
| Address scope | Each address and the whole CIDR must fit inside one of `192.0.2.0/24`, `198.51.100.0/24`, or `203.0.113.0/24`. Broader ranges and real addresses are rejected. |
| Source and destination port | An integer from `1` through `65535`, or `"*"` for any port in that range. No port ranges, lists or port zero. |
| Packet file fields | Exact addresses and integer ports; no subnet or port wildcard |

CIDR is a way to name an address range. “Canonical” means the range is written in its required base form. This model checks range membership with maths. It does not decide whether an address can be used by a host. Network and broadcast addresses get no special treatment. The destination port usually names the intended service in these cases. It cannot be swapped with the source port.

This model is **stateless**: each decision concerns one packet in one direction. Allowing a request does not also allow its response. An `allow` result does not prove a service is listening. It does not prove that a full connection would work.

| Model boundary | Exact limit |
| --- | --- |
| Address features not supported | Hostnames, address wildcards, address lists, IPv6 or groups |
| Network features not modelled | Connection tracking, routing, NAT, interface selection, application inspection, TCP flags, ICMP or connection establishment |
| Invalid fields or values | Unknown or missing fields; duplicate JSON keys or IDs; unsupported values; noncanonical addresses; booleans used as numbers; malformed JSON |
| Size bounds | At most 1 MB per file, 64 rules and 256 packets/probes |

Invalid input is an error. It is never silently counted as a valid denial.

A policy has this shape. Replace the sample addresses with those in your generated requirements:

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

This rule allows TCP traffic from the client subnet to one service. It lacks the restricted-host exception and other required services. It is not a complete solution.

## Worked example: a deny that never gets a chance

```console
python lab.py generate --case shadowed-deny --seed 17
python lab.py check
python lab.py evaluate --policy run/practice-policy.json --packets run/packets.json
```

Read `run/scenario.json` first. It states these needs:

| Sender | Needed access |
| --- | --- |
| Client subnet | Portal over TCP port 443 |
| One administrator | Separate management host over TCP port 22 |
| One exporter | Telemetry host over UDP port 5514 |
| One restricted client | Must be denied |
| Everything else | No stated need |

The starting policy allows the portal before it denies the restricted host. That host belongs to the allowed client subnet. So rule 1, `portal`, allows the probe named `restricted-portal`. A probe is a sample packet used to test a decision. A later rule says deny, but the evaluator has already stopped. The initial check exits with `1`. It reports **one excess probe, zero missing probes; all eight legitimate probes remain allowed**.

In `run/practice-policy.json`, move the restricted TCP denial before the portal allowance. Check again. The restricted packet should now match the denial first. Ordinary portal clients should still reach the portal. Keep the management and telemetry permissions. Deleting all allow rules removes the excess. It also blocks eight valid probes and fails the task.

Keep the answer key closed for now. For `restricted-portal`, record the first matching rule before and after your edit. Add one valid packet that stayed allowed. Then compare with the supplied solution:

```console
python lab.py check --policy run/solution-policy.json
python lab.py evaluate --policy run/solution-policy.json --packets run/packets.json
```

The solution check exits with `0` for 22 probes. Eight are allowed and 14 denied. This confirms the expected sample outcomes. It does not show that you explained rule order without help. Another policy may pass these samples but allow untested traffic. Compare every remaining rule with the written requirements too.

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

Each initial check should fail with code `1`. Work through one case at a time. Edit that run's `practice-policy.json`. A seed changes the made-up host addresses. The same seed and case give the same result. A seed does not change the security model. A different case changes the fault. The backup case also adds a business need.

For a guided attempt, read the worked example. Trace one rule at a time. For a hints-only attempt, close the worked example. Use this checklist: **source, destination, transport, source port, destination port, rule order, default outcome**. For an unfamiliar attempt, choose another case and seed. Predict all missing and excess access before running the checker. Explain each edit without looking at the solution.

For an extra challenge, copy a generated `packets.json` to a new file. Add a packet with a unique lowercase ID. Keep its five traffic fields exact. Change one thing at a time: source address, destination host, protocol or port. Predict the outcome first. Run `evaluate` with your copy and find the first matching rule. `evaluate` reports what the policy does. It does not judge whether that is the right outcome. Record your prediction and reasons separately.

Useful teach-back prompts:

- Why can a later deny fail to block a packet?
- Why would removing every allow rule fail this exercise?
- Which rule keeps the administrator's access? Which probe catches giving that access to ordinary clients by mistake?
- Why is UDP port 5514 different from TCP port 5514 here?
- What happens to a response packet? Why does this limit claims about full connections?
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

All authored and generated files use UTF-8 and LF line endings. Local Git attributes preserve those bytes. After reviewing changes to shipped files, maintainers can refresh the manifest. The command is `python lab.py manifest --write`. It does not replace review of the needs, outcomes or explanation. The tests compare new fixtures with shipped references, byte for byte.

These materials are learning aids. Independent completion and explanation of unfamiliar cases have not been assessed. There is no learner score or professional credential. There is no claim of production firewall experience. A checked practice note should name the case and change made. Add the valid access kept, evidence seen and limits understood.
