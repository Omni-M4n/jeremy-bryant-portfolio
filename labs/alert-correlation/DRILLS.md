# Drills: Alert deduplication and correlation

## Guided practice

Prepare guided in a fresh run folder, read the README rules, and make a prediction for every decision ID. Use WORKED-EXAMPLE.md only after saving that prediction. Correct your explanation in a different paragraph so the original reasoning remains visible.

## Prompts only

Close the worked example and use these questions to reconsider the evidence:

- Which record can be removed as a duplicate, and why?
- Would three failures at exactly the success timestamp count as earlier failures?

## Independent attempt

Prepare challenge in a fresh folder. Keep reference outputs, worked example and analyse closed until you have saved answers.json plus a five-sentence handover in notes.txt. Include the observation, interpretation, an alternative, uncertainty and next check. Use the README for syntax if needed and record that help. Afterwards run analyse/check and have a person inspect the explanation. Independent completion is unassessed unless someone actually reviews it.

## Changed case

Prepare changed. Predict which conclusions change and which do not. Explain the changed evidence before checking:

- Why do four deliveries of a1 count as only one failure?
- Why do alerts separated by host form different groups even at nearby times?

Small edit drill: In a copied challenge case, move a4 from 00:05:01Z to 00:05:00Z. Predict the effect of the inclusive 300-second boundary.

## Teach-back

Explain delivery count, unique-alert count, correlation-group count and confirmed-incident count as four different quantities. Use exact record IDs from your attempt. A partner should ask one counterexample rather than accepting a memorised label. Record the question and your response.

## Later recall

After 24-72 hours, reopen only your own notes and a fresh case. Write the central rule from memory, identify one boundary or missing-evidence condition and predict the result. Then check the documentation and record what you forgot. Do not count rereading an answer as an independent attempt.

## Handover

Keep the copied case, completed worksheet and notes together. State the scope, conclusion, two evidence references, unresolved uncertainty and requested next check. Include help used and whether someone assessed the reasoning. Do not claim experience beyond this fictional exercise.
