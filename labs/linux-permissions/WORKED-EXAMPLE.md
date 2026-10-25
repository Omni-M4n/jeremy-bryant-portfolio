# Worked example: Linux mode bits and directory traversal

Try the guided case before you read this page. Use `python lab.py prepare --scenario guided --out run/worked-01` for a fresh ignored copy.

The actor learner belongs to students. The root folder / has mode 755. Learner uses other bits there, which allow search.

The folder /srv is owned by custodian. Its group is students and its mode is 750. Learner uses group 5, which includes search.

The file /srv/notes.txt has mode 640 and group students. Learner uses group 4. This allows read but not write.

The folder /srv/drop has mode 733 and group staff. Learner uses other 3. This allows search and creating an entry. It does not allow listing names because read bit 4 is absent.

A file result depends on two checks. The target's chosen class must allow the action. Every ancestor folder must also allow search.

The guided case has these reference decisions:

```json
{
  "read-notes": "allowed-by-mode",
  "write-notes": "denied-by-mode",
  "list-drop": "denied-by-mode",
  "search-drop": "allowed-by-mode",
  "create-drop": "allowed-by-mode"
}
```

Now run `python lab.py analyse --case run/worked-01/case.json`. Compare the evidence and your reasons, as well as the labels. Record one difference between your first prediction and the answer. If they match, explain how each rule led to your choice. Do not just copy the label.

In your handover, explain what the evidence proves. Cite its exact IDs or lines. Give another possible explanation or state what is still unclear. Name the smallest next check. Record any help used. A correct label alone does not show that you understood the case on your own.
