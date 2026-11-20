# Worked example: Collection 01

Read this after you save your first prediction. It explains only the guided case.

Collection 01 source-01 reads 10:02:00Z and is 120 seconds ahead, giving 10:00:00Z. Source-02 reads 10:00:01Z with zero correction. Their one-second separation fits their combined two-second uncertainty; IDs and content hashes also agree.

## Walk through the evidence

- pair-01: corrected separation=1 seconds; combined uncertainty=2 seconds; sources=source-01,source-02.

Check each number or pair of values in `fixtures/guided.json`. The output label is not proof on its own. The fields and records must support it.

## Guided decision fields

- `pair-01`: `link-supported-within-clock-bounds`.

I will explain how the values I found support these choices. I will retain these limits: I treat matching supplied request IDs and recorded object SHA-256 values, together with corrected uncertainty intervals that touch or overlap, as support only for a proposed link in this fictional model; identifiers and logs can be missing, reused, copied, incomplete or wrong. I treat clock errors, uncertainty values and collection notes as supplied training assertions, not live measurements or independently verified custody; I also record that the analyser neither acquires logs nor recomputes the recorded object hashes from underlying objects. I do not use timing compatibility to identify a person, establish causation or prove that either source is complete.

## Connect it to the operation

Write your prediction before you run the guided task. Then open the saved task folder and follow these steps. Read output/timeline.csv. Keep observed_utc and corrected_utc side by side. A positive clock error means the source clock was ahead, so subtract it. A blank correction means unknown, not zero. Check collection notes when discussing reliability. Compare the source-before and source-after SHA-256 values in its receipt. These values come from the task you ran. The worksheet uses a made-up example. Keep any differences. Do not change the evidence to make it agree.

## Handover prompt

“I checked these item IDs and saved these files. These values support my choice. This evidence cannot show ____. To check that, I would need ____. I have done the guided stage. My ability to explain a new case still needs review.”
