# Worked example: Scheduled task change review

Try the guided case before you read this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

archive had a baseline time of 02:00, account lab-backup and action C:/Lab/bin/archive.exe. Its observed 03:00 time matches the maintenance approval exactly. The account and path also match that approval. This explains the difference.

inventory had time 04:00, account lab-inventory and action C:/Lab/bin/inventory.exe. The observed time is still 04:00. But the account is now SYSTEM and the action is C:/Lab/temp/inventory.exe. There is no approval. Both account and path differ, so it needs review. A harmless repair could explain the change, but you must check that idea. This snapshot alone does not prove an attempt to keep access or cause harm.

The set decision fields for guided are:

```json
{
  "archive": "approved-maintenance-difference",
  "inventory": "unapproved-change-review"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json`. Compare what you found as well as the labels. Record one change from your first choice. If all choices matched, explain the rule behind each one in your own words.

In your handover, state what the evidence shows. Cite the exact IDs or lines. Give another possible cause or say what is still unknown. Name the smallest next check. Record any help used. A correct label alone does not show that you understood the rule.
