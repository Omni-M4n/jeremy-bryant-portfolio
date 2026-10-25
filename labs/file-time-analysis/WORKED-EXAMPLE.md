# Worked example: Collection 01

Read this after you save your first prediction. It explains only the guided case.

The supplied Collection 01 hashes match and the modified times are equal. copy2 attempts to preserve supported timestamps; it does not preserve every kind of metadata.

## Walk through the evidence

- item-01: hash equal=True; modified-time difference=0 ns.

Check each number or pair of values in `fixtures/guided.json`. The output label is not proof on its own. The fields and records must support it.

## Guided decision fields

- `item-01`: `content-equal-time-equal`.

Explain how the values you found support these choices. Then add a limit: File timestamps can be copied or set explicitly; they do not identify a person or prove an action occurred at that exact time.

## Connect it to the operation

Write your prediction before you run the guided task. Then open the saved task folder and follow these steps. Read output/snapshots.json. Compare SHA-256 first, then mtime_ns. Note that atime was collected before hashing. Record whether birthtime_ns is available. Do not call ctime a creation time on all platforms. Compare the source-before and source-after SHA-256 values in its receipt. These values come from the task you ran. The worksheet uses a made-up example. Keep any differences. Do not change the evidence to make it agree.

## Handover prompt

“I checked these item IDs and saved these files. These values support my choice. This evidence cannot show ____. To check that, I would need ____. I have done the guided stage. My ability to explain a new case still needs review.”
