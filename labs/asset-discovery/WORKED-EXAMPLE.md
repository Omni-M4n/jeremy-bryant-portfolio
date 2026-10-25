# Worked example: Asset discovery and inventory

Save your first choices for guided before you read this page. It explains one case. A match does not prove that you can do a new case on your own.

## Read, calculate, interpret

Start with the approved scope. Match by IP, not by a service label. `192.0.2.10` expects 443 and shows 443 open. The observed and expected sets agree. `192.0.2.20` expects only 443 but shows 22 and 443 open. The difference is `{22,443} - {443} = {22}`. Use `unapproved-service-observed`. This does not prove that port 22 is used for harm.

`192.0.2.30` appears up on port 80 but has no inventory record. Use `unregistered-host-observed` and ask for an ownership check. `192.0.2.40` is approved but absent from the XML. Use `not-observed-in-scan`. Do not claim that the host was retired.

A first handover could say: "The saved scan shows an unexpected open TCP port 22 on approved host 192.0.2.20. Confirm its owner and purpose before changing it."

Cite `data.approved[1]` and the matching XML host/port. State that this snapshot cannot prove the current state.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then view `python lab.py analyse --case run/attempt-01/case.json`. Compare the decision fields and reasons. If a label differs, find the exact input or rule you missed. Explain the change in your own words.

Keep a short note: "I first chose __ because __. The evidence at __ changed that to __. I still cannot conclude __." A label can match even if your reason is wrong. Use the handover questions with another person, or explain your choices aloud.
