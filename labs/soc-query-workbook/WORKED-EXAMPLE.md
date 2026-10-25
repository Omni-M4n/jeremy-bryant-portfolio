# Worked example: record set A

Read this after saving your first attempt.

l1 and l2 are failures. l3 is a success and is filtered out. Each failure pairs
with p1 and p2. The four pairs are l1/p1, l1/p2, l2/p1, l2/p2. COUNT(*) is **4**.
Only l1 and l2 occur in the left side of those pairs. COUNT(DISTINCT l.id) is **2**.
The raw failure count is **2**. w2 has status 404, so the web count is **1**.

The extra by-account query gives one row: reader, 2. Both failure records belong
to reader. Compare this table only after saving your own hand count.

Write failures="2", joined="4", linked="2", web="1". Four joined rows are not
four alerts or four incidents. The query's question must state its counting unit.
The authoring check ran database creation and all four queries locally.

Write the evidence separately from your interpretation. State one thing these
records cannot establish. Keep the first answer and the corrected answer.
