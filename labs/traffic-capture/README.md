# Capture traffic you generated

Run a small HTTP service on your own computer. Capture its requests in Wireshark. Compare a successful response, HTTP 404 and a failed connection. The script makes real loopback traffic, which stays on your machine. You operate Wireshark. The script does not make a capture file or claim that you captured anything.

Allow 35-50 minutes. You need Python 3.10+, a terminal, and Wireshark already installed. You must have permission to capture loopback traffic. On Windows, this needs Npcap. On Linux, capture access must already be set up. If the interface is missing or access is denied, note the limit. Ask the computer's owner to arrange setup. This lab includes no installs or changes to firewalls or VMs. You do not need to write code.

The service binds only to `127.0.0.1`. It serves fixed text and never serves local files. The client has no destination option and uses no proxy. A second socket holds a local port but does not listen on it. This gives the failed connection its own target. Both sockets close when the run ends or is stopped. Do not leave this teaching service running.

## Maintained entry point

Open a terminal in this folder. On Windows, use `python`. On Linux, use `python3` if that is your Python 3 command. Use that choice in all commands below.

```text
python lab.py --help
python lab.py cases
python lab.py run --scenario guided --out run/guided-01
```

Each run needs a fresh direct child of this folder's `run/`. This means a folder one level inside it. The tool refuses existing folders, linked paths and paths that escape this folder. Names use lowercase letters, digits, hyphens or underscores. Each run writes `setup.json` and a blank `worksheet.txt`. After it makes traffic, it adds `client-results.json` and `server-log.json`. Setup records the generator's SHA-256 hash, a value used to check which file was used. Version control ignores these files. Ports and packet timing vary. Request labels, order and content stay fixed for each scenario.

Exit code `0` means traffic was made. Code `2` means an input or runtime error. Code `130` means the run was stopped. No exit code proves you finished the lab. `--no-wait` skips the capture pause for maintenance checks. It does not capture traffic.

## Guided capture: Windows or Linux

1. Run the command above and leave the terminal at its prompt. Record the **HTTP port** and **non-listening port**. Below, `P` and `Q` stand for these printed numbers. Do not type the letters into the filters.
2. Open Wireshark and choose **Capture > Options**. On Windows, select only **Adapter for loopback traffic capture**. On Linux, select only **lo**. Do not select Wi-Fi, Ethernet or all interfaces. Wireshark's [loopback guide](https://wiki.wireshark.org/captureSetup/loopback) explains why traffic to this machine uses its own interface.
3. Copy the full printed capture filter into that interface's capture filter box. It has this form: `host 127.0.0.1 and tcp and (port P or port Q)`. Click **Start**. A capture filter chooses which packets to record. A later display filter cannot bring back packets you did not record. See the [capture filter guide](https://www.wireshark.org/docs/wsug_html_chunked/ChCapCaptureFilterSection.html).
4. Return to the terminal and press Enter. Wait for the summary. Stop the Wireshark capture with the red square. Use **File > Save As**. Save all captured packets as `capture.pcapng` in this run folder. This is your actual capture. The script's logs are separate evidence.
5. Paste `display_filter` from `setup.json` into the display filter bar. Its syntax differs: `ip.addr == 127.0.0.1 && (tcp.port == P || tcp.port == Q)`. If Wireshark does not show HTTP, select a packet to port P. Use **Analyze > Decode As**. Set that TCP port's current protocol to **HTTP** and apply. This tells Wireshark how to read these packets for this session. See the [protocol dissection guide](https://www.wireshark.org/docs/wsug_html_chunked/ChCustProtocolDissectionSection.html).
6. Try `http.request`, `http.response.code == 200`, and `http.response.code == 404` one at a time. Select a request and use **Follow > TCP Stream**. Find its `X-Lab-Id` label, path and response. Record the real frame and stream numbers from your run. They are not fixed in advance.
7. Clear the HTTP filter. Use `tcp.port == Q` with your Q value. Then use `tcp.flags.reset == 1` to look for resets. Compare this evidence with L4's client result. A refused connection will often cause a reset. Local rules may cause a timeout instead. Write what you saw. An HTTP-only filter would hide this failed connection. The [display filter guide](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html) explains how to match fields and values.

## Interpret the evidence

| Label | Guided request | Question |
| --- | --- | --- |
| L1 | `GET /hello` | Did TCP connect, and what HTTP response followed? |
| L2 | `GET /missing` | What proves the server was reachable despite HTTP 404? |
| L3 | `GET /marker`, harmless `ORCHARD-CANARY-42` header | Where can you see the marker in clear text? |
| L4 | connection to the owned non-listening port | Was any HTTP response possible? |

**Loopback** means this machine. A **port** names a local endpoint, or place where a service can connect. **TCP** provides a connection. **HTTP** carries app requests and responses. A **reset** rejects or ends a TCP connection. A **capture filter** limits which packets are saved. A **display filter** limits which saved packets you can see.

Finish the worksheet. Include your capture, filter and pairs of request and response frames. Add L4's result and a short reason for each claim. Keep the worked example closed until you have made a prediction. Continue with [drills](DRILLS.md).

If the capture is empty, check the interface and printed ports. Check that capture began before you pressed Enter. Use a new run to retry. Silence alone does not prove a firewall blocked traffic. Packet counts, source ports, retries and times can differ across systems. So can checksums shown by capture tools. There is no TLS encryption, routing, DNS lookup or outside network here. A 200 comes from this toy service. It does not prove a real business task worked. A 404 is an app result. It does not mean the network is down.

The files and text were made up for this lab. They contain no university questions or live incident evidence. Maintainer tests check the toy service and its limits. You still need real capture evidence and an explanation of it. Use this handover prompt: **Show one successful exchange, one HTTP error and one failed connection. What did each layer show? What would you check next?**
