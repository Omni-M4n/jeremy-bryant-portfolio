# Worked example: Library account event sample

Open this after your prediction. Each record is a separate piece of evidence.

q1 is confirm. The password matches, and the account is not yet enrolled.
The proof matches and has not been used. Expect accept. The record also
shows accept, so use matches-model.

q2 is challenge on an enrolled account. The password is right, but the proof
does not match. Expect reject. The record shows reject, so use matches-model.

q3 is challenge on an enrolled account. Both the password and unused proof
match. Expect accept. The record shows accept, so use matches-model.

These answers show that the supplied records follow the rules. They do not
show that you ran the service. For that evidence, keep the redacted event
log from your own practice run.

After successful local recovery, active_sessions must be zero.
The recovery_used value must be true. The enrolled value must be false until
you confirm again. These state changes show more of this exercise's stages
than a screenshot that only shows a code was entered.
