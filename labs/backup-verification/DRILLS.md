# Drills: Backup scope, freshness and synthetic restore verification

## Guided practice

Prepare guided in a fresh run folder, read the README rules, and make a prediction for every decision ID. Use WORKED-EXAMPLE.md only after saving that prediction. Correct your explanation in a different paragraph so the original reasoning remains visible.

## Prompts only

Close the worked example and use these questions to reconsider the evidence:

- What does a matching hash establish, and what does it leave untested?
- Why can a complete, intact copy still fail an RPO check?

## Independent attempt

Prepare challenge in a fresh folder. Keep reference outputs, worked example and analyse closed until you have saved answers.json plus a five-sentence handover in notes.txt. Include the observation, interpretation, an alternative, uncertainty and next check. Use the README for syntax if needed and record that help. Afterwards run analyse/check and have a person inspect the explanation. Independent completion is unassessed unless someone actually reviews it.

## Changed case

Prepare changed. Predict which conclusions change and which do not. Explain the changed evidence before checking:

- Which file in b1 fails byte comparison?
- Why is b0 still not a qualifying fallback even when its hashes match?

Small edit drill: In a copied guided case, change b1 captured_at to 2026-02-01T08:00:00Z, then to 07:59:59Z. Predict the inclusive RPO boundary before running analysis.

## Teach-back

Explain freshness, scope, retention, byte integrity and application usability as separate checks, and distinguish RPO from RTO. Use exact record IDs from your attempt. A partner should ask one counterexample rather than accepting a memorised label. Record the question and your response.

## Later recall

After 24-72 hours, reopen only your own notes and a fresh case. Write the central rule from memory, identify one boundary or missing-evidence condition and predict the result. Then check the documentation and record what you forgot. Do not count rereading an answer as an independent attempt.

## Handover

Keep the copied case, completed worksheet and notes together. State the scope, conclusion, two evidence references, unresolved uncertainty and requested next check. Include help used and whether someone assessed the reasoning. Do not claim experience beyond this fictional exercise.
