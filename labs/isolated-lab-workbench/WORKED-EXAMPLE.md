# Guided example: verify each claim separately

Open this after saving your prediction. This example explains supplied fictional records; it does not report an actual VM run.

`inventory.txt` names `practice-vm-a`, records a disposable purpose and lists **all eight** NIC slots as disabled. The guest summary has zero default routes and no non-loopback addresses. Those observations agree with the declared disconnected-loopback design. `scope` is `disposable-vm-recorded` and `network` is `disconnected-boundary-supported`. The first label describes a declaration; the second describes evidence for this boundary at this time. Neither is a general safety verdict.

Shared folders are zero and clipboard, drag/drop and passthrough are false, so `host-paths` is `no-listed-host-transfer-path`. A network-only check would miss these other ways of crossing the boundary. The real workflow additionally reviews storage, USB, remote display and serial connections; the compact offline model does not enumerate all possible devices.

`connectivity.txt` records a server bound to `127.0.0.1`, HTTP 200 and exact body `BASELINE` followed by LF. It also records connection refusal after the server stops. The positive and negative observations establish that the intended local service responded and then stopped responding: `connectivity` is `loopback-pair-demonstrated`. They do not test host or internet reachability.

`restore.txt` links snapshot `baseline-a` to the same VM and records restoration of that same snapshot on a normal-mode disk. The SHA-256 for `BASELINE\n` is `8d7fca7dd0556ad56dc2ad09871cb6ebd6bd740cc5c9ef4ca4661330a118d98d`. Confirm this against the fixture rather than trusting a copied digest in a note. The changed file hash must differ; the restored hash must equal the baseline. The supplied three observations meet those comparisons, so `rollback` is `dummy-file-rollback-demonstrated`.

The five positive decisions produce `review: supplied-evidence-complete`. A concise explanation is: “All listed adapter slots are disconnected, the supplied guest route/address summary agrees, and no listed host transfer channel is enabled. The exact loopback body responds only while the server runs. The same snapshot and VM are identified, a real marker change is evidenced, and the restored marker matches its baseline.” Cite the exact data fields and artifact names.

For the real attempt, the reviewer must replace supplied statements with actual screenshots, commands and file hashes. A claim such as “the VM is safe because curl failed” misses both configuration evidence and the purpose of the failed connection. A claim such as “restore worked because the file still says BASELINE” misses the changed state that proves there was something to undo.
