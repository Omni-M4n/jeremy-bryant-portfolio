# Worked example: Scheduled task change review

Try the guided case before reading this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

archive was approved for 02:00, lab-backup and C:/Lab/bin/archive.exe. Its observed 03:00 time exactly matches the maintenance approval, so the difference is explained by that note. inventory changes from 04:00/lab-inventory/C:/Lab/bin/inventory.exe to 04:00/SYSTEM/C:/Lab/temp/inventory.exe without an approval. Both account and path differ, so it needs review. A benign repair could explain the change, but that explanation must be checked; the snapshot alone does not establish persistence or malicious intent.

The reference decision fields for guided are:

```json
{
  "archive": "approved-maintenance-difference",
  "inventory": "unapproved-change-review"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json` and compare observations, not only labels. Record one difference between your first prediction and the reference. If there was no difference, explain the rule that produced each decision rather than copying the label.

Handover prompt: explain what this evidence establishes, cite its exact IDs or lines, give a plausible alternative or remaining uncertainty, and name the smallest next check. Record any help used. A correct label by itself is not evidence of independent understanding.
