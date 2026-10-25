# Practice in three passes

**Every dataset is SYNTHETIC. Independent mastery: NOT assessed.**

Use the same steps each time. Find the question and match its flow. Inspect the reply. Then state only what the saved packets support.

## Pass 1 — guided

Open the saved seed-37 capture beside the worked example. Follow the violet lookup with the name filter. Find its request and reply. Point to the reversed ports and matching ID. Then find the question type, response code and A answer. Work out 45 ms yourself from the frame times.

Explain aloud why `dns.id == 0x800f` shows two separate lookups. Finish the worksheet with the key at hand. Mark this pass “guided”. Even a perfect tool score is not work done without help.

## Pass 2 — hints only

Close the worked example and create a fresh worksheet:

```sh
python lab.py exercise --out run/worksheet-37-hints.json
```

Find three things: the NXDOMAIN reply, a repeat with no reply, and a repeat that gets an answer. Record the evidence. Work out the time from the first request. Use one hint at a time, and only when stuck:

1. A reply with an error code still counts as a reply. Check the DNS response flag before naming the failure.
2. Filter by the full question name. Compare the client and resolver addresses across the rows. Check the UDP ports, transaction ID and A question too.
3. A repeated question may get a reply later. Search the whole file before calling it unanswered.
4. Start timing at the first request for this exercise. Do not use the latest retry in its place.

```sh
python lab.py check --answers run/worksheet-37-hints.json
```

Write two limits without copying the example note. Ask a reviewer to test your wording. Why is “no visible reply” weaker than “the resolver failed”? Working with a file you have seen before is still rehearsal.

## Pass 3 — changed data, no key

Make a new case and worksheet. The example uses seed 91. A partner may choose a whole number from 0 to 2147483647 instead.

```sh
python lab.py generate --seed 91
python lab.py exercise --case run/case-91 --out run/worksheet-91-independent.json
```

Open `run/case-91/SYNTHETIC-dns.pcap`. Keep its manifest and the worked example closed. Names link to different outcomes in this case. DNS IDs, ports, answer addresses and times also differ. Do not reuse the seed-37 links between frames and names.

Fill in the five entries. Write a short note about what you saw. Alongside the checked fields, record the matching DNS ID and UDP ports. Where present, add the response code and returned address. Find the reused DNS ID. Explain how you told its two flows apart.

Before checking, think about where a reply could be missing. It might be absent at the resolver or only at the client. What extra evidence could tell those cases apart? Explain your reasoning. Do not start a real capture or contact a device.

```sh
python lab.py check --case run/case-91 --answers run/worksheet-91-independent.json
```

The tool checks packet facts only. Ask a person to review your explanation. They should ask you to find the evidence without the key. In your notes, record the seed, capture hash and help used. Add the score and reviewer feedback. This repository records no learner session or independent assessment. **Independent mastery remains NOT assessed** until there is separate evidence. Solving one small fixture without help does not prove broad real-network skill.
