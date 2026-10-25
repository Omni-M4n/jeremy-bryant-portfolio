# Worked example: Library object requests

Open this after your guided prediction. In `q1`, reading `poster.txt`
matches `s1`. The start of the staff path in `s2` does not match.
The result is `allow`.

For `q2`, both `s1` and `s2` match the read of `staff/rota.txt`.
A matching deny wins, so use `explicit-deny`. This does not work like a
firewall list that stops at its first match.

For `q3`, neither statement covers PutObject. Use `implicit-deny`.
The file name alone is not enough. The action matters too.

You could write: "q2 matches s1 and s2 on both action and object.
s2 has effect Deny, so the model refuses q2."
Three answer words alone do not explain how you decided.

The reference files contain decisions worked out by hand, then checked
against the helper. They do not show that a cloud service accepted a policy.
