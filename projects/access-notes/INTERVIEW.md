# Explaining Access Notes honestly

Current status: a working reference project and practice exercises are prepared. Personal implementation practice and an unaided explanation are pending. This is a learning project, not professional security experience or evidence of independent authorship.

## Before completing the practice

An accurate introduction is:

> I have a local notes application prepared for practising web security. It separates two fictional users' notes and includes regression tests for ownership, CSRF, session revocation, escaping and SQL injection input. I am working through the code and independent exercises before presenting it as my own implementation experience.

Do not claim you built the whole app independently, performed a penetration test, or established that it is secure in production.

## After doing the work

Replace the brackets with completed actions and evidence; do not use this script until you can demonstrate them:

> I used a small local Flask notes app to practise authentication and authorisation. I traced [specific request], independently changed [specific behaviour], and verified it with [specific tests]. The key access rule is that every note read, edit and delete is scoped to the authenticated user's ID. I can show why a forged owner field or another user's note ID does not grant access. It remains a local demo with public fictional credentials and several production controls out of scope.

Keep your original change, test result and a short explanation available. Say which parts were supplied and which you implemented.

## A short demonstration

1. Show a note as Alex and explain how the server obtains Alex's identity.
2. Switch to Sam and request the same note URL. Explain the owner-scoped query and `404`.
3. Run the cross-user and logout-replay tests. Explain the attempted action, the expected denial and the unchanged data.
4. Show your independently completed change and the test that verifies it.
5. State the local-only limitations without treating a passing suite as a complete security assessment.

## Questions to practise aloud

| Question | Points to explain in your own words |
| --- | --- |
| Authentication versus authorisation? | The password identifies an account; each object access still needs an ownership check. |
| Why not send `user_id` in a hidden field? | A browser can change hidden fields. Identity comes from the server-side session, and the session token is opaque. |
| Why check both ID and owner in SQL? | Knowing an object ID is not permission to read or change that object. |
| Why parameterised SQL? | Values are bound as data. Placeholders do not decide which user's rows are allowed. |
| How does logout work? | Delete the server-side session record and expire the cookie. A copied old token can no longer authenticate. |
| Why CSRF plus same-site cookies? | Cookies are sent by browsers automatically; a form token and origin validation provide explicit request checks. Login and logout are included. |
| Why escape output? | Stored text must remain text when inserted into HTML. Jinja supplies escaping, and the templates avoid marking note text safe. |
| Is hashing encryption? | Password verification uses a one-way, salted password hash. Notes remain plaintext in SQLite. |
| What would hosting require? | Revisit authentication, known demo credentials, HTTPS/cookie settings, server choice, rate limits, secrets, operational logging and a broader threat model. This reference app is not a deployment template. |

If you cannot explain a helper or test, say so and use it as the next practice task. Specific completed work is stronger evidence than a long list of security terms.
