# Worked example: one changed ID

This is the expected reasoning for the guided scenario. It is not a record of
a learner's completed session. Keep it closed until you have written your first
prediction in the generated worksheet.

The seeded roster says Ada owns 101 and 103; Ben owns 102. A legitimate task is
for each person to read their own order. Hiding Ben's link from Ada is useful
presentation, but a user can edit a request independently of the page.

An intercepted baseline will resemble this. The cookie shown is a placeholder;
keep the real disposable token captured in your own current run.

```http
GET /api/orders/101 HTTP/1.1
Host: 127.0.0.1:8765
Cookie: lab_session=<Ada token captured in this run>

```

After sending the unchanged baseline through Repeater, the response is 200 and
its JSON includes `"id": "101"`, `"owner": "ada"`, and the fictional lantern
note. Record `X-Lab-Mode: vulnerable` and `X-Lab-Scenario: guided` as context.

Change only the request path to `/api/orders/102`. The selected Ada cookie stays
the same. In vulnerable mode the response is also 200, but the body says
`"owner": "ben"` and contains `Fictional order: 1 silver cardboard moon.`
The owner roster, unchanged account, requested ID and returned content together
support a finding: **the order-read endpoint returns another account's record
to Ada in the guided vulnerable configuration**. The status alone would not
establish that the wrong content was disclosed.

Reverse the direction with a freshly captured Ben request. His own 102 returns
200; changing only its ID to 101 returns Ada's record in vulnerable mode. These
two comparisons test the same failure in both directions.

After stopping the server and starting fixed mode, select each account again
and capture new requests. The same-ID comparisons now have these outcomes:

| Current account | ID | Vulnerable | Fixed | Meaning |
| --- | --- | --- | --- | --- |
| Ada | 101 | 200, Ada record | 200, Ada record | Necessary access retained |
| Ada | 102 | 200, Ben record | 403, error only | Cross-user read denied |
| Ada | 103 | 200, Ada record | 200, Ada record | A second legitimate record remains usable |
| Ben | 102 | 200, Ben record | 200, Ben record | Ben's necessary access retained |
| Ben | 101 / 103 | 200, Ada record | 403, error only | Reverse direction denied |

The server checks the selected account against the stored order owner before
returning a record in fixed mode. If every request returned 403, the change
would break legitimate use and would not satisfy this exercise's rule.

With a valid account, ID 999 returns 404 because no record was seeded. `abc`
returns 400 because it is not a supported three-digit ID. Removing the session
cookie returns 401. Those outcomes describe different conditions: none is a
substitute for testing a known other user's existing object with a valid
session. In particular, a stale token returning 401 after restart does not prove
the ownership check worked.

A bounded handover might read:

> In the local guided configuration, I kept Ada's session unchanged and changed
> order 101 to 102 in Repeater. The vulnerable response returned Ben's fictional
> note. After restarting in fixed mode and selecting fresh sessions, cross-user
> requests returned 403 without record content. Both accounts still received
> their own records. This supports the owner check for the tested read endpoint;
> it does not assess real authentication, writes or other application routes.

Use that wording only after doing and documenting those actions yourself.
Replace it with your actual observations and any mismatch. Keep the request and
response evidence private in the run folder and ask a reviewer to challenge
your explanation, especially the difference between 401, 403 and 404.
