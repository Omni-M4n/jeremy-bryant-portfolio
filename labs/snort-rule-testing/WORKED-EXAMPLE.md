# Worked reasoning: marker rule

These are predictions from the fixture specification and rule text, not a
transcript of an executed Snort session. Your actual evidence belongs in a
fresh run folder.

The original rule requires both a matching header and an exact byte pattern.
For `positive.pcap`, frame 4 is from `192.0.2.10:45000` to
`198.51.100.20:18080`. Its HTTP request contains the uppercase marker. Predict
one SID 1000001 alert. Inspect the engine's alert object and recorded packet
number rather than treating the prediction as observed evidence.

`near-miss.pcap` has the same endpoints and port but a lowercase marker.
Without `nocase`, the marker does not meet the content condition. Predict zero.
The controls were deliberately specified before engine execution; the writer
does not read the rule and invent an expected result from it.

`negative.pcap` carries `ORDINARY-BOOKING-42`. The text is harmless and different
from the rule's content. Predict zero. `wrong-port.pcap` carries the exact
uppercase marker but sends it to port 18081, outside the header's condition.
Predict zero there too. Searching only for the marker string would miss this
important distinction.

After adding `,nocase` and increasing the revision, only the near-miss's
prediction changes from zero to one. The address/port requirements are
unchanged. If the wrong-port fixture alerts, inspect the exact rule copy and
command before explaining the result away. If all four cases show zero, check
the positive control, engine exit codes, stderr and rule identity. An engine
that failed to run has supplied no detection evidence.

The wrapper stores `version.txt`, the final rule, `result.json` and per-case
`command.json`, `stdout.txt`, `stderr.txt` and `input.pcap`. The command uses
offline PCAP input; it does not open a capture interface. Matching expected
counts is useful evidence about this exact experiment, not evidence that the
rule can detect arbitrary attacks.

A useful finding is: "With rule revision ___ and Snort version ___, the
positive control produced ___ SID 1000001 alerts; the near-miss produced ___.
After the nocase edit, ___ changed. The raw output in ___ supports this. The
wrong-port control remained ___ because ___. These are harmless test markers."

If Snort is absent, the accurate finding is: "I generated and structurally
checked the synthetic fixtures and predicted the rule outcomes. Snort execution
is pending." Do not complete the blanks with expected counts as if observed.
