# Worked example: Email identity and message triage

Save your first choices for guided before you read this page. It explains one case. A match does not prove that you can do a new case on your own.

## Read, calculate, interpret

First read the receiver trust register. It lists both notice-relay and invoice-relay for mx.receiver.test. For `notice`, SPF and DKIM pass for museum.test. That domain matches From. DMARC passes, and Reply-To and link domains match. Use `authenticated-domain-review-content`. This does not prove who the curator is or that the message is harmless.

For `invoice`, SPF passes for sender.test, while From is museum.test. That SPF result does not authenticate the From domain. DKIM fails and trusted DMARC fails. Use `domain-authentication-failed`. Keep the payments.test Reply-To and link differences in your note.

Check the request through a contact method you know from a separate source. Do not follow the supplied link to make this check. The lab sends no messages and resolves no URLs. Cite the message ID, trusted record ID and domains that differ. This lets someone check your reasons.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then view `python lab.py analyse --case run/attempt-01/case.json`. Compare the decision fields and reasons. If a label differs, find the exact input or rule you missed. Explain the change in your own words.

Keep a short note: "I first chose __ because __. The evidence at __ changed that to __. I still cannot conclude __." A label can match even if your reason is wrong. Use the handover questions with another person, or explain your choices aloud.
