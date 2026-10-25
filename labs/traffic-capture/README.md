# Capture traffic you generated

Run a small HTTP service on your own computer, capture its requests in
Wireshark, and explain the difference between a successful response, HTTP 404
and a failed connection. This is an operational exercise: the script makes real
loopback traffic, and you operate Wireshark. It does not generate a capture file
or claim that you captured anything.

Allow 35-50 minutes. You need Python 3.10+, a terminal and an existing Wireshark
installation with permission to capture loopback traffic. On Windows, loopback
capture requires Npcap. On Linux, capture permissions must already be configured.
If the interface is missing or access is denied, record that limitation and ask
the owner of the computer to arrange setup. No installation, firewall changes or
VM changes are part of this lab. No programming is required.

The service binds only to `127.0.0.1`. It serves fixed text, never local files.
The client has no destination option and uses no proxy. A second socket reserves
a local port without listening, giving the failed connection its own target.
Both sockets close at completion or interruption. This is a temporary teaching
service, not a service to leave running.

## Maintained entry point

Open a terminal in this folder. On Windows use `python`; on Linux use `python3`
if that is your Python 3 command. Substitute it consistently below.

```text
python lab.py --help
python lab.py cases
python lab.py run --scenario guided --out run/guided-01
```

Each run needs a fresh direct child of this folder's `run/`. Existing folders,
linked paths and path traversal are refused. Names use lowercase letters,
digits, hyphens or underscores. Outputs include `setup.json`, a blank
`worksheet.txt`, and, after traffic runs, `client-results.json` and
`server-log.json`. The setup records the generator's SHA-256 for traceability.
These files stay ignored by version control. Ports and packet
timing vary; request labels, order and content are fixed for each scenario.

Exit codes are `0` for completed traffic generation, `2` for an input/runtime
error and `130` for interruption. No exit code awards learner completion.
`--no-wait` skips the capture pause for maintenance checks; it does not capture.

## Guided capture: Windows or Linux

1. Run the command above. Leave the terminal at its prompt. Record the **HTTP
   port** and **non-listening port**; the example letters `P` and `Q` below mean
   these printed numbers, not literal filter text.
2. Open Wireshark and choose **Capture > Options**. On Windows select only
   **Adapter for loopback traffic capture**. On Linux select only **lo**. Do not
   select Wi-Fi, Ethernet or an all-interface capture. Wireshark's
   [loopback guide](https://wiki.wireshark.org/captureSetup/loopback) explains why
   traffic sent to the local machine uses a different capture interface.
3. Copy the complete printed capture filter into that interface's capture
   filter box. It has this form:
   `host 127.0.0.1 and tcp and (port P or port Q)`.
   Click **Start**. Capture filters select what is recorded; packets excluded
   now cannot be recovered by changing a display filter later. See the
   [capture filter guide](https://www.wireshark.org/docs/wsug_html_chunked/ChCapCaptureFilterSection.html).
4. Return to the terminal and press Enter. Wait for its summary, then stop the
   Wireshark capture with the red square. Use **File > Save As** to save all
   captured packets as `capture.pcapng` inside this run folder. This is your
   actual capture, separate from the script's application logs.
5. In the display filter bar, paste `display_filter` from `setup.json`. It uses
   different syntax: `ip.addr == 127.0.0.1 && (tcp.port == P || tcp.port == Q)`.
   If HTTP is not recognised on the changing port, select a packet to port P,
   use **Analyze > Decode As**, set that TCP port's current protocol to **HTTP**
   and apply. This is a decoding choice for this session, described in the
   [protocol dissection guide](https://www.wireshark.org/docs/wsug_html_chunked/ChCustProtocolDissectionSection.html).
6. Try `http.request`, `http.response.code == 200`, and
   `http.response.code == 404` separately. Select a request and use **Follow >
   TCP Stream**. Find its `X-Lab-Id` label, request path and response. Record
   actual frame numbers and stream numbers; these are not predetermined.
7. Clear the HTTP filter. Use `tcp.port == Q` with your Q value, then
   `tcp.flags.reset == 1` to examine resets. Compare this evidence with L4's
   client result. A refusal normally produces a reset; a local policy may
   instead cause a timeout. Record what you observed. An HTTP-only display
   filter would hide this failed connection. The
   [display filter guide](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html)
   describes field and value matching.

## Interpret the evidence

| Label | Guided request | Question |
| --- | --- | --- |
| L1 | `GET /hello` | Did TCP connect, and what HTTP response followed? |
| L2 | `GET /missing` | What proves the server was reachable despite HTTP 404? |
| L3 | `GET /marker`, harmless `ORCHARD-CANARY-42` header | Where can you see the marker in clear text? |
| L4 | connection to the owned non-listening port | Was any HTTP response possible? |

**Vocabulary:** loopback means this machine; a port identifies a local endpoint;
TCP provides a connection; HTTP provides application requests and responses;
a reset rejects or terminates a TCP connection; a capture filter limits recorded
packets; a display filter limits visible packets.

Finish the worksheet with your capture, filter, request/response frame pairs,
the L4 result and a short explanation. Keep the worked example closed until you
have made a prediction. Continue with [drills](DRILLS.md).

Troubleshoot an empty capture by checking the selected interface, the printed
ports and whether capture started before Enter. Use a new run for a retry.
Do not infer firewall blocking from silence alone. Packet counts, source ports,
retries, checksums reported by capture tools and timestamps can differ between
systems. There is no TLS, routing, DNS lookup or external network here. A 200
response is a response from this toy service, not proof that a real business
operation succeeded. A 404 is an application result, not a network outage.

The fixtures and text are original fictional practice materials. No university
questions or live incident evidence are included. Maintainer tests validate the
toy service and boundaries; packet capture operation and learner understanding
still require actual evidence. Handover prompt: **Show one successful exchange,
one HTTP error and one failed connection. What did each layer establish, and
what would you check next?**
