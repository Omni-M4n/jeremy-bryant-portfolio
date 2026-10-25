# Worked example: matching evidence, not filenames

Read this after saving your first prediction. These XML records were made up. No Windows capture was used to produce this answer.

## Follow the GUIDs

All four records name `LAB-VM.test`. In this table, `...1101` stands for the full GUID `{11111111-1111-1111-1111-111111111101}`. Use full GUIDs in your own notes.

| Record | UtcTime on 20 October 2026 | Image ending | PID | Process GUID ending | Parent GUID ending | Linked parent record |
| --- | --- | --- | --- | --- | --- | --- |
| 101 | 09:00:00.000 UTC | powershell.exe | 1000 | ...1101 | ...1100 | Absent |
| 102 | 09:00:01.000 UTC | cmd.exe | 2000 | ...1102 | ...1101 | 101 |
| 103 | 09:00:01.500 UTC | powershell.exe | 3000 | ...1103 | ...1102 | 102 |
| 104 | 09:00:01.600 UTC | powershell.exe | 4000 | ...1104 | ...1190 | Absent |

Record 102's parent GUID matches record 101's process GUID. Record 103's parent GUID matches record 102's process GUID. The recorded chain is **101 -> 102 -> 103**. These are links between process instances on the same recorded computer. A shared program name would not prove a link.

The gap from 101 to 102 is 1 second. From 102 to 103, it is 0.5 seconds. Record 103's `SystemTime` is `09:00:01.5200000Z`. That is 20 ms after its `UtcTime`. Keep both values. This gap alone cannot prove clock drift or an exact logging delay.

Record 104 has the same image and command text as 103. It occurs 0.1 seconds later. But its parent GUID ends in `1190`, not `1102`. It does not join this chain. The export lacks its parent's creation record. It also lacks 101's parent creation. The child reports some facts about its parent. That is different from having the parent's own creation record.

## Try the other cases yourself

Keep the changed and challenge answers closed while you work. Make a new worksheet for each case. Check time order and full GUIDs on the same computer. Save each link, its source and any gap before you inspect the file. This worked answer covers only guided.

## Example handover

"I inspected the made-up guided export. Records 101, 102 and 103 form a recorded PowerShell -> cmd -> PowerShell chain. Their full parent and process GUIDs match on LAB-VM.test. Record 104 shares 103's marker and program, but has a different parent GUID. The export lacks creation records for the parents of 101 and 104. I would ask for earlier records and logging settings before extending either branch. Event 1 alone does not show whether the marker printed. I used the worked example. This is practice, not an assessed real capture."

Add the real SHA-256 from your receipt. Do not add a claimed VM result to this made-up case. Do not fill a gap with the story you expected to see.
