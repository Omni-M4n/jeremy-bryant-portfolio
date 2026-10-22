# Worked example: Endpoint process context triage

Try the guided case before reading this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

Start at p1, the desktop root, then trace p1 -> p2 -> p3. p2 is a document process and p3 is a shell. p3 therefore deserves context review even though its signature is verified and it runs from system. p4 is an unsigned utility in user-temp, a separate trigger. p1 and p2 have no modelled triggers; that is not a clean bill of health. The inert command text gives a collection lead, not something to run. Ask whether a helpdesk demonstration or approved macro explains p3, and request the executable hash and collection context for p4.

The reference decision fields for guided are:

```json
{
  "p1": "no-modelled-triage-trigger",
  "p2": "no-modelled-triage-trigger",
  "p3": "prioritise-context-review",
  "p4": "prioritise-context-review"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json` and compare observations, not only labels. Record one difference between your first prediction and the reference. If there was no difference, explain the rule that produced each decision rather than copying the label.

Handover prompt: explain what this evidence establishes, cite its exact IDs or lines, give a plausible alternative or remaining uncertainty, and name the smallest next check. Record any help used. A correct label by itself is not evidence of independent understanding.
