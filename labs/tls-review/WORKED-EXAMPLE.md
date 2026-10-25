# Worked example: TLS certificate review

Save your first guided answer before reading this page. This explains one case. Matching it does not show that you can solve a fresh case.

## Read, calculate, interpret

Use the fixed time 2030-01-11 00:00:00 UTC. The renewal threshold is 14 days: 14 x 86400 = 1209600 seconds. `gallery` expires on 2030-03-01. That leaves 49 days, or 4233600 seconds. Its SAN name matches the host. The supplied chain report says verified. Use `fields-and-reported-chain-pass`. The word "reported" matters: you did not check a real chain here.

`archive` expires on January 21. It has 10 days left: 10 x 86400 = 864000 seconds. This is within the threshold, so use `renewal-due`.

`kiosk` expired at 2030-01-10 23:59:59. That is one second before the fixed check time. Its chain is also unverified. Keep both findings as `expired|chain-unverified`.

In your note, name the host and time checked. Show the SAN match and time left. If trust needs to be proved, request a check by a real client. These records do not show that all HTTPS use is safe.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then reveal `python lab.py analyse --case run/attempt-01/case.json`. Compare your reasons as well as the labels. If one differs, find the exact input or rule you missed. Explain the change in your own words.

Keep this note: "I first predicted __ because __. The evidence at __ changed that to __. I still cannot conclude __." A matching label can have the wrong reason. Ask someone to check your explanation, or practise saying it aloud.
