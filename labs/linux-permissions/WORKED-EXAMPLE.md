# Worked example: Linux mode bits and directory traversal

Try the guided case before reading this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

learner belongs to students. / is 755, so other search is allowed. /srv is owned by custodian with group students and mode 750: learner uses group 5, which includes search. /srv/notes.txt is 640 with group students: learner uses group 4, allowing read but not write. /srv/drop is 733 with group staff: learner uses other 3. This permits search and creating an entry, but not listing names (read=4 is absent). The file result depends on both the selected target class and every ancestor search check.

The reference decision fields for guided are:

```json
{
  "read-notes": "allowed-by-mode",
  "write-notes": "denied-by-mode",
  "list-drop": "denied-by-mode",
  "search-drop": "allowed-by-mode",
  "create-drop": "allowed-by-mode"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json` and compare observations, not only labels. Record one difference between your first prediction and the reference. If there was no difference, explain the rule that produced each decision rather than copying the label.

Handover prompt: explain what this evidence establishes, cite its exact IDs or lines, give a plausible alternative or remaining uncertainty, and name the smallest next check. Record any help used. A correct label by itself is not evidence of independent understanding.
