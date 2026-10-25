# Flow notebook 1: worked example

f01 sends client bytes 1000 through 1099. Its half-open range is [1000,1100). f02 shows the same range at 200 ms. Save `repeated-range-observed`. A retry is possible, but this extract does not rule out duplicate recording or show where any packet was lost.

f03 acknowledges 1100 at 210 ms. All bytes up to that point appear in the extract, so use `no-unseen-ack-in-extract`. f04 starts the server response at 220 ms. The observed interval after the complete request acknowledgement is `220 - 210 = 10 ms`, giving `request-ack-to-response:10ms`. Do not call that the request's whole delay or an RTT.

No reset is listed, so use `no-reset-in-extract`. The capture counter is zero: `no-local-drops-reported`. That does not prove that every relevant packet passed this collection point. A useful next check is the sender's capture or log, obtained within the same owned lab, to distinguish a real resend from duplicate collection.
