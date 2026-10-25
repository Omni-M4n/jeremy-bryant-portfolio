# Worked example: one changed ID

This explains the guided case. It is not a record of a learner's completed session. Keep it closed until you save your first prediction in the worksheet.

The owner list says Ada owns 101 and 103. Ben owns 102. Each person should be able to read their own order. Hiding Ben's link from Ada changes the page. But a user can edit a request without using that page.

A captured baseline will look like this. The cookie shown is a placeholder. Keep the real temporary token captured in your current run.

```http
GET /api/orders/101 HTTP/1.1
Host: 127.0.0.1:8765
Cookie: lab_session=<Ada token captured in this run>

```

Send the unchanged baseline through Repeater. The response is 200. Its JSON includes `"id": "101"`, `"owner": "ada"`, and the made-up lantern note. Record `X-Lab-Mode: vulnerable` and `X-Lab-Scenario: guided` to show the test setup.

Change only the path to `/api/orders/102`. Keep the same Ada cookie. In vulnerable mode, the response is also 200. But its body says `"owner": "ben"` and includes `Fictional order: 1 silver cardboard moon.` Read this with the owner list, unchanged account and requested ID. Together, they support this finding: **this order-read endpoint returns Ben's record to Ada in guided vulnerable mode**. Status alone would not prove that the wrong content was returned.

Reverse the test with a fresh captured Ben request. His own 102 returns 200. Change only its ID to 101. Vulnerable mode returns Ada's record. These two checks test the same failure in both directions.

Stop the server and start fixed mode. Select each account again and capture fresh requests. The same-ID checks now give these results:

| Current account | ID | Vulnerable | Fixed | Meaning |
| --- | --- | --- | --- | --- |
| Ada | 101 | 200, Ada record | 200, Ada record | Necessary access retained |
| Ada | 102 | 200, Ben record | 403, error only | Cross-user read denied |
| Ada | 103 | 200, Ada record | 200, Ada record | A second legitimate record remains usable |
| Ben | 102 | 200, Ben record | 200, Ben record | Ben's necessary access retained |
| Ben | 101 / 103 | 200, Ada record | 403, error only | Reverse direction denied |

In fixed mode, the server checks the chosen account against the stored owner. It does this before returning the record. If every request returned 403, valid use would break. That would fail this lab's rule.

With a valid account, ID 999 returns 404. There is no such stored record. `abc` returns 400 because it is not a supported three-digit ID. Removing the session cookie returns 401. These results test different conditions. None replaces a test for another user's known record with a valid session. A 401 from an old token after restart does not prove the owner check worked.

A handover could read:

> I used the local guided setup. I kept Ada's session and changed order 101 to 102 in Repeater. Vulnerable mode returned Ben's made-up note. I restarted in fixed mode and chose fresh sessions. Requests across accounts returned 403 with no record content. Each account could still read its own records. This supports the owner check for this read endpoint. It does not assess real authentication, writes or other app routes.

Use this wording only after you do and record those steps. Replace it with what you saw, including any mismatch. Keep request and response evidence private in the run folder. Ask a reviewer to test your reasons. Be ready to explain how 401, 403 and 404 differ.
