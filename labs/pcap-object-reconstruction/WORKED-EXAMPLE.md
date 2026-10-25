# Worked example: Collection 01

Read this after you save your first prediction and your own account of the task results. It explains only the guided made-up case. For your real capture, keep the separate evidence listed in LOCAL-CAPTURE.md.

Collection 01 carries alpha plus a newline: six bytes. Offsets 0-2 and 3-5 cover all positions once. Once joined, the bytes have the same hash as the known six-byte object.

## Walk through the evidence

- Body positions present=6/6; missing=0; conflicting positions=0; encrypted=False.

Check each number or pair of values in `fixtures/guided.json`. The output label is not proof on its own. The fields and records must support it.

## Guided decision fields

- `stream`: `complete-matches-known-object`.

Explain how the values you found support these choices. Then add a limit: the script made this PCAP. It was not collected from a network. The parser handles one small plain HTTP/1.1 response. It has Content-Length, fixed IPv4/TCP headers and no TLS.

## Connect it to the operation

Write your prediction before you run the guided task. In the saved task folder, read output/packet-log.json. Count positions in the body, not packets. Check for missing positions and overlaps that conflict. Then compare the exported hash. The exported start of the body may be shorter than Content-Length, its stated size. The source PCAP was made for training. Save your own explanation before you open output/feedback.json and receipt.json. Then compare the source-before and source-after SHA-256 values in the receipt. These values were measured from the generated data. The worksheet uses a made-up example. Keep any differences. Do not change the evidence to make it agree.

## Handover prompt

“I checked these item IDs and saved these files. These values support my choice. This evidence cannot show ____. To check that, I would need ____. I have done the guided stage. My ability to explain a new case still needs review.”
