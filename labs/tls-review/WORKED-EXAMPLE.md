# Worked example: TLS certificate review

Use this only after saving a first prediction for guided. It explains one case; matching it does not establish independent performance.

## Read, calculate, interpret

The evaluation time is 2030-01-11 00:00:00 UTC and the renewal threshold is 14 x 86400 = 1209600 seconds. `gallery` expires on 2030-03-01, 49 days or 4233600 seconds later. Its SAN matches and its supplied chain report says verified, so use `fields-and-reported-chain-pass`. The phrase "reported" is part of the result for a reason.

`archive` expires on January 21, leaving 10 x 86400 = 864000 seconds, within the threshold: `renewal-due`. `kiosk` expired at 2030-01-10 23:59:59, one second before evaluation. Its chain is also unverified, so retain both findings as `expired|chain-unverified`.

A useful handover says which host and timestamp were checked, lists the SAN match and remaining time, and requests real client validation if trust must be established. Do not report that HTTPS is generally safe.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`, then reveal `python lab.py analyse --case run/attempt-01/case.json`. Compare decision fields and the reasoning. If a label differs, identify the exact missed input or rule; copying the reference label without explaining the change is not enough.

Keep a short correction in notes: "I first predicted __ because __. The evidence at __ changed that to __. I still cannot conclude __." A matching label can still have a mistaken explanation, so use the handover prompt with another person or teach it back aloud.
