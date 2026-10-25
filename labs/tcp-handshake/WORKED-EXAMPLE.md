# Worked example: TCP handshake investigation

Save your first choices for guided before you read this page. It explains one case. A match does not prove that you can do a new case on your own.

## Read, calculate, interpret

For `gallery`, frame 1 has SYN sequence 1000. The next client number is 1001. Frame 2 has server sequence 9000 and ACK 1001. The next server number is 9001. Frame 3 has client sequence 1001 and ACK 9001. All three events support `handshake-observed`.

For `archive`, frame 4 has SYN 2000. Frame 5 is RST-ACK with ACK 2001. Record `reset-observed`. The sender or a device on the path could cause a reset. This excerpt cannot prove the cause.

For `catalogue`, frames 6 and 8 have the same SYN sequence 3000. There is no server response in the excerpt. Use `no-response-observed`. Do not turn that finding into "the firewall blocked it".

Record frame IDs and your sums before opening the set answer. You could state this limit: "The excerpt may miss a server response. We do not know if the capture is complete."

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then view `python lab.py analyse --case run/attempt-01/case.json`. Compare the decision fields and reasons. If a label differs, find the exact input or rule you missed. Explain the change in your own words.

Keep a short note: "I first chose __ because __. The evidence at __ changed that to __. I still cannot conclude __." A label can match even if your reason is wrong. Use the handover questions with another person, or explain your choices aloud.
