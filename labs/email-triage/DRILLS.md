# Drills: Email identity and message triage

## 1. Guided evidence pass

Prepare guided as `run/attempt-01`. Keep WORKED-EXAMPLE closed initially. Read the question, mark scope and evidence sources, then fill every decision and a short explanation. Use the vocabulary if needed and record that help. Allow 30-45 minutes for this first pass.

## 2. Fewer prompts

Work through these questions before opening the analysis:

- Which record IDs are trusted independently of the message?
- Which domain does the SPF result refer to?
- Does a domain-authentication result say anything conclusive about the human author or requested action?

Check decisions, read the worked example and write one correction with its evidence reference. If every label matched, still explain the hardest choice; a lucky label is not evidence of understanding.

## 3. Independent case

Prepare challenge in a fresh folder. Evaluate each message using the trusted receiving evidence and stated context. Separate observed identity checks from conclusions about intent. Keep reference outputs, the worked example and analyse closed until your decisions, evidence references and handover are saved. Use the README for syntax or vocabulary if needed and record that help. Afterwards, compare results and have another person assess the reasoning. A matching label alone does not establish understanding.

## 4. Changed conditions

Prepare changed separately and compare its evidence with guided; keep both attempts. Predict each result before revealing analysis.

- Why is inserted-header unverified even though it claims mx.receiver.test?
- What does a valid result for museum-billing.test establish when the expected sender is museum.test?
- What further evidence would distinguish an authorised sender service from impersonation?

Write which fact changed, why the relevant rule changed or did not change, and what remains uncertain. Do not edit the shipped fixture or reference files to make an answer match.

## 5. Teach-back

Explain the receiver trust boundary, the difference between SPF and From, and why domain authentication never guarantees safe content. Use one record ID and a counterexample. If you need the worked example, say so in the help-used note, then try again later with it closed.

## 6. Later recall

Two days later, sketch one aligned SPF example, one aligned DKIM example with SPF failure, and one forged untrusted Authentication-Results claim. Check each against the decision vocabulary. Record the date, what you recalled unaided, what you checked and one remaining question. This is a practice record, not a claim of complete real-world competence.

## Handover

Submit your own saved worksheet and a short note answering: "What is observed, where is the evidence, what is uncertain, and what should be checked next?" Include initial prediction, correction and help used. No upload or publication is part of this lab.
