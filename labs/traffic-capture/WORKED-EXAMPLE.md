# Worked reasoning: guided traffic

This is an explanation of the intended exercise. It is not a saved capture or
a claim that Wireshark was operated. Supply frame numbers from your own run.

L1 requests `/hello`. The toy service returns HTTP 200 and fixed text. In a
capture started in time, look for the TCP handshake, the request containing
`X-Lab-Id: L1`, and the response in the same TCP stream. The request and response
provide application evidence beyond a completed TCP handshake.

L2 requests `/missing`. It receives HTTP 404 because the toy service does not
implement that path. The HTTP response itself shows that the client reached an
HTTP server. Calling this a connection failure would confuse two different
layers. Pair the actual request and response before attributing the 404 to L2.

L3 requests `/marker` and includes `X-Lab-Marker: ORCHARD-CANARY-42`. This is a
harmless label, not an exploit or secret. It is visible because this lab uses
clear-text HTTP. A marker can identify test traffic without making that traffic
malicious.

L4 attempts to connect to another socket owned by the script, bound but never
put into a listening state. The normal outcome is connection refused. The
application creates no HTTP request on this connection, because it cannot
finish connecting. Inspect the SYN/reset exchange if captured. If your result
is a timeout, state that and investigate capture and local policy; do not invent
a reset. Application logs alone do not prove which packets Wireshark saved.

An example finding, completed with your evidence, is: "L2 reached the HTTP
service: request frame ___ and response frame ___ share TCP stream ___. The
server returned 404 for `/missing`. L4 had no HTTP response; client output says
___ and frames ___ show ___. These are different failure types."

For the changed run, `/hello?note=missing` is still a supported path and returns
200. `/missing?note=hello` is still absent and returns 404. The query's wording
does not determine the route. L3's marker changes letter case; that matters for
a later case-sensitive rule, even though the HTTP service still returns 200.

Do not copy fixed frame numbers, claim that a file was captured from synthetic
logs, or infer compromise from the marker. A useful next check depends on the
layer that failed: application routing for the 404, endpoint listening state
for the failed connection, and capture setup when packet evidence is absent.
