# Worked example: Email identity and message triage

Use this only after saving a first prediction for guided. It explains one case; matching it does not establish independent performance.

## Read, calculate, interpret

First read the receiver trust register. Both notice-relay and invoice-relay are listed for mx.receiver.test. For `notice`, SPF and DKIM pass for museum.test, which matches From; DMARC passes, and Reply-To/link domains match. Use `authenticated-domain-review-content`. Do not translate that into "the curator is verified" or "the message is harmless".

For `invoice`, SPF passes for sender.test, while From is museum.test. That SPF result does not authenticate the From domain. DKIM fails and trusted DMARC fails. Use `domain-authentication-failed`; also retain the payments.test Reply-To and link differences in the note.

A useful next check is to confirm the claimed request using an independently known channel, without following the supplied link. The lab sends no messages and resolves no URLs. Cite the message ID, trusted record ID and differing domains so the reasoning is auditable.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`, then reveal `python lab.py analyse --case run/attempt-01/case.json`. Compare decision fields and the reasoning. If a label differs, identify the exact missed input or rule; copying the reference label without explaining the change is not enough.

Keep a short correction in notes: "I first predicted __ because __. The evidence at __ changed that to __. I still cannot conclude __." A matching label can still have a mistaken explanation, so use the handover prompt with another person or teach it back aloud.
