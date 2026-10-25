# Drills: HTTP headers and cookies

## 1. Guided evidence pass

Prepare guided as `run/attempt-01`. Keep WORKED-EXAMPLE closed initially. Read the question, mark scope and evidence sources, then fill every decision and a short explanation. Use the vocabulary if needed and record that help. Allow 30-45 minutes for this first pass.

## 2. Fewer prompts

Work through these questions before opening the analysis:

- Which requirements apply to every response, and which depend on response context?
- Are Secure and HttpOnly answering the same question?
- Why does private not satisfy the supplied no-store requirement?

Check decisions, read the worked example and write one correction with its evidence reference. If every label matched, still explain the hardest choice; a lucky label is not evidence of understanding.

## 3. Independent case

Prepare challenge in a fresh folder. Review each response and cookie against the fictional application requirements. Prioritise specific changes and explain which legitimate behaviour must remain. Keep reference outputs, the worked example and analyse closed until your decisions, evidence references and handover are saved. Use the README for syntax or vocabulary if needed and record that help. Afterwards, compare results and have another person assess the reasoning. A matching label alone does not establish understanding.

## 4. Changed conditions

Prepare changed separately and compare its evidence with guided; keep both attempts. Predict each result before revealing analysis.

- Does an HSTS field on an HTTP response satisfy HTTPS delivery?
- Why can the public non-HTML feed satisfy its requirements without CSP, a session cookie or no-store?
- Would adding every header everywhere prove the application safe? Explain the evidence limit.

Write which fact changed, why the relevant rule changed or did not change, and what remains uncertain. Do not edit the shipped fixture or reference files to make an answer match.

## 5. Teach-back

Explain one response-specific requirement and why a header name alone does not establish its intended effect. Use one record ID and a counterexample. If you need the worked example, say so in the help-used note, then try again later with it closed.

## 6. Later recall

Two days later, list the separate purposes of Secure, HttpOnly and the application SameSite rule. Then reconstruct the difference between private and no-store for this exercise. Record the date, what you recalled unaided, what you checked and one remaining question. This is a practice record, not a claim of complete real-world competence.

## Handover

Submit your own saved worksheet and a short note answering: "What is observed, where is the evidence, what is uncertain, and what should be checked next?" Include initial prediction, correction and help used. No upload or publication is part of this lab.
