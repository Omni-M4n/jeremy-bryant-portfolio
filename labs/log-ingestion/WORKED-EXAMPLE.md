# Worked example: record set A

Read this after saving your first attempt.

Row 1 is e01 at 10:00 with +10:00. Subtract 10 hours: 00:00 UTC.
Row 2 has the same ID and the same normalised content, so it is a repeat.
Row 3 is e02 and is imported. Row 4 has no offset, so its time is ambiguous.
Keep it in the rejection report. The expected balance is **4 = 2 + 1 + 1**.

The database should contain e01 at 00:00 and e02 at 00:01, both on 15 January.
This hand calculation is the reference. A two-row database alone is not enough:
check which two rows it holds. Save the field map and one source-to-database pair.

Write the evidence separately from your interpretation. State one thing these
records cannot establish. Keep the first answer and the corrected answer.
