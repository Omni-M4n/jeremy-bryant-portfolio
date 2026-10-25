# Worked example: put event times in order

Try guided before reading this page. To make a fresh copy, use `python lab.py prepare --scenario guided --out run/worked-01`.

## Correct the times

1. e1 shows 2026-01-15T10:00:00+10:00. Subtract ten hours to get 00:00:00Z on 15 January.
2. Its clock is 30 seconds fast. Subtract those seconds. The centre is now 2026-01-14T23:59:30Z, on the previous day.
3. Its uncertainty is five seconds in either direction. The range runs from 23:59:25Z to 23:59:35Z.
4. e2 has a corrected centre of 23:59:45Z. Three seconds in either direction gives 23:59:42Z to 23:59:48Z.
5. e3 has a corrected centre of 00:00:20Z on 15 January. Two seconds in either direction gives 00:00:18Z to 00:00:22Z.

## Compare the bounds

e1's upper bound is 23:59:35Z. e2's lower bound is 23:59:42Z. They have a seven-second gap. That gives definitely-before for e1-vs-e2.

e2's upper bound is also below e3's lower bound. That gives definitely-before for e2-vs-e3. Neither result proves that the earlier event caused the later one.

The guided decisions are:

```json
{
  "e1-vs-e2": "definitely-before",
  "e2-vs-e3": "definitely-before"
}
```

Run `python lab.py analyse --case run/worked-01/case.json` after your own answer is saved. Compare the times and bounds, not just the labels. Keep the first answer and add any correction. If you were right, explain how the evidence led to that result.

For a handover, cite the event IDs and bounds. Give the conclusion, one remaining doubt and the smallest next check. Include help used. A correct label alone does not show that you can explain it.
