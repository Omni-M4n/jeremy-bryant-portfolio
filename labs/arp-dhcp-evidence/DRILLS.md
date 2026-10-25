# Exchange practice with fewer prompts

Use a fresh `run/attempt-NN` for every pass. Record date, Python version, case ID, prediction, evidence, help used and correction. Preserve the first worksheet before running `check`; it reveals reference labels for differences. Stages describe observed work, for example "guided with prompts" or "independent attempt awaiting review". A passing utility does not assess mastery.

## Guided: 30-45 minutes

Prepare `guided` using the README. Draw one timeline with DHCP and ARP frame numbers. For each claimed link, underline the exact matching fields. Write the result and its limit before opening the worked example. After comparison, retain the original answer and explain any correction.

## Prompts only: 15 minutes

Prepare `guided` in a fresh folder and close the worked example. Use these prompts: Which client and xid am I following? What does the Request say about the client address? Which server/address should a reply match? Which address is ARP seeking? To whom is the reply addressed? Does the frame order support the proposed relationship? Save the completed table before checking.

## Independent: 20-30 minutes

Prepare `challenge`. Close worked solutions, reference files, tests and previous answers. Use only its evidence, the README's model rules and a blank table. Classify each query, identify all relevant and excluded frames, and explain at least one unresolved question without inventing a missing event. Complete every `-lease-link` entry separately from the ARP exchange result. Save first; check and request human review afterwards. No case-specific answers are supplied in this drill.

## Changed observations: 20-30 minutes

Prepare `changed`. Do not carry a label forward just because a message name looks familiar. Determine the request form from its fields, correlate the required identifiers, and record the evidence for each excluded packet. Explain what the excerpt's end time and observation point do and do not establish. Save a new first attempt before checking. No lease release/renewal, adapter edit or network transmission is required.

## Teach-back: 5-10 minutes

Explain why a DHCP Request can be meaningful without a preceding Discover/Offer in the same attempt. Explain why xid alone is insufficient here, how you match an ARP reply, and why a correctly matched pair does not prove the sender's ownership. Have a reviewer point to one frame and ask which conclusion it supports and which it cannot support. Keep the questions and corrections.

## Later recall

On another day, write the minimum fields you would compare for DHCP, ARP and the link between them before looking at notes. About a week later, ask a reviewer to choose an unfamiliar excerpt from your authorised saved lab material, or verbally remove one observation from a supplied case. Predict which conclusions remain supported and justify the difference. Keep the exercise offline; do not create real missing-message conditions. Record uncertainty and help honestly, then compare with a reviewer rather than assuming the fixture checker covers the new scenario.
