# Worked example: TCP handshake investigation

Use this only after saving a first prediction for guided. It explains one case; matching it does not establish independent performance.

## Read, calculate, interpret

For `gallery`, frame 1 has SYN sequence 1000. The next client number is 1001. Frame 2 has server sequence 9000 and acknowledges 1001. The next server number is 9001. Frame 3 carries client sequence 1001 and acknowledgement 9001, so all three events support `handshake-observed`.

For `archive`, frame 4 has SYN 2000 and frame 5 is RST-ACK acknowledging 2001. Record `reset-observed`; the sender or an intermediary could explain a reset, and this excerpt cannot establish the cause. For `catalogue`, frames 6 and 8 contain the same SYN sequence 3000 with no server response. Use `no-response-observed`. Do not turn that observation into "the firewall blocked it".

Record frame IDs with the arithmetic before opening the reference output. An example limitation is: "The excerpt may omit a server response because capture completeness is not guaranteed."

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`, then reveal `python lab.py analyse --case run/attempt-01/case.json`. Compare decision fields and the reasoning. If a label differs, identify the exact missed input or rule; copying the reference label without explaining the change is not enough.

Keep a short correction in notes: "I first predicted __ because __. The evidence at __ changed that to __. I still cannot conclude __." A matching label can still have a mistaken explanation, so use the handover prompt with another person or teach it back aloud.
