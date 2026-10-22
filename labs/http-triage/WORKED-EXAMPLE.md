# Worked example: seed 53, mixed

Try your own explanation first. This is a supplied reference analysis, not a
record of Jeremy independently completing an investigation.

## Establish scope

```sh
python lab.py check
python lab.py timeline
python lab.py triage --output runs/worked-report.json
python lab.py check --report runs/worked-report.json
```

The export contains **21** synthetic requests for `practice-library-053.test`,
with a collection interval of **2032-06-14 09:39:00–09:44:00 UTC**, inclusive.
There are three recorded source addresses. `complete-for-fixture` confirms the
generator's intended export, not real-world visibility. The timestamps are
invented future dates. CSV file order is shuffled; use the sorted timeline.

## Compare the sources

| Source | Evidence | Interpretation and next check |
| --- | --- | --- |
| `192.0.2.65` | 4 requests, `HTTP-0001`–`HTTP-0004`; three `GET` responses of `200`, then `POST /contact` with `303` | Compatible with ordinary browsing and a form redirect. The absent redirect header and request body limit further interpretation. |
| `198.51.100.126` | 12 requests, `HTTP-0005`–`HTTP-0016`, 09:42:00–09:42:11; eleven `GET`, one `HEAD`; nine `200`, three `404`; no watched path | The volume rule matches. Public pages, stale guide paths and the scheduled-job note support a crawler explanation. Confirm the job's timing and requests before treating the note as verified. |
| `203.0.113.138` | 5 requests, `HTTP-0017`–`HTTP-0021`, 09:43:00–09:43:20; four different watched paths, then `POST /login` | Watched-path variety matches despite lower volume. Requests for configuration, administration, backup and debug paths make probing plausible. Check authorisation and corresponding application records. |

The default settings are volume **8** and watched-path variety **3**. The report
contains **two review prompts**, one for volume and one for path variety. These
are questions for review, not two proven incidents.

For the third source, `HTTP-0017` requested `/.env` and received `404`;
`HTTP-0018` requested `/admin` and received `403`; `HTTP-0019` and `HTTP-0020`
requested `/backup.zip` and `/debug`, both with `404`. These records show paths
and outcomes observed by this logging component. They do not demonstrate code
execution, exposed file contents or account access.

`HTTP-0021` is `POST /login`, status `200`, with a 470-byte response body recorded.
The export contains neither the body nor an authentication result. A response
that redisplays a form is one possibility. “The attacker logged in successfully”
would go beyond this evidence.

The crawler and the watched-path source both claim `PracticeCrawler/1.0` as
their user-agent. That text is client-supplied. It cannot transfer the owner's
scheduled-job note from one source to the other or establish a shared actor.

## Example handover

> Review requests from 203.0.113.138 to practice-library-053.test during
> 2032-06-14 09:43:00–09:43:20 UTC. Four distinct watched paths appear in
> HTTP-0017 through HTTP-0020, exceeding the configured threshold of three.
> Probing is plausible; an authorised test remains possible. HTTP-0021 records
> a 200 response to POST /login, with no authentication outcome available.
> Check authorised testing records and correlate the five event times with
> application routing and authentication records. The export alone does not
> establish disclosure or compromise. Separately, corroborate the scheduled
> crawler note for 198.51.100.126 before closing its volume prompt.

This handover names evidence and uncertainty, and requests information that
could change the decision. It does not recommend blocking an address merely
because it sent the most requests.

## How the answer changes

With the same seed and `soft-200`, `HTTP-0017` changes to `200` with 128 body
bytes. A third prompt, `watched-path-200`, appears. The new context note says a
fallback route can return `200` for unknown paths. Both a fallback response and
unexpected content need consideration; the note and byte count do not identify
the actual body. Request the relevant route/application evidence and preserved
response before asserting disclosure.

With `logging-gap`, the export retains **18** requests. The missing interval is
09:43:05–09:43:15 UTC. Only `HTTP-0017` and `HTTP-0021` remain for the third
source, so its variety rule no longer matches. The report retains the gap warning.
A learner can observe the missing interval; the triage report does not reconstruct
the omitted requests. “No rule matched, therefore no probing occurred” is not a
supported conclusion.

With `crawler-only`, **16** requests remain and only the volume prompt appears.
A false positive is a rule match that proves unrelated to the suspected security
problem after investigation. High volume warrants context, not an automatic
malicious label.
