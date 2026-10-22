# Worked example: Backup scope, freshness and synthetic restore verification

Try the guided case before reading this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

Before checking the decisions below, run `python inspect_payloads.py --case run/worked-01/case.json`. Compare each measured SHA-256 with the same filename in the case's required_sha256 manifest, and record the measured length and bytes. This command reveals the measurements without revealing a decision; use them with the capture and retention timestamps to make your prediction.

Recovery time is 2026-02-01T12:00:00Z and the RPO is four hours (14,400 seconds). b1 was captured at 10:00Z: age 7,200 seconds. It remains retained, includes notes.txt and roster.csv, and both decoded payload digests match the manifest. b1 is qualified-synthetic-copy. b0 was captured the previous day at 10:00Z: age 93,600 seconds, so its matching bytes do not rescue its RPO failure. recovery selects b1. The test reconstructed only the embedded fictional bytes in memory. It did not restore an application, a disk backup or real user data.

The reference decision fields for guided are:

```json
{
  "b1": "qualified-synthetic-copy",
  "b0": "rpo-exceeded",
  "recovery": "select:b1"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json` and compare observations, not only labels. Record one difference between your first prediction and the reference. If there was no difference, explain the rule that produced each decision rather than copying the label.

Handover prompt: explain what this evidence establishes, cite its exact IDs or lines, give a plausible alternative or remaining uncertainty, and name the smallest next check. Record any help used. A correct label by itself is not evidence of independent understanding.
