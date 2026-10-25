# Worked example: Collection 01

Read this after you save your first prediction. It explains only the guided case.

Collection 01 has both expected six-byte files, and their hashes match. There are no extra names. The restore took 20 ms against a 100 ms target. The backup age is 10 minutes against a 30-minute limit. Each check supports a different part of the result.

## Walk through the evidence

- item-01: expected item-01.txt, 6 bytes; restored entry present=True.
- item-02: expected item-02.txt, 6 bytes; restored entry present=True.
- Unexpected names=none; restore=20/100 ms; backup age=10/30 minutes.

Check each number or pair of values in `fixtures/guided.json`. The output label is not proof on its own. The fields and records must support it.

## Guided decision fields

- `item-01`: `file-matches`.
- `item-02`: `file-matches`.
- `inventory`: `inventory-no-extras`.
- `recovery-time`: `within-time-target`.
- `recovery-point`: `within-data-age-target`.

Explain how the values you found support these choices. Then add a limit: A local byte-copy drill does not establish application startup, permissions, cloud availability, full-machine recovery or a disaster recovery time.

## Connect it to the operation

Write your prediction before you run the guided task. Then open the saved task folder and follow these steps. Read output/restore-log.json. Compare every baseline name, size and hash against restored. Compare current_after_change to explain which version was restored. Keep copy_elapsed_ns separate from verification_elapsed_ns. Nanoseconds are the counter unit, not a promise of precise disaster timing. Compare the source-before and source-after SHA-256 values in its receipt. These values come from the task you ran. The worksheet uses a made-up example. Keep any differences. Do not change the evidence to make it agree.

## Handover prompt

“I checked these item IDs and saved these files. These values support my choice. This evidence cannot show ____. To check that, I would need ____. I have done the guided stage. My ability to explain a new case still needs review.”
