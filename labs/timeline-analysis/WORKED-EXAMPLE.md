# Worked example: Timeline normalisation and uncertainty

Try the guided case before reading this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

e1 at 2026-01-15T10:00:00+10:00 becomes 00:00:00Z. Its clock is 30 seconds fast, so the corrected centre is 2026-01-14T23:59:30Z; +/-5 seconds gives 23:59:25Z through 23:59:35Z. e2 centres on 23:59:45Z with +/-3 seconds, giving 23:59:42Z through 23:59:48Z. The seven-second gap between e1 upper and e2 lower supports definitely-before for e1-vs-e2. e3 centres on 00:00:20Z with +/-2 seconds, so e2-vs-e3 is also definitely-before. None of these comparisons says the earlier event caused the later event.

The reference decision fields for guided are:

```json
{
  "e1-vs-e2": "definitely-before",
  "e2-vs-e3": "definitely-before"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json` and compare observations, not only labels. Record one difference between your first prediction and the reference. If there was no difference, explain the rule that produced each decision rather than copying the label.

Handover prompt: explain what this evidence establishes, cite its exact IDs or lines, give a plausible alternative or remaining uncertainty, and name the smallest next check. Record any help used. A correct label by itself is not evidence of independent understanding.
