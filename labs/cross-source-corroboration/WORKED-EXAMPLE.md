# Worked example: Collection 01

Read this after you save your first prediction. It explains only the guided case.

Collection 01 source-01 reads 10:02:00Z and is 120 seconds ahead, giving 10:00:00Z. Source-02 reads 10:00:01Z with zero correction. Their one-second separation fits their combined two-second uncertainty; IDs and content hashes also agree.

## Walk through the evidence

- pair-01: corrected separation=1 seconds; combined uncertainty=2 seconds; sources=source-01,source-02.

Check each number or pair of values in `fixtures/guided.json`. The output label is not proof on its own. The fields and records must support it.

## Guided decision fields

- `pair-01`: `link-supported-within-clock-bounds`.

Explain how the values you found support these choices. Then add a limit: A shared ID and compatible time interval support a link within this fictional model; IDs and logs can be reused, copied or wrong.

## Connect it to the operation

Write your prediction before you run the guided task. Then open the saved task folder and follow these steps. Read output/timeline.csv. Keep observed_utc and corrected_utc side by side. A positive clock error means the source clock was ahead, so subtract it. A blank correction means unknown, not zero. Check collection notes when discussing reliability. Compare the source-before and source-after SHA-256 values in its receipt. These values come from the task you ran. The worksheet uses a made-up example. Keep any differences. Do not change the evidence to make it agree.

## Handover prompt

“I checked these item IDs and saved these files. These values support my choice. This evidence cannot show ____. To check that, I would need ____. I have done the guided stage. My ability to explain a new case still needs review.”
