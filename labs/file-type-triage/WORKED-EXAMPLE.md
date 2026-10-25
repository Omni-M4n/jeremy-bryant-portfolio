# Worked example: Collection 01

Read this after saving your first prediction. It explains only the guided collection.

Collection 01 has PNG starting bytes but a .dat ending. Report the mismatch and the limited check. There is no evidence here of malware.

## Walk through the evidence

- item-01: 16 prefix bytes inspected from 69 bytes; reported label=application/octet-stream.

Check each number or comparison directly in `fixtures/guided.json`. Do not treat the output label as evidence for itself. The observation fields and records must support the label.

## Guided decision fields

- `item-01`: `png-signature-extension-differs`.

Write a short explanation connecting the observed values to these decisions. Then add a limit: A matching signature is a format clue, not proof that the whole file is valid or safe.

## Connect it to the operation

Run the guided practical only after your prediction. Within the saved practical folder, use these steps. Read output/observations.json. Convert the first eight PNG bytes to 89 50 4e 47 0d 0a 1a 0a. For a database, compare all 16 signature bytes. Do not double-click unknown files. Compare the source-before and source-after SHA-256 values in its receipt. These are actual measurements; the worksheet is a supplied fictional snapshot. Save differences rather than adjusting evidence to make it agree.

## Handover prompt

“I examined these item IDs and saved these files. My decision is supported by these values. This evidence cannot show ____. To check that, I would need ____. My work is at the guided stage; independent explanation still needs review.”
