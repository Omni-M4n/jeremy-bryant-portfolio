# Worked reasoning: guided traffic

This explains the guided exercise. It is not a saved capture or a claim that someone used Wireshark. Save your first prediction before reading it. Supply frame numbers from your own run.

L1 requests `/hello`. The toy service returns HTTP 200 and fixed text. If capture started in time, look for the TCP handshake. This is the exchange that starts a connection. Find the request with `X-Lab-Id: L1` and its response in the same TCP stream. These show what the app exchanged. A handshake alone cannot show that.

L2 requests `/missing`. The service has no route for that path, so it returns HTTP 404. This response shows that the client reached an HTTP server. It is not a failed connection. Pair the actual request and response before you assign the 404 to L2.

L3 requests `/marker` with `X-Lab-Marker: ORCHARD-CANARY-42`. This is a harmless label. It is neither an exploit nor a secret. You can read it because this lab uses clear-text HTTP. A marker can help you find test traffic. It does not make that traffic harmful.

L4 tries to connect to a second socket owned by the script. That socket holds a port but never listens. The normal result is connection refused. The app sends no HTTP request here because it cannot finish connecting. Look for a SYN and reset exchange if it was captured. If you see a timeout, say so. Check capture setup and local rules. Do not invent a reset. App logs alone do not prove which packets Wireshark saved.

You could write: "L2 reached the HTTP service. Request frame ___ and response frame ___ share TCP stream ___. The server returned 404 for `/missing`. L4 had no HTTP response. Client output says ___ and frames ___ show ___. These are different failure types." Fill the blanks with your own evidence.

For the changed run, predict each outcome from the request and service behaviour. Save your reasons before checking the logs and capture. Compare the marker bytes with guided. Explain what you can and cannot infer from any difference.

Do not copy fixed frame numbers or claim that made-up logs are a capture. Do not infer a break-in from the marker. Choose the next check based on the layer that failed. For 404, check the app's route. For a failed connection, check whether the endpoint is listening. If packet evidence is missing, check capture setup.
