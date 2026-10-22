# Drills: TLS certificate review

## 1. Guided evidence pass

Prepare guided as `run/attempt-01`. Keep WORKED-EXAMPLE closed initially. Read the question, mark scope and evidence sources, then fill every decision and a short explanation. Use the vocabulary if needed and record that help. Allow 30-45 minutes for this first pass.

## 2. Fewer prompts

Work through these questions before opening the analysis:

- Which fixed time is being used, and why should the wall clock not change the answer?
- Does the requested host match any SAN?
- Which facts came from fields and which from a supplied chain report?

Check decisions, read the worked example and write one correction with its evidence reference. If every label matched, still explain the hardest choice; a lucky label is not evidence of understanding.

## 3. Independent case

Prepare challenge in a fresh folder. Use challenge without help. Explain exactly-notAfter behaviour, why a good hostname with an unverified chain is incomplete, and why an empty SAN list is not rescued by an imagined common name. Keep the reference files closed until your worksheet and handover are saved. Use the README vocabulary as a glossary if necessary and record that help. Ask another person to examine the reasoning rather than merely the exit code.

## 4. Changed conditions

Prepare changed separately and compare its evidence with guided; keep both attempts. Predict each result before revealing analysis.

- Why does *.museum.test not cover images.eu.museum.test?
- How can not-yet-valid and a failed chain report both require attention?
- Which checks would still be missing if all supplied fields passed?

Write which fact changed, why the relevant rule changed or did not change, and what remains uncertain. Do not edit the shipped fixture or reference files to make an answer match.

## 5. Teach-back

Explain expiry, hostname matching and trust as three separate checks, then demonstrate one wildcard that must not match. Use one record ID and a counterexample. If you need the worked example, say so in the help-used note, then try again later with it closed.

## 6. Later recall

Two days later, write the inclusive boundary rule and the one-label wildcard rule from memory. Use a different date and hostname to test your explanation. Record the date, what you recalled unaided, what you checked and one remaining question. This is a practice record, not a claim of complete real-world competence.

## Handover

Submit your own saved worksheet and a short note answering: "What is observed, where is the evidence, what is uncertain, and what should be checked next?" Include initial prediction, correction and help used. No upload or publication is part of this lab.
