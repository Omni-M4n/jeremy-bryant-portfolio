# Test a small Snort rule

Predict, run and explain a Snort 3 rule on four harmless packet files. Then change one content option and retest. You edit a rule, use the tool and review evidence. You do not need to write code.

Allow 40-60 minutes. Python 3.10+ creates the files with its standard library. To test detection, you need **Snort 3 already installed** with the `alert_json` logger. Snort 2 cannot run this exercise. Use an existing Linux lab if that is where Snort 3 is installed. On Windows, you can prepare and inspect the files. Mark Snort execution as pending until you have a suitable existing setup. This lab includes no installs, live interface capture or elevated commands. It uses no public target and changes no VM settings.

## What the files represent

`fixtures/cases.json` defines four made-up requests. Each PCAP has nine Ethernet/IPv4/TCP packets. They form a handshake, one HTTP request, an acknowledgement and a connection close. There is no HTTP response. Only frame 4 has a payload, which is the data carried by the packet. The client is `192.0.2.10:45000`. Its made-up server is `198.51.100.20`. `orchard.test` is a made-up HTTP Host value. These addresses are reserved for examples. The generator sends no packets.

The Ethernet addresses and times are fixed teaching values. These PCAPs are **synthetic**, which means they were made up. They were never captured from a real session. `PROVENANCE.json` records source and output SHA-256 hashes. A hash helps check that a file is the same. These hashes can check that generation gives the same files. They do not prove a real capture took place or that you understand the task.

| Fixture | Marker in frame 4 | Destination port | Original rule prediction |
| --- | --- | --- | --- |
| positive | `ORCHARD-CANARY-42` | 18080 | one SID 1000001 alert |
| near-miss | `orchard-canary-42` | 18080 | zero |
| negative | `ORDINARY-BOOKING-42` | 18080 | zero |
| wrong-port | `ORCHARD-CANARY-42` | 18081 | zero |

The predictions in `reference/expected.json` were written by hand. They are separate from the packet writer and are not saved Snort results. Negative controls test when the rule should stay quiet. Zero alerts alone cannot prove that input is safe. They also cannot prove the engine ran as it should.

## Maintained commands

Open a terminal in this folder. Use `python3` in place of `python` where needed.

```text
python lab.py --help
python lab.py verify
python lab.py prepare --out run/guided-01
python lab.py run-snort --attempt run/guided-01 --out run/snort-01
```

`verify` checks the supplied hashes and exact generated PCAP bytes. It also checks packet structure and checksums. It **does not run Snort**. `prepare` writes the PCAPs, a rule copy, source record and worksheet. Save your own prediction in the worksheet before you run the engine.

`run-snort` looks for `snort` or `snort3` on PATH. To name an existing executable, use this form:

```text
python lab.py run-snort --attempt run/guided-01 --out run/snort-02 --snort /usr/local/bin/snort
```

Use your real installed path. This example does not install Snort. Put a Windows path with spaces in quotes. If the engine is absent, `result.json` says `unverified`. The command returns 2. Do not replace this result with a predicted count.

For each file, the wrapper runs this command's equivalent. It uses full paths and a fresh log folder for each case.

```text
snort -q -R local.rules -r input.pcap -A alert_json -l CASE_OUTPUT --lua "search_engine = { detect_raw_tcp = true }"
```

This explains the recorded command. Use `run-snort` to prepare safe output paths. `-r` reads a PCAP. `-R` loads the local rule. `-A` selects JSON alerts. The wrapper saves the engine version, exact command, rule hash and input hashes. It keeps stdout, stderr, exit codes and parsed alerts too. Stdout is normal tool output; stderr is its error output. An error or timeout does not count as zero alerts. Read each case's saved evidence even if counts match. The official [rule loading guide](https://docs.snort.org/start/rules) and [alert logging guide](https://docs.snort.org/start/alert_logging) explain these options and outputs.

All command output goes into fresh direct children `run/NAME`. The tool refuses existing output, links and paths that escape that folder. Input PCAPs must match the prepared files exactly. You may edit only the copy of the one-line rule in your run folder. Allowed changes are its content text, optional `,nocase`, message and revision. You may also choose destination port 18080 or 18081. Includes, scripts and other rule actions are refused.

Exit code `0` means the requested task finished. For `run-snort`, it also means counts matched. Code `1` means a count mismatch, engine error, timeout or unreadable alert output needs review. Code `2` means bad input, a missing engine, or failure to start or prepare. Read each case's status and output before using its result. No code proves mastery.

## Read the rule, then change it

The supplied rule checks TCP from `192.0.2.10` to `198.51.100.20:18080`. It alerts when the raw data contains `ORCHARD-CANARY-42`. This marker is harmless. The header's address, direction and port must also match. SID `1000001` names this rule. `rev` tracks its version. See the official [rule structure guide](https://docs.snort.org/rules/headers/), [content guide](https://docs.snort.org/rules/options/payload/content) and [raw-data option](https://docs.snort.org/rules/options/payload/raw_data).

For a changed test, first prepare `run/changed-01`. Open its `local.rules` copy in a text editor. Change only this content line:

```text
content:"ORCHARD-CANARY-42";
```

Replace it with this line:

```text
content:"ORCHARD-CANARY-42",nocase;
```

Also change `rev:1;` to `rev:2;`. Predict which controls will be affected. Save the prediction, then run:

```text
python lab.py run-snort --attempt run/changed-01 --out run/snort-changed-01 --expect case-insensitive
```

Record the real counts and evidence for all four cases. Compare each result with your saved prediction. The [nocase option](https://docs.snort.org/rules/options/payload/nocase) controls letter-case matching. Check the header conditions as well when explaining a result.

A **rule header** selects traffic. **Content** is a pattern of bytes. A **SID** names a rule. A **revision** labels its version. A **positive control** is meant to trigger the rule. A **negative control** is meant to stay quiet. **PCAP** is a packet-file format. An **alert** means a condition matched. It is not proof of an attack.

Keep your worksheet, rule copy and actual engine output. If the engine has not run, mark it pending. Continue with [drills](DRILLS.md). Use the [worked example](WORKED-EXAMPLE.md) after your prediction. For handover, explain what changed after nocase. State which controls stayed quiet. Show the evidence that Snort processed the files.

This small rule matches raw bytes. It cannot prove harmful intent or that encrypted TLS content can be seen. It does not test robust HTTP parsing, speed or real-world detection quality. It does not teach matches spread over several packets. The raw-data choice and raw TCP setting make this single-packet test easy to inspect. Snort explains raw data and processed buffers in its [packet-data documentation](https://docs.snort.org/rules/options/payload/pkt_data). The [traffic capture lab](../traffic-capture/README.md) uses the same harmless marker in real loopback traffic. That capture has different addresses and ports. This rule's fixed header will not match it unchanged.

These exercises were made for practice. They are not university work or live incident evidence. File checks and wrapper tests are separate from a real Snort run. Your practical work and explanation still need review. Until then, learner completion is unassessed.
