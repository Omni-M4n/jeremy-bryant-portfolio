# Guided example: a command result needs a question

Read this after saving your own explanation. This example uses a made-up Linux command notebook. The helper does not inspect any host process or service.

| Record | Reasoning | Decision |
|---|---|---|
| P1 | The command received three path arguments: `notes`, `with`, `spaces.txt`. The intended file is `/lab/run/notes with spaces.txt`, which the supplied inventory contains. Correct the argument boundary before diagnosing a missing file. | `repair-path-quoting` |
| S1 | Ordinary `grep -F READY` returned 1, selected zero lines and wrote no diagnostic. It read the supplied file but found no match. This differs from exit 2. | `no-matching-lines` |
| D1 | 2,000 available bytes minus 1,500 required bytes leaves 500 bytes. This meets this tiny fictional budget only. | `stated-space-budget-met` |
| V1 | The supplied service-state query established that the unit is present and stopped. It does not say the service should be running or why it stopped. | `service-stopped` |
| R1 | The selected PID 420 matches the previously recorded expected PID 420. The name `python3` adds context, not a conclusion about purpose. | `process-pid-correlated` |
| L1 | A listener at `127.0.0.1:8765` is associated with PID 420, matching the expected PID in this supplied observation. | `loopback-listener-correlated` |

For P1, try a quoted, literal read of the exact path from the known working folder. For S1, check the intended pattern and file text before claiming a fault. For V1, find the service state the task expects. Check a relevant log only if the actual state differs. Do not restart the service just because it is stopped.

The notebook shows a stopped `lab-demo.service` and a separate Python process. No given unit/PID mapping links them. They may be separate things, so these records do not prove a conflict. If the link matters, ask which command runs the service and which PID belongs to it.

The process/socket link also depends on time. A process can exit and its PID can be reused. A socket's bind address does not show firewall rules or every route. A small next check is fresh local PID/listener evidence. There is no need to scan a remote system.

A short handover could say: “P1 needs one quoted path argument. S1 finished its search and found no matching lines. D1 meets the 1,500-byte budget with 500 bytes to spare. V1 is stopped. The records do not say what state it should have. R1 and L1 share PID 420. The listener is on loopback. No record shows harmful intent. The link between service and process is unknown.” Cite `notebook.txt` and the exact record IDs.

For a live attempt, keep the actual command output and the status saved at once. Copying these given results into a notebook does not show that you ran a real shell command.
