# Practice in three passes

**Every dataset is SYNTHETIC. Independent mastery: NOT assessed.**

Use the same reasoning each time: identify the question, match the flow, inspect the response, then describe only what the retained packets support.

## Pass 1 — guided

Open the retained seed-37 capture and the worked example side by side. Reproduce the violet lookup using the name filter. Point to its request, reply, reversed ports, matching ID, question type, response code and A answer. Calculate 45 ms yourself from the frame times.

Then explain aloud why `dns.id == 0x800f` displays two separate lookups. Finish the worksheet with the key available. Mark this pass “guided”; even a perfect automated score is not independent work.

## Pass 2 — hints only

Close the worked example and create a fresh worksheet:

```sh
python lab.py exercise --out run/worksheet-37-hints.json
```

Find the NXDOMAIN reply, the repeated question with no visible reply, and the repeated question that eventually receives an answer. Record the evidence and compute the first-request interval. Use hints one at a time only when stuck:

1. A reply with an error code still counts as a reply. Inspect the DNS response flag before naming the failure.
2. Filter by the full question name. Compare client/resolver addresses, UDP ports, transaction ID and A question across the resulting rows.
3. A repeated question may have an eventual reply. Search the entire file before deciding an episode is unanswered.
4. Timing begins at the first request for this exercise. Do not silently substitute the most recent retry.

```sh
python lab.py check --answers run/worksheet-37-hints.json
```

Write two limitations without copying the example note. Have a reviewer ask why “no visible reply” is weaker than “the resolver failed.” Revisiting a dataset you have already seen remains rehearsal.

## Pass 3 — changed data, no key

Generate a new case and worksheet. The example uses seed 91; a partner may choose another nonnegative integer up to 2147483647.

```sh
python lab.py generate --seed 91
python lab.py exercise --case run/case-91 --out run/worksheet-91-independent.json
```

Open `run/case-91/SYNTHETIC-dns.pcap`. Keep its manifest and the worked example closed. The names associated with each outcome, DNS IDs, ports, answer addresses and timings differ from the guided case. Do not reuse seed-37 frame/name associations.

Complete the five entries and write a short observation note. In addition to the checked fields, record the matching DNS ID, UDP ports, response code and returned address where applicable. Identify the reused DNS ID and explain how you separated its two flows.

Before checking, explain what extra observations might distinguish an absent reply at the resolver from an absent reply only at the client. This is a reasoning question; do not start a real capture or contact a device.

```sh
python lab.py check --case run/case-91 --answers run/worksheet-91-independent.json
```

The automated result checks packet facts only. A person should review the explanation and ask you to find the evidence again without the answer key. Record the seed, capture hash, assistance used, score and reviewer feedback in your own practice notes. No learner session or independent assessment is recorded by this repository; **independent mastery remains NOT assessed** until separately evidenced. Even an independently solved small fixture does not demonstrate competence across real networks.
