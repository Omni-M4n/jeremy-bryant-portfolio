# Practice progression: Review MFA and recovery controls by account type

Use the exact prepare/show/check commands in [README.md](README.md). Save a
prediction before running `analyse`. Fresh folders preserve earlier attempts.

1. **Guided (10 minutes):** inspect each guided account type, predict missing
   labels in policy order, and explain enrolment separately from enforcement.
2. **With prompts (5 minutes):** Does recovery create a weaker access route?
   Who owns the workload? Does its password remain usable? Which emergency
   controls does a dated exception leave mandatory?
3. **Independent (10 minutes):** use `challenge`. Explain why the current
   emergency exception cannot excuse missing monitoring/storage, and why a
   workload with both federation and a password still has a credential finding.
4. **Changed evidence (5 minutes):** use `changed`. Compare the review date to
   exception expiry and 91-day test age. In a copied case, set test age to 90;
   predict exactly which label disappears and which ones remain.
5. **Teach back (5 minutes):** explain why "MFA enrolled" is incomplete evidence
   and why "service account" does not answer the security question.
6. **Later recall (next day, 5 minutes):** list the four service controls and
   five emergency controls without the reference. Describe the expiry boundary.

For each pass record: evidence references, decision, reason, uncertainty, help
used and one next check. Have another person review the explanation and one
unfamiliar case if possible. Until that occurs, independent completion is
unassessed even if every decision matches. Keep all attempts below `run/`.
