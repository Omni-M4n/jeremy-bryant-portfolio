# Worked example: Alert deduplication and correlation

Try the guided case before you read this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

Six deliveries contain five unique alerts because a1 is delivered twice. a1, a2 and a3 are separate failures. Their times are 00:00:00Z, 00:00:10Z and 00:00:20Z. a4 succeeds at 00:01:00Z, strictly after all three. a5 is a process alert at 00:02:00Z. All share workstation.test/student. All lie within 300 seconds of a1.

The group workstation.test/student/1 gets review-auth-sequence. This rule takes priority over the mixed-signal rule. It is one group to review. It does not prove that one incident took place. Check if the account holder retried a password or did an approved task.

The set decision fields for guided are:

```json
{
  "workstation.test/student/1": "review-auth-sequence"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json`. Compare what you found as well as the labels. Record one change from your first choice. If all choices matched, explain the rule behind each one in your own words.

In your handover, state what the evidence shows. Cite the exact IDs or lines. Give another possible cause or say what is still unknown. Name the smallest next check. Record any help used. A correct label alone does not show that you understood the rule.
