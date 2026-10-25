# Worked example: note printer

The note printer started at version 1.0. The target is 1.1. For `p1`, the checked
source is official, the installer exit code is 0, and a separate query reads 1.1.
The small print check passes. Those observations support the update.

No rollback version was observed. A saved plan is not a tested restoration. Record
`update-verified-rollback-untested`, and cite `installed_version`, `smoke` and both
rollback fields. The next action is a rollback test in the disposable VM.

For local practice, first write down what `Hello Sam` should look like. Compare
that known result with the applied candidate. Then compare the restored file hash
with the saved baseline and run the greeting again. These are separate checks.
