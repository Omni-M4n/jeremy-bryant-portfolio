# Practice progression: Triage a fictional software inventory and advisory ranges

Use the exact prepare/show/check commands in [README.md](README.md). Save a
prediction before running `analyse`. Fresh folders preserve earlier attempts.

1. **Guided (10 minutes):** turn each installed and boundary version into a
   numeric triple. Show both comparisons before assigning a decision.
2. **With prompts (5 minutes):** Is the package name an exact match? Is the
   introduced boundary included? Is this runtime or build exposure? What does
   the reachability evidence actually demonstrate?
3. **Independent (10 minutes):** use `challenge`. Explain why 1.10.1 is affected
   by a separate later advisory although it exceeds DEMO-ADV-001's fixed version.
   Compare runtime unknown reachability with a reachable development dependency.
4. **Changed evidence (5 minutes):** use `changed`. Explain 1.9.0 and 1.10.0 at
   opposite boundaries. In a copy change report-parser reachability to `unknown`
   with evidence `no path review performed`; predict the changed decision.
5. **Teach back (5 minutes):** explain range match, reachability and exploitability
   separately. Why is a development-only dependency still worth reviewing?
6. **Later recall (next day, 5 minutes):** order 1.9.9, 1.10.0 and 1.10.1 without
   string sorting. Explain why no supplied advisory does not prove security.

For each pass record: evidence references, decision, reason, uncertainty, help
used and one next check. Have another person review the explanation and one
unfamiliar case if possible. Until that occurs, independent completion is
unassessed even if every decision matches. Keep all attempts below `run/`.
