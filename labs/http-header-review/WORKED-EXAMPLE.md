# Worked example: HTTP headers and cookies

Save your first guided answer before reading this page. This explains one case. Matching it does not show that you can solve a fresh case.

## Read, calculate, interpret

`booking` uses HTTPS. Its HSTS max-age is the required 31536000 seconds. It has nosniff, and frame-ancestors is none. Its private content has no-store. The session cookie has Secure, HttpOnly and SameSite=Strict. Record `meets-supplied-requirements`. This describes the supplied policy only.

`account` sets HSTS max-age to zero. It has no frame-ancestors rule. It uses private instead of no-store. Its cookie lacks HttpOnly and uses Lax where this app requires Strict. Use the exact answer `requirement-gaps:hsts-duration,frame-ancestors,cache-no-store,cookie-httponly,cookie-samesite`. Secure is present, so there is no Secure gap.

In your note, link each proposed change to the rule that calls for it. For example: "Add HttpOnly to account's named session cookie. This app requires a limit on script access to that cookie." A real change would need tests for valid app use too. This lab changes no app.

## Check and revise

Run `python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json`. Then reveal `python lab.py analyse --case run/attempt-01/case.json`. Compare your reasons as well as the labels. If one differs, find the exact input or rule you missed. Explain the change in your own words.

Keep this note: "I first predicted __ because __. The evidence at __ changed that to __. I still cannot conclude __." A matching label can have the wrong reason. Ask someone to check your explanation, or practise saying it aloud.
