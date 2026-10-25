# Worked example: room timer

A timer sleeps in the background. Its setup says to run as `labsvc`. The process
list also says `labsvc`, so `s1` is `identity-matches`. This says who runs it;
it does not show that every file permission is suitable.

The helper account's one rule names `/usr/bin/id`, target account `labsvc`, and
argument `-u`. Request `q1` matches all three, so it is `allowed-by-listed-rule`.
Request `q2` asks for `-un`. That is a different argument and is `not-listed`.
Do not assume that permission for one use of a program covers every use.

Cite the service record, rule 0 and both request records. Then write what you
would measure in a VM: process user, exact command line, output and exit status.
