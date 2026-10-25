# Worked example: seed 53, mixed

Try your own explanation first. This is a supplied reference answer. It is not a record of Jeremy completing an investigation without help.

## Establish scope

```sh
python lab.py check
python lab.py timeline
python lab.py triage --output runs/worked-report.json
python lab.py check --report runs/worked-report.json
```

The export has **21** made-up requests for `practice-library-053.test`. Its collection interval is **2032-06-14 09:39:00–09:44:00 UTC**, including both endpoints. It records three source addresses. `complete-for-fixture` confirms that the generator exported what it planned. It says nothing about real-world log coverage. The future dates are made up. The CSV rows are shuffled. Use the sorted timeline.

## Compare the sources

| Source | Evidence | Interpretation and next check |
| --- | --- | --- |
| `192.0.2.65` | 4 requests, `HTTP-0001`–`HTTP-0004`; three `GET` responses of `200`, then `POST /contact` with `303` | Compatible with ordinary browsing and a form redirect. The absent redirect header and request body limit further interpretation. |
| `198.51.100.126` | 12 requests, `HTTP-0005`–`HTTP-0016`, 09:42:00–09:42:11; eleven `GET`, one `HEAD`; nine `200`, three `404`; no watched path | The volume rule matches. Public pages, stale guide paths and the scheduled-job note support a crawler explanation. Confirm the job's timing and requests before treating the note as verified. |
| `203.0.113.138` | 5 requests, `HTTP-0017`–`HTTP-0021`, 09:43:00–09:43:20; four different watched paths, then `POST /login` | Watched-path variety matches despite lower volume. Requests for configuration, administration, backup and debug paths make probing plausible. Check authorisation and corresponding application records. |

The default volume setting is **8**. The watched-path variety setting is **3**. The report has **two review prompts**. One concerns volume; the other concerns path variety. They are questions for review. They do not prove two incidents.

For the third source, trace each watched path:

| Event | Requested path | Status |
| --- | --- | --- |
| `HTTP-0017` | `/.env` | `404` |
| `HTTP-0018` | `/admin` | `403` |
| `HTTP-0019` | `/backup.zip` | `404` |
| `HTTP-0020` | `/debug` | `404` |

These are the paths and outcomes this logging component saw. They do not prove code ran, file contents were exposed or an account was accessed.

`HTTP-0021` is `POST /login` with status `200`. It records a 470-byte response body. The export has neither that body nor an authentication result. The response might just show the form again. “The attacker logged in successfully” goes beyond this evidence.

Both the crawler and the watched-path source claim user-agent `PracticeCrawler/1.0`. The client supplies that text. It does not prove they share an actor. The owner's scheduled-job note applies to one source. Matching labels do not make it apply to the other.

## Example handover

> Review requests from 203.0.113.138 to practice-library-053.test. The time span is 2032-06-14 09:43:00–09:43:20 UTC. HTTP-0017 through HTTP-0020 contain four distinct watched paths. This exceeds the set threshold of three. Probing is one possible cause. An authorised test is another. HTTP-0021 records a 200 response to POST /login. No authentication outcome is available. Check the records of authorised tests. Match the five event times to app routing and authentication records. This export alone cannot prove disclosure or compromise. Also check the scheduled crawler note for 198.51.100.126 against other evidence. Do this before closing its volume prompt.

This handover names the evidence and the doubts. It asks for facts that could change the decision. It does not suggest blocking an address just because it sent the most requests.

## How the answer changes

With the same seed and `soft-200`, `HTTP-0017` changes to `200` with 128 body bytes. A third prompt, `watched-path-200`, appears. The new note says a fallback route can return `200` for unknown paths. A fallback response and unexpected content are both possible. The note and byte count cannot identify the actual body. Request the relevant route/app evidence and saved response. Do this before claiming data was disclosed.

With `logging-gap`, the export keeps **18** requests. The missing interval is 09:43:05–09:43:15 UTC. Only `HTTP-0017` and `HTTP-0021` remain for the third source. Its variety rule no longer matches. The report keeps the gap warning. You can see that an interval is missing. The triage report does not rebuild the lost requests. “No rule matched, therefore no probing occurred” is not supported.

With `crawler-only`, **16** requests remain. Only the volume prompt appears. A false positive starts with a rule match. Further review shows it is unrelated to the suspected security problem. High volume needs context. It does not automatically mean harm.
