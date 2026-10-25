# Drills: Small SSH server configuration review

## Guided practice

Prepare guided in a new run folder. Read the rules and predict each decision. Save your answer before opening WORKED-EXAMPLE.md. Add any correction in a new paragraph. Keep your first answer.

## Prompts only

Close the worked example. Try these questions:

- Why does prohibit-password differ from no for root login?
- PasswordAuthentication is no. Is that enough to rule out every other password-like login method? Explain the missing checks.

## Independent attempt

Prepare challenge in a fresh folder. Keep all answers and analyse output closed. Save answers.json and a short note in notes.txt. State a fact, your view of it, another possible explanation, a limit and a next check. Use the README for syntax if needed. Record that help. Then run analyse and check. Ask someone to review your reasons. Until then, the attempt is not independently assessed. A case you have already read is repeat practice, not an unseen test.

## Changed case

Prepare changed. Predict each result and show the facts before checking:

- Which of the six settings match the baseline now? Which, if any, differ?
- What can this text show about a working login? What would need a real test?

Copy challenge into a new attempt. Move PermitRootLogin no before PermitRootLogin yes. Predict all decisions from the new order. Explain which rules apply. Do not change the original file.

## Teach-back

Explain why the first value is used. Show why an unsupported Match or Include stops this small tool. Use exact IDs from your case. Ask a partner to change one fact and challenge your answer. Save the question and your reply.

## Later recall

After 24–72 hours, use your notes and a fresh case. Recall the main rule. Name one boundary or missing fact, then predict the result. Check the rules and record what you forgot. Rereading an answer is not a fresh attempt.

## Handover

Keep the case, worksheet and notes together. State the scope, conclusion, two evidence references, a limit and the next check. Include help used and whether someone reviewed your reasons. Describe only the practice you actually did.
