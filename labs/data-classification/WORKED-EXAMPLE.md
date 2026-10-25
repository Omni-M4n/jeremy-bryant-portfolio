# Guided worked example

Read this after saving your first attempt. This is a fictional example, not a
claim that a learner or an author ran a real engagement.

Item-1 holds made-up personal contact data. Use `confidential`. Keep booking
and email. Leave birthday out of future forms; this task does not need it.
Day 12 is before the day-30 review. Only `booking-team` may receive the data.
A folder limited to that team is a possible storage rule.

Item-2 holds approved opening times with no sensitive fields. Use `public`.
The notice could go on a public page. This exercise publishes neither item.
The receipt lacks a real disposal date, method and authorising role.
Mark these **not supplied**. Do not invent a deletion record.

Expected guided decision strings:

```json
{
  "item-1": "confidential;retain-until-review;share-as-approved;no-receipt",
  "item-2": "public;retain-until-review;share-as-approved;no-receipt"
}
```

Keep the first attempt. Write corrections in a separate file, explaining which
fact changed your answer. A useful explanation names the evidence and its limit.
