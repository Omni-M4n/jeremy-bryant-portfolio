# Test a small Snort rule

Predict, run and explain a Snort 3 rule against four harmless offline packet
fixtures. Then change one content option and retest. The work is rule editing,
tool operation and evidence review; no programming is required.

Allow 40-60 minutes. Python 3.10+ generates the files using only its standard
library. Actual detection requires an **already installed Snort 3** executable
with the `alert_json` logger. Snort 2 is not compatible with this exercise.
Use an existing Linux lab environment if that is where Snort 3 is available.
Windows users can prepare and inspect the fixtures locally; they should record
Snort execution as pending until they have an appropriate existing environment.
No installation, network interface capture, elevated command, public target or
VM configuration change is part of the lab.

## What the files represent

`fixtures/cases.json` specifies four original fictional requests. Each generated
PCAP contains nine Ethernet/IPv4/TCP packets: a handshake, one HTTP request,
acknowledgement and connection close. There is no HTTP response. Frame 4 carries
the only payload. The fixture client is `192.0.2.10:45000`; its fictional server
is `198.51.100.20`. `orchard.test` is a fictional HTTP Host value. Addresses are
documentation addresses, and no packets are transmitted by the generator.

The Ethernet addresses and timestamps are fixed teaching values. These PCAPs
are **synthetic**, never recordings of a real session. `PROVENANCE.json` records
source and generated-file SHA-256 values. Hashes establish file identity and
reproducibility, not authenticity of a capture or learner understanding.

| Fixture | Marker in frame 4 | Destination port | Original rule prediction |
| --- | --- | --- | --- |
| positive | `ORCHARD-CANARY-42` | 18080 | one SID 1000001 alert |
| near-miss | `orchard-canary-42` | 18080 | zero |
| negative | `ORDINARY-BOOKING-42` | 18080 | zero |
| wrong-port | `ORCHARD-CANARY-42` | 18081 | zero |

Predictions are manually specified in `reference/expected.json`, independent of
the packet writer. They are not saved Snort results. The negative controls help
test whether the experiment detects the intended condition; zero alerts alone
never establishes that an input is safe or that an engine ran correctly.

## Maintained commands

Open a terminal in this folder. Use `python3` instead of `python` where required.

```text
python lab.py --help
python lab.py verify
python lab.py prepare --out run/guided-01
python lab.py run-snort --attempt run/guided-01 --out run/snort-01
```

`verify` checks the shipped hashes, deterministic PCAP bytes and packet
structure/checksums. It **does not run Snort**. `prepare` writes the PCAPs, a rule
copy, provenance and worksheet. The worksheet is where you record your own
prediction before running the engine.

`run-snort` looks for `snort` or `snort3` on PATH. To name an existing executable:

```text
python lab.py run-snort --attempt run/guided-01 --out run/snort-02 --snort /usr/local/bin/snort
```

Use your actual installed path; this is a path example, not an installation
instruction. A Windows path containing spaces must be quoted. If the engine is
absent, `result.json` says `unverified`, and the command returns 2. Do not replace
that result with a predicted alert count.

For each fixture the wrapper executes the equivalent of this command with
absolute paths and a fresh per-case log folder:

```text
snort -q -R local.rules -r input.pcap -A alert_json -l CASE_OUTPUT --lua "search_engine = { detect_raw_tcp = true }"
```

This is an explanation of the recorded command; use `run-snort` to prepare safe
output paths. `-r` reads a PCAP, `-R` loads the local rule, and `-A` selects JSON
alerts. The wrapper retains the engine version, exact command, rule hash, input
hashes, stdout, stderr, exit codes and parsed alerts. An engine error or timeout
is not counted as zero alerts. Check the per-case evidence in the output folder
even when the expected counts match. The official
[rule loading guide](https://docs.snort.org/start/rules) and
[alert logging guide](https://docs.snort.org/start/alert_logging) document these
options and the logger's output.

All CLI output is confined to fresh direct children `run/NAME`; existing output,
links and traversal paths are refused. Input PCAPs must exactly match the
prepared fixtures. Rule edits are limited to this one-line lab rule: its
content text, optional `,nocase`, destination port 18080/18081, message and
revision. Includes, scripts and arbitrary rule actions are refused. Edit only
the copy in your run folder. Exit codes: `0` means the requested operation
completed and, for `run-snort`, expected counts were observed; `1` means a
count difference, per-case engine error, timeout or unreadable alert output
needs review; `2` means invalid input, an unavailable engine or a failure to
start or prepare the operation. Read the saved per-case status and command
output before interpreting any result.
No code awards mastery.

## Read the rule, then change it

The shipped rule alerts on TCP from `192.0.2.10` to `198.51.100.20:18080` when
the raw data includes `ORCHARD-CANARY-42`. The marker is harmless. The header's
address, direction and port conditions must also match. SID `1000001` identifies
this rule and `rev` tracks revisions. See the official
[rule structure guide](https://docs.snort.org/rules/headers/),
[content guide](https://docs.snort.org/rules/options/payload/content) and
[raw-data option](https://docs.snort.org/rules/options/payload/raw_data).

For a changed experiment, first prepare `run/changed-01`. Open that folder's
`local.rules` in a text editor and change only:

```text
content:"ORCHARD-CANARY-42";
```

to:

```text
content:"ORCHARD-CANARY-42",nocase;
```

Also change `rev:1;` to `rev:2;`. Predict the affected control, then run:

```text
python lab.py run-snort --attempt run/changed-01 --out run/snort-changed-01 --expect case-insensitive
```

The near-miss should now alert; the wrong-port and negative cases should still
not alert. Record actual counts and evidence. The
[nocase option](https://docs.snort.org/rules/options/payload/nocase) changes
letter-case matching, not addresses or ports.

**Vocabulary:** a rule header selects traffic; content is a byte pattern;
SID identifies a rule; revision labels a rule version; a positive control is
intended to trigger; a negative control is intended not to trigger; PCAP is a
packet-file format; an alert is a matched condition, not proof of an attack.

Deliver your worksheet, rule copy and actual engine output, or clearly mark
engine execution pending. Continue with [drills](DRILLS.md) and use the
[worked example](WORKED-EXAMPLE.md) after your prediction. Handover prompt:
**What changed after nocase, which control stayed quiet, and what evidence
shows that Snort actually processed the files?**

This narrow raw-byte rule does not establish malicious intent, TLS visibility,
robust HTTP parsing, performance or production detection quality. It does not
teach stream-spanning content matching. Its raw-data choice and explicit raw
TCP detection setting keep this single-packet marker experiment inspectable;
Snort distinguishes raw data from normalised inspection buffers in its
[packet-data documentation](https://docs.snort.org/rules/options/payload/pkt_data).
The [traffic capture lab](../traffic-capture/README.md) uses the same harmless
marker in real loopback traffic. Its actual capture has different addresses
and ports, so these fixture-specific rule headers will not match it unchanged.

The source materials are original exercises, not university work or incident
evidence. Source/packet checks and wrapper tests are distinct from real Snort
execution. Learner completion remains unassessed until the practical work and
explanation have been reviewed.
