# Worked example: guided seed 37

**SYNTHETIC practice. This is an answer explanation, not evidence of learner completion.**

Use `fixtures/guided/SYNTHETIC-dns.pcap`. Other seeds produce different evidence. Start with the first question, then use the full key only after attempting the worksheet.

## One question, carefully matched

Apply `dns.qry.name == "synthetic-violet.test"`. Frame 1 asks for an A record from `192.0.2.10:60341` to `192.0.2.53:53`. Its DNS transaction ID is `0x800f` (32783). Frame 2 reverses those endpoints and repeats the same question and ID. The response has code 0 and an A address in its answer section.

That is sufficient to label this episode `answer`. It does not prove an application subsequently connected to the returned address. Frame 2 occurs 0.045 seconds after frame 1: `0.045 × 1000 = 45` milliseconds.

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

Now apply `dns.id == 0x800f`. Frames 6 and 7 also appear. They concern `synthetic-maple.test` and the other client, `192.0.2.11:62186`. Reusing the same 16-bit ID does not make them replies to frame 1.

## Full evidence key — spoilers

The interval below always starts at the **first** request in the episode.

| Question | Client | Request frames | Reply frames | Outcome | First-request interval |
| --- | --- | --- | --- | --- | --- |
| `synthetic-violet.test` | `192.0.2.10` | 1 | 2 | `answer` | 45 ms |
| `synthetic-meadow.test` | `192.0.2.11` | 3 | 4 | `nxdomain` | 48 ms |
| `synthetic-orchard.test` | `192.0.2.10` | 5, 9 | none | `unanswered` | `null` |
| `synthetic-maple.test` | `192.0.2.11` | 6 | 7 | `answer` | 24 ms |
| `synthetic-lantern.test` | `192.0.2.10` | 8, 10 | 11 | `answer` | 1511 ms |

Frame 4 is a reply with RCODE 3 (NXDOMAIN), not a missing response. The defensible statement is that the resolver's reply reports the name as nonexistent. This constructed file does not independently validate that claim.

Frames 5 and 9 repeat the same orchard question, client port and ID. No matching response exists in the file. Record one unanswered episode with two observed requests. Do not convert that into “the firewall blocked it”; this capture cannot identify why the reply is absent.

Frames 8 and 10 repeat the lantern question. Frame 11 supplies a matching A answer. The first request is at 0.800 seconds and the response at 2.311 seconds: `(2.311 - 0.800) × 1000 = 1511` ms. Measured from the repeated request at 1.800 seconds, the interval would be 511 ms, but that is not the worksheet's requested measure. The matching identifiers do not reveal which request caused the reply.

## Example observation note

“Within this synthetic 11-packet file, three question episodes have A answers, one has an NXDOMAIN reply, and one has no visible reply. The lantern episode includes a repeated request followed by an answer 1511 ms after its first request. The orchard episode repeats without a visible answer. This evidence does not establish packet loss, application success, or a particular faulty device.”

Copying this key can check the software and your understanding of the format. It does not establish independent mastery, which remains **NOT assessed**.
