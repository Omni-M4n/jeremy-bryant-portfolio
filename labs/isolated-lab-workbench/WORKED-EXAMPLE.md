# Guided example: verify each claim separately

Open this after saving your prediction. This example explains made-up records. It does not report a real VM run.

`inventory.txt` names `practice-vm-a` and says it is for disposable practice. It lists **all eight** NIC slots as disabled. The guest summary has no default routes and no addresses outside loopback. These records agree with the stated disconnected-loopback design. `scope` is `disposable-vm-recorded`. The `network` result is `disconnected-boundary-supported`. The first label reports a claim about the VM's purpose. The second reports evidence for this boundary at this time. Neither is a general verdict that the VM is safe.

Shared folders are zero. Clipboard, drag/drop and passthrough are false. Thus `host-paths` is `no-listed-host-transfer-path`. A network check alone would miss these other ways across the boundary. The real task also checks storage, USB, remote display and serial connections. This small offline model does not list every possible device.

`connectivity.txt` records a server bound to `127.0.0.1`. It gives HTTP 200 and the exact body `BASELINE` followed by LF. It also records connection refusal after the server stops. Together, these show that the intended local service replied and then stopped replying. The `connectivity` result is `loopback-pair-demonstrated`. This does not test whether the host or internet can be reached.

`restore.txt` links snapshot `baseline-a` to the same VM. It records a restore of that snapshot on a normal-mode disk. The SHA-256 for `BASELINE\n` is `8d7fca7dd0556ad56dc2ad09871cb6ebd6bd740cc5c9ef4ca4661330a118d98d`. Check this against the fixture. Do not just trust a digest copied into a note. The changed file's hash must differ. The restored hash must match the baseline. The three given records meet these checks. Thus `rollback` is `dummy-file-rollback-demonstrated`.

The five positive results give `review: supplied-evidence-complete`. A short answer is: “All listed adapter slots are disconnected. The guest route/address summary agrees. No listed host transfer channel is enabled. The exact loopback body appears only while the server runs. The records name the same snapshot and VM. They show that the marker changed, then returned to its baseline.” Cite the exact data fields and file names.

For a real attempt, the reviewer needs real screenshots, commands and file hashes in place of these made-up records. “The VM is safe because curl failed” is not enough. It misses the settings and why the connection was meant to fail. “Restore worked because the file still says BASELINE” also misses a step. The changed state shows there was something to undo.
