# Worked example: Endpoint process context triage

Try the guided case before you read this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

Start at p1, the desktop root. Trace p1 -> p2 -> p3. p2 is a document process and p3 is a shell. This gives p3 a context review trigger. Its verified signature and system location do not cancel that trigger. p4 is an unsigned utility in user-temp. This is a separate trigger. p1 and p2 have no triggers in this model. That does not prove that they are safe.

Use the command text as a lead for what to collect. Do not run it. Ask if a helpdesk demo or approved macro explains p3. For p4, ask for the program file hash and details of how the evidence was collected.

The set decision fields for guided are:

```json
{
  "p1": "no-modelled-triage-trigger",
  "p2": "no-modelled-triage-trigger",
  "p3": "prioritise-context-review",
  "p4": "prioritise-context-review"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json`. Compare what you found as well as the labels. Record one change from your first choice. If all choices matched, explain the rule behind each one in your own words.

In your handover, state what the evidence shows. Cite the exact IDs or lines. Give another possible cause or say what is still unknown. Name the smallest next check. Record any help used. A correct label alone does not show that you understood the rule.
