# Guided case: review after your first attempt

The first three ticket requests return 200. Their remaining values are 2, 1
and 0. The fourth arrives in the same window. All three places are used, so
it returns 429 with remaining 0 and a Retry-After header.

The runner waits 2.15 seconds. The next request is past the two-second
window. It starts a new window and returns 200 with remaining 2.
Expected status sequence: 200, 200, 200, 429, 200.

Use the times and actual Retry-After value to explain what happened. The
header can be 1 or 2. It depends on when the rejected request arrives. Check
that normal use works again after the wait. A rejection alone cannot show
this. These five requests do not show how much traffic the server can handle.
