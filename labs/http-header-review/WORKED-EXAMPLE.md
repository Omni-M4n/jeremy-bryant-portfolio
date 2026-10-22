# Worked example: HTTP headers and cookies

Use this only after saving a first prediction for guided. It explains one case; matching it does not establish independent performance.

## Read, calculate, interpret

`booking` is HTTPS. Its HSTS max-age equals the required 31536000 seconds, nosniff is present, frame-ancestors is none, private content has no-store, and the session cookie has Secure, HttpOnly and SameSite=Strict. Record `meets-supplied-requirements`. This describes the supplied policy only.

`account` sets HSTS max-age to zero, omits frame-ancestors, uses private instead of no-store, omits HttpOnly, and uses Lax where this application requires Strict. Its exact answer is `requirement-gaps:hsts-duration,frame-ancestors,cache-no-store,cookie-httponly,cookie-samesite`. Secure is present, so do not add a Secure gap.

In the written review, pair each proposed change with the requirement that motivates it. For example: "For account, add HttpOnly to the named session cookie because this application requires script access to be restricted." A production change would need compatibility testing; this lab changes no application.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`, then reveal `python lab.py analyse --case run/attempt-01/case.json`. Compare decision fields and the reasoning. If a label differs, identify the exact missed input or rule; copying the reference label without explaining the change is not enough.

Keep a short correction in notes: "I first predicted __ because __. The evidence at __ changed that to __. I still cannot conclude __." A matching label can still have a mistaken explanation, so use the handover prompt with another person or teach it back aloud.
