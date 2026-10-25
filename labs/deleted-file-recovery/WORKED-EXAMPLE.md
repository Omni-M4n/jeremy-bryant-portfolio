# Worked example: Collection 01

Read this after you save your first prediction. It explains only the guided case.

Collection 01 declares 42 bytes and the candidate contains those same 42 bytes. Its hash matches the known training file. This establishes this file comparison, not complete recovery of an arbitrary disk.

## Walk through the evidence

- item-01: directory present=True; declared bytes=42; candidate bytes=42; cluster allocated=False.

Check each number or pair of values in `fixtures/guided.json`. The output label is not proof on its own. The fields and records must support it.

## Guided decision fields

- `item-01`: `matches-known-training-file`.

Explain how the values you found support these choices. Then add a limit: This parser accepts only the generated 32 KiB FAT12 layout and one-cluster deleted entries. It is not a general recovery tool.

## Connect it to the operation

Write your prediction before you run the guided task. Then open the saved task folder and follow these steps. Read output/recovery-log.json. The generated layout has 512-byte sectors, two one-sector FAT copies, a root directory at byte 1536, and data at byte 2048. A first directory byte e5 marks the deleted entry. Compare the separately extracted item-01.bin with the known training hash. Compare the source-before and source-after SHA-256 values in its receipt. These values come from the task you ran. The worksheet uses a made-up example. Keep any differences. Do not change the evidence to make it agree.

## Handover prompt

“I checked these item IDs and saved these files. These values support my choice. This evidence cannot show ____. To check that, I would need ____. I have done the guided stage. My ability to explain a new case still needs review.”
