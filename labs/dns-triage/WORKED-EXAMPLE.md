# Worked example: guided seed 37

**SYNTHETIC practice. This is an answer explanation, not evidence of learner completion.**

Use `fixtures/guided/SYNTHETIC-dns.pcap`. Other seeds give different evidence. Start with the first question. Try the worksheet before reading the full key.

## One question, carefully matched

Apply `dns.qry.name == "synthetic-violet.test"`. Check these fields in the first two frames:

| Field | Frame 1 | Frame 2 |
| --- | --- | --- |
| Direction | From `192.0.2.10:60341` to `192.0.2.53:53` | The endpoints are reversed |
| Question | Asks for an A record | Same question |
| DNS transaction ID | `0x800f` (32783) | Same ID |
| Reply | This is the request | Code 0; an A address in the answer section |

These facts support the label `answer`. They do not prove that an app connected to that address. Frame 2 comes 0.045 seconds after frame 1. In milliseconds, that is `0.045 × 1000 = 45`.

The worksheet entry becomes:

```json
{
  "client": "192.0.2.10",
  "qname": "synthetic-violet.test",
  "request_frames": [1],
  "response_frames": [2],
  "outcome": "answer",
  "first_response_ms": 45,
  "explanation": "Frame 2 reverses frame 1's endpoints and matches its DNS ID and A question. It contains an A answer. This does not show an application connection."
}
```

Now apply `dns.id == 0x800f`. Frames 6 and 7 also appear. Their name is `synthetic-maple.test`. Their client is different: `192.0.2.11:62186`. They share the same 16-bit ID. That does not make them replies to frame 1.

## Full evidence key — spoilers

The interval below always starts at the **first** request in the episode.

| Question | Client | Request frames | Reply frames | Outcome | First-request interval |
| --- | --- | --- | --- | --- | --- |
| `synthetic-violet.test` | `192.0.2.10` | 1 | 2 | `answer` | 45 ms |
| `synthetic-meadow.test` | `192.0.2.11` | 3 | 4 | `nxdomain` | 48 ms |
| `synthetic-orchard.test` | `192.0.2.10` | 5, 9 | none | `unanswered` | `null` |
| `synthetic-maple.test` | `192.0.2.11` | 6 | 7 | `answer` | 24 ms |
| `synthetic-lantern.test` | `192.0.2.10` | 8, 10 | 11 | `answer` | 1511 ms |

Frame 4 is a reply with RCODE 3 (NXDOMAIN). The reply is present. It says the name does not exist. This made-up file cannot confirm that claim from another source.

Frames 5 and 9 repeat the orchard question. They have the same client port and ID. No matching reply exists in the file. Record one unanswered episode with two seen requests. Do not turn that into “the firewall blocked it”. This capture cannot show why the reply is absent.

Frames 8 and 10 repeat the lantern question. Frame 11 gives a matching A answer. The first request is at 0.800 seconds. The reply is at 2.311 seconds. The gap is `(2.311 - 0.800) × 1000 = 1511` ms. The retry is at 1.800 seconds. Timing from that retry would give 511 ms. The worksheet asks for the time from the first request. Matching IDs cannot tell us which request caused the reply.

## Example observation note

“This made-up file has 11 packets. Three question episodes have A answers. One has an NXDOMAIN reply. One has no visible reply. The lantern episode has a repeat request. Its answer comes 1511 ms after the first request. The orchard episode repeats with no visible answer. This does not prove packet loss or app success. It does not identify a faulty device.”

Copying this key can check the software and your grasp of the format. It does not prove independent mastery. That remains **NOT assessed**.
