# Worked example: Alert deduplication and correlation

Try the guided case before reading this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

Six deliveries contain five unique alerts because a1 is delivered twice. a1, a2 and a3 are distinct failures at 00:00:00Z, 00:00:10Z and 00:00:20Z. a4 succeeds at 00:01:00Z, strictly after all three, and a5 is a process alert at 00:02:00Z. All share workstation.test/student and lie within 300 seconds of a1. The group workstation.test/student/1 therefore gets review-auth-sequence, which takes precedence over the mixed-signal rule. It is one review group, not evidence of one confirmed incident. Check whether the account holder retried a password or performed an authorised task.

The reference decision fields for guided are:

```json
{
  "workstation.test/student/1": "review-auth-sequence"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json` and compare observations, not only labels. Record one difference between your first prediction and the reference. If there was no difference, explain the rule that produced each decision rather than copying the label.

Handover prompt: explain what this evidence establishes, cite its exact IDs or lines, give a plausible alternative or remaining uncertainty, and name the smallest next check. Record any help used. A correct label by itself is not evidence of independent understanding.
