# Worked example: Collection 01

Read this after you save your first prediction. It explains only the guided case.

Collection 01 has a history record at 10:00:00Z, a completed 40/40-byte download at 10:00:08Z and cache at 10:00:10Z. URL/session agree; the eight- and ten-second gaps meet this exercise's rule.

## Walk through the evidence

- item-01: kind=history; earlier same-session URL records=none; bytes=0/0.
- item-02: kind=download; earlier same-session URL records=item-01; bytes=40/40.
- item-03: kind=cache; earlier same-session URL records=item-01; bytes=0/0.

Check each number or pair of values in `fixtures/guided.json`. The output label is not proof on its own. The fields and records must support it.

## Guided decision fields

- `item-01`: `history-record`.
- `item-02`: `download-complete-linked`.
- `item-03`: `cache-linked`.

Explain how the values you found support these choices. Then add a limit: This is a fictional SQLite schema with explicit UTC times, not a Chrome/Firefox profile parser. No real browser history is read.

## Connect it to the operation

Write your prediction before you run the guided task. Then open the saved task folder and follow these steps. Read output/timeline.json. Match URL and session before checking the time gap. The SQLite tables store explicit UTC text. A complete download record is not proof that the downloaded file still exists on disk. Compare the source-before and source-after SHA-256 values in its receipt. These values come from the task you ran. The worksheet uses a made-up example. Keep any differences. Do not change the evidence to make it agree.

## Handover prompt

“I checked these item IDs and saved these files. These values support my choice. This evidence cannot show ____. To check that, I would need ____. I have done the guided stage. My ability to explain a new case still needs review.”
