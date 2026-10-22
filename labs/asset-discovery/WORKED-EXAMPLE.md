# Worked example: Asset discovery and inventory

Use this only after saving a first prediction for guided. It explains one case; matching it does not establish independent performance.

## Read, calculate, interpret

Start with the authorised scope, then match by IP rather than by a service label. `192.0.2.10` expects 443 and shows 443 open, so its observed and expected sets agree. `192.0.2.20` expects only 443 but shows 22 and 443 open: `{22,443} - {443} = {22}`. This produces `unapproved-service-observed`; it does not prove that port 22 is malicious. `192.0.2.30` appears up on port 80 but has no inventory record, so use `unregistered-host-observed` and request an ownership check. `192.0.2.40` is approved but absent from the XML, so use `not-observed-in-scan`. Do not describe it as decommissioned.

A suitable first handover sentence is: "The saved scan shows an unexpected open TCP port 22 on approved host 192.0.2.20; confirm its owner and purpose before changing it." Cite `data.approved[1]` and the matching XML host/port, then state that this snapshot cannot establish current state.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`, then reveal `python lab.py analyse --case run/attempt-01/case.json`. Compare decision fields and the reasoning. If a label differs, identify the exact missed input or rule; copying the reference label without explaining the change is not enough.

Keep a short correction in notes: "I first predicted __ because __. The evidence at __ changed that to __. I still cannot conclude __." A matching label can still have a mistaken explanation, so use the handover prompt with another person or teach it back aloud.
