# Reading room visit: review after your first attempt

The first login creates a server record. The next profile request presents
its cookie, so both return 200 and `signed-in`.

Logout removes that record and returns 200 with `signed-out`. The runner
keeps a private copy of the old cookie only to test it. `old-profile` sends
the copy and receives 401 with `signed-out`. This is evidence that the server
rejected the old ID; the client did not merely hide its login display.

The final login creates a different session and the final profile returns
200. The expected status sequence is 200, 200, 200, 401, 200, 200.

Read the method, path, status, body and elapsed time in `evidence.json`.
Cookie values must remain redacted in a handover. Explain the negative result
and the successful normal use. A 401 alone does not prove every logout path
in another app is correct.
