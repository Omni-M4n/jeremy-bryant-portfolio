# Burp practice: whose order is this?

Use Burp Suite Community Edition to pause a request and send it again by hand. Change an order ID. Compare the server before and after a prepared fix. This lab's Lantern Orders app has two made-up users and three craft orders. Can one user read the other user's order when the page only shows their own links?

Allow 45–75 minutes for the guided attempt and 20 minutes for a later repeat. You need a terminal, a browser and Burp's manual tools. You do not need to write code.

## Prerequisites and scope

- You need Python 3.10+ and Burp Suite Community Edition already on the **same machine**. Use Burp's bundled browser. This lab does not install tools, change a VM or set up your everyday browser. You do not need an online account.
- Open a terminal in this lab folder. On Windows, use PowerShell. Commands below use `python`. Use your existing Python command in its place if needed.
- Test only this process at `http://127.0.0.1:8765/`. Do not use an outside target or another local service. No scanner, extension, Intruder job or paid feature is needed. The server has no host or target argument. It always binds to `127.0.0.1`. Do not expose it through a tunnel or port forward.

Choosing Ada Finch or Ben Reed makes a temporary session cookie without a password. A cookie is a value the browser sends to identify this session. Anyone using this app can choose either account. This is **not real authentication** or a privacy service. It does not model safe sessions for a live service. Keep the same account cookie when you compare two order IDs. Changing the account too would test a different question.

## Maintained command contract

`lab.py` is the single entry point. It uses only Python's standard library.

```text
python -B lab.py --help
python -B lab.py serve --help
python -B lab.py cases
python -B lab.py serve --mode vulnerable --scenario guided --out run/guided-vulnerable-01
```

`serve` runs until Ctrl+C. You must state `--mode`. `--scenario` can be `guided` or `changed`. It defaults to `guided`. `--port` defaults to 8765 and accepts 1024–65535. If the port is busy, stop this attempt. Use a fresh output name with `--port 8766`. Use the new printed URL and port in every Burp step.

`--out` starts from this lab folder, whatever the terminal's current folder. Use a fresh direct child such as `run/attempt-01`. The tool refuses full paths, nested folders and paths that escape the folder. It also refuses existing paths, symbolic links and Windows reparse or junction paths. These are paths that can point elsewhere. A failed start may leave its new folder. Keep it and use a new name. Version control ignores files under `run/`. These checks guard against path mistakes. They do not protect against another local process changing paths at the same time. Exit 0 means a normal stop or a read-only command. Exit 2 means bad arguments, an output-path problem or a port that cannot be used.

Each successful run creates these files:

| File | Purpose |
| --- | --- |
| `run.json` | Mode, scenario, exact URL and process ID; manual completion remains pending |
| `roster.json` | Synthetic owner roster used by this run |
| `worksheet.md` | Blank manual evidence table and explanation prompts |
| `events.jsonl` | Server outcomes with account labels and IDs, without session tokens |

The server serves only the home page, account picker and order routes held in memory. It cannot browse or serve your folders. It does not read login details, fetch remote URLs, change orders or send data elsewhere. Its loopback and Host/Origin checks limit this exercise. They do not prove that Python's development HTTP server is secure.

## Guided attempt

1. Run the vulnerable command above. Leave that terminal open. Check the printed URL is `http://127.0.0.1:8765/`. Check mode is `vulnerable` and scenario is `guided`. Open the new `worksheet.md` in your text editor.
2. Start your installed Burp Community with a temporary project and default settings. In **Proxy > Intercept**, leave interception off at first. Use **Open Browser**. That browser is already set up to send its traffic through Burp. Open **Settings > Tools > Proxy > Proxy listeners**. Check that its listener binds to loopback, normally `127.0.0.1:8080`. It must not bind to all interfaces. The [Proxy settings reference](https://portswigger.net/burp/documentation/desktop/settings/tools/proxy) explains listeners. Proxy port 8080 and app port 8765 do different jobs. Do not change an unrelated listener.
3. In that browser, enter `http://127.0.0.1:8765/` exactly. Use HTTP, not HTTPS. Use `127.0.0.1`, not `localhost`. You do not need to install a certificate. Choose **Ada Finch**, then **Select account**. The home page should show Ada, **VULNERABLE**, `guided`, and links to orders 101 and 103.
4. In **Target > Site map**, right-click the `http://127.0.0.1:8765` node. Choose **Add to scope**. If asked, exclude out-of-scope traffic from logging. Check the scope entry in Settings. Keep only this HTTP host and port in the temporary project. In **Proxy > HTTP history**, open the display filter. Select **Show only in-scope items**. Scope filters help you focus. They do not block all out-of-scope requests. Browse only this app in this browser. See the [scope guide](https://portswigger.net/burp/documentation/desktop/getting-started/setting-target-scope).
5. Turn interception on in **Proxy > Intercept**. In the browser, click Ada's order 101. Burp holds the request, so the browser waits. Check `GET /api/orders/101`, the exact Host, and `Cookie: lab_session=...`. Keep this baseline request unchanged. Click **Forward**, then turn interception off. Record the matching HTTP history entry number. The JSON should show order 101 owned by `ada`. Drop any unrelated traffic that is held. Do not send it to this lab. See the [interception guide](https://portswigger.net/burp/documentation/desktop/getting-started/intercepting-http-traffic).
6. In HTTP history, right-click that **GET order request**. Choose **Send to Repeater**. In Repeater, check the destination is HTTP, `127.0.0.1`, port 8765. Click **Send** with the request unchanged. Read the status, body, `X-Lab-Mode` and `X-Lab-Scenario`. Write your prediction for order 102.
7. Change only `/api/orders/101` to `/api/orders/102`. Keep the Host, method and Ada cookie. Click **Send** once. Record the status and the returned owner and note. Compare with `roster.json`: guided order 102 belongs to Ben. Explain what this shows about this endpoint. The [Repeater guide](https://portswigger.net/burp/documentation/desktop/getting-started/reissuing-http-requests) explains manual sends, edits and response history.
8. In the browser, return to `/`, select Ben and open order 102. Send this fresh GET to a **separate Repeater tab** labelled Ben. Check his own 102, then change only its ID to 101. Record both results. Keep the Ada and Ben tabs separate. A browser account change does not rewrite an old captured request. Do not guess tokens or use real accounts.
9. Save screenshots or copied request and response evidence beside the worksheet. Do this before closing the temporary Burp project. In your notes, label tokens by account. The generated event log alone cannot prove that you used Burp.

## Apply the prepared fix and retest

Fixed mode already has the server's owner check. You do not need to edit code. Stop the vulnerable process with **Ctrl+C in its terminal**, then start:

```text
python -B lab.py serve --mode fixed --scenario guided --out run/guided-fixed-01
```

Refresh `/` in Burp's browser. Check **FIXED** and `guided`. Select Ada again. Old session cookies stop working after a server restart. Capture a fresh order 101 request and send it to a new Repeater tab. A 401 from an old cookie does not prove the owner fix works.

Predict each outcome. Then perform these checks by hand with fresh Ada and Ben sessions. Save the results in the fixed run's worksheet.

| Selected account | Request | Expected outcome in fixed mode |
| --- | --- | --- |
| Ada | `/api/orders/101` and `/api/orders/103` | 200; Ada's correct record is present |
| Ada | `/api/orders/102` | 403; no order note or record body |
| Ben | `/api/orders/102` | 200; Ben's correct record is present |
| Ben | `/api/orders/101` and `/api/orders/103` | 403; no order note or record body |
| Either valid account | `/api/orders/999` | 404; no such seeded order |
| Either valid account | `/api/orders/abc` | 400; invalid ID format |
| Cookie header removed | `/api/orders/101` | 401; select an account first |

The rule is narrow. **A selected training account may read an existing order only when the server's owner field matches that account.** The browser's links are the same in both modes. The server must check the requested record. Checking the page that links to it is not enough. A 200 must include the correct record. A denied response must leave it out. A status code alone cannot prove either result.

## Stop, troubleshoot and hand over

Turn interception off and save your evidence. Press Ctrl+C in the server terminal. Wait for the stopped message, then reload the app URL. It should fail to connect. Close the lab browser and temporary Burp project. These steps have not changed your everyday browser's proxy settings or certificates. Keep the `run/` notes for review. There is no automatic delete command. Use a new name for a fresh attempt.

If the browser waits, check for a held Proxy request. Use Forward or turn interception off. If history is empty, check you used **Open Browser** and the exact printed URL. Then check the scope filter. A 421 means Host did not match the printed host and port. A 403 on `/session` means Origin was missing or different. Reload the form from the printed URL. A 401 after restart means you need to select a new session. A bind error often means the port is in use. Do not kill an unknown service. Use the alternate port and a new run folder. If Burp is absent, stop here. Direct HTTP tests do not replace the requested Burp practice.

Keep a short finding, a before/after evidence table, proof that own-record access still works, and one limit. Use the worksheet's handover sentence. Continue with [the drills](DRILLS.md). Open [the worked example](WORKED-EXAMPLE.md) after you write your first predictions.

## Software validation and limits

```text
python -B test_lab.py
```

The tests open temporary **loopback** listeners and send real HTTP requests. They check both modes, both accounts and both owner lists. They cover valid and invalid requests, session restarts, Host/Origin checks and refused output paths. They start the real CLI, which is the command-line tool. They check its files and home page, stop that test process, and check its socket closes. Test files stay in fresh `run/software-tests-*` and `run/cli-smoke-*` folders. If the system cannot create a symlink, that check is marked skipped. It is not a pass.

Passing tests show how the lab software behaves. They do not show that you paused a request, understood the result or did a manual Burp retest. **Hands-on completion remains pending until your evidence and explanation are reviewed.**

This app models one read endpoint with an owner-only rule. It has no real authentication or password handling. It does not save records across runs or model writes, sharing, roles or account recovery. It has no production session protection. Its 403 and 404 responses reveal whether an ID exists. This is deliberate for teaching. It does not show privacy protection or prove a whole app is secure.

The linked interception, scope and Repeater guides were checked on 23 October 2026. So was PortSwigger's [horizontal access-control workflow](https://portswigger.net/burp/documentation/desktop/testing-workflow/vulnerabilities/access-controls/horizontal-access-controls). Those guides describe their own exercises. Use only this local Lantern Orders target for this lab. Burp's labels may differ with the installed version.

A **proxy** observes traffic between browser and server. **Intercept** pauses a request before it is sent on. **Repeater** lets you edit and resend a request by hand. An **object ID** selects a record. A **session** identifies the chosen account in this toy app. **Authorization** decides whether that account may read that record. **Horizontal access** crosses between accounts with the same type of rights. A **regression check** tests that needed behaviour still works after a change.
