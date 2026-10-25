# Worked example: record set A

Read this after saving your first attempt.

Interval a has a known empty source list and no deliveries: 0 expected, 0
received. Its coverage is complete-at-cutoff. Delivery is no-deliveries; the
heartbeat is present. Say "zero listed source events in a", not "nothing happened".

Interval b expects e1 and e2. Only e1 arrived. e1 took 30 seconds, within the 60
second budget. e2 is missing at 00:05. The heartbeat is absent. The answers are
gap-at-cutoff, within-budget, absent. The quick arrival of e1 cannot explain away
the missing e2. Request the source export and collector queue or health record.

Write the evidence separately from your interpretation. State one thing these
records cannot establish. Keep the first answer and the corrected answer.
