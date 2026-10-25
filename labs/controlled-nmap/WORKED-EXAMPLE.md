# Inventory notebook 1: worked example

Read s01 beside the target's local note. Port 8000 is open and a listener binds to the target address. The HTTP probe agrees with the known HTTP service. Record `open-listener-corroborated;label-probe-consistent`. This supports the entry in your list. It does not prove a product version or a security flaw.

For s02, the 8001 listener binds only to loopback. A different machine cannot reach that bind through the target's network address. The closed result is `closed-consistent-with-snapshot`. For s03, no 8002 listener is listed and the scan is closed. Use the same label, but cite this row's evidence.

Save the target address, port, bind, scan state and label source in separate columns. If the snapshots were taken at different times, a program could have started or stopped. The helper cannot rule that out. These records were made up for practice. They are not a scan that you collected.
