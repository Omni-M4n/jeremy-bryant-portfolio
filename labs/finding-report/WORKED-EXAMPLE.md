# Guided worked example

Read this after saving your first attempt. This is a fictional example, not a
claim that a learner or an author ran a real engagement.

For guided item-1, line 1 shows another account's toy record in the original
response. Line 3 retests the same route. It reports 403 with no other record.
Line 4 reports 200 for the owner. Use `bounded-correction-supported` for this
route and these supplied facts only.

A report could say: In the authored transcript, account-a could read
account-b's toy record before the change. After the change, that request was
refused. The owner's retest returned 200. This does not prove that the whole
app is secure.

No date, environment or account setup is supplied. Mark these **not supplied**.
The lines show requests and results. Any added setup or repeat steps must be
labelled **proposed — not run**. Keep the origin as supplied training evidence.
It is not proof that you used Burp or ran a local test.

This example completes only the fictional preparation. The README's required
Stage 2 needs your own completed local attempt and a separate report.
Leave that stage unrun until you have its evidence. Do not fill its dates,
steps, owner retest or review results from this example.

Expected guided decision strings:

```json
{
  "item-1": "bounded-correction-supported"
}
```

Keep the first attempt. Write corrections in a separate file, explaining which
fact changed your answer. A useful explanation names the evidence and its limit.
