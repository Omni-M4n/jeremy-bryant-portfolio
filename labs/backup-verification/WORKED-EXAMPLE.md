# Worked example: check a backup

Try guided before reading this page. To make a fresh copy, use `python lab.py prepare --scenario guided --out run/worked-01`.

First run `python inspect_payloads.py --case run/worked-01/case.json`. Save the measured bytes, lengths and hashes. Compare each SHA-256 with the same filename in required_sha256. Use the capture and retention dates to predict the decisions. The inspector gives measurements, not answers.

## Check both copies

The recovery time is 2026-02-01T12:00:00Z. The RPO is four hours, or 14,400 seconds.

- b1 was captured at 10:00Z on the same day. Its age is two hours, or 7,200 seconds. Its retention period has not ended. It includes notes.txt and roster.csv. Both measured hashes match the expected hashes. The decision is qualified-synthetic-copy.
- b0 was captured at 10:00Z on the previous day. Its age is 26 hours, or 93,600 seconds. Its hashes match, but it is too old for this RPO. The decision is rpo-exceeded.

The recovery choice is b1. This check decoded dummy bytes in memory. It did not restore an app, a disk backup or real user data.

The guided decisions are:

```json
{
  "b1": "qualified-synthetic-copy",
  "b0": "rpo-exceeded",
  "recovery": "select:b1"
}
```

Run `python lab.py analyse --case run/worked-01/case.json` after saving your own answer. Compare the measured facts, not just the labels. Keep your first answer and add any correction. If it matched, explain how you reached it.

For a handover, state what these checks show. Cite exact IDs and measurements. Give one remaining doubt and the smallest next check. Include help used. A correct label alone does not show that you can explain it.
