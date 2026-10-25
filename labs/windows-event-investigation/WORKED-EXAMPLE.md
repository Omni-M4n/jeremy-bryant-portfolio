# Worked example: matching evidence, not filenames

Read this after saving your first prediction. These are synthetic XML records.
No Windows capture was used to produce this answer.

## Follow the GUIDs

All four records name `LAB-VM.test`. In the table, `...1101` means the full GUID
`{11111111-1111-1111-1111-111111111101}`; use full GUIDs in your own notes.

| Record | UtcTime on 20 October 2026 | Image ending | PID | Process GUID ending | Parent GUID ending | Linked parent record |
| --- | --- | --- | --- | --- | --- | --- |
| 101 | 09:00:00.000 UTC | powershell.exe | 1000 | ...1101 | ...1100 | Absent |
| 102 | 09:00:01.000 UTC | cmd.exe | 2000 | ...1102 | ...1101 | 101 |
| 103 | 09:00:01.500 UTC | powershell.exe | 3000 | ...1103 | ...1102 | 102 |
| 104 | 09:00:01.600 UTC | powershell.exe | 4000 | ...1104 | ...1190 | Absent |

Record 102's parent GUID equals record 101's process GUID. Record 103's parent
GUID equals record 102's process GUID. The recorded chain is therefore
**101 -> 102 -> 103**. This is a relationship among process instances on the
same recorded computer, not a grouping by executable name.

The gap from 101 to 102 is 1 second; from 102 to 103 it is 0.5 seconds. Record
103's `SystemTime` is `09:00:01.5200000Z`, 20 ms after its `UtcTime`. Preserve
both values. That difference alone does not diagnose clock drift or establish
an exact logging delay.

Record 104 has the same image and command text as 103 and occurs 0.1 seconds
later. Its parent GUID ends in `1190`, not `1102`, so it does not attach to the
displayed chain. The export does not contain its parent creation. It also does
not contain 101's parent creation; the child supplies parent attributes, but
that is different from possessing the parent's own creation record.

## Changed case: a reused PID

In `changed.xml`, records 201 and 202 both have PID 2000. Their GUIDs differ.
Record 203 names the full GUID ending `2202` as its parent. Its parent is record
202, not the older record 201. The inspector lists 201 as a PID-only alternative
to help you notice the trap. These Event 1 records do not supply the earlier
process's termination time, so do not invent it.

## Challenge: a gap that PID cannot repair

In `challenge.xml`, the file stores record 302 before 301. The UTC timeline
correctly displays 301 before 302. The latter's parent GUID ends `3399`, which
is absent. Record 301 has the matching parent PID 2000 but GUID ending `3301`.
It cannot be substituted as the parent. The correct label for 302 is
`parent-not-in-export`; the next check is a wider time window and collection
configuration, not a malware verdict.

## Example handover

"I inspected the synthetic guided export. Records 101, 102 and 103 form a
recorded PowerShell -> cmd -> PowerShell chain, supported by their full parent
and process GUID matches on LAB-VM.test. Record 104 shares the marker and
executable with 103 but has a different parent GUID. The export lacks the
creation records for the parents of 101 and 104. I would obtain earlier records
and configuration context before extending either branch. Event 1 alone does
not establish whether the marker printed. I used the worked example; this is
practice, not an independently assessed real capture."

Add the actual SHA-256 from your receipt. Do not copy a claimed VM observation
into this synthetic note, or replace missing evidence with the expected story.
