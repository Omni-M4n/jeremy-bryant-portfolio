# Drills: TCP handshake investigation

## 1. Guided evidence pass

Prepare guided as `run/attempt-01`. Keep WORKED-EXAMPLE closed initially. Read the question, mark scope and evidence sources, then fill every decision and a short explanation. Use the vocabulary if needed and record that help. Allow 30-45 minutes for this first pass.

## 2. Fewer prompts

Work through these questions before opening the analysis:

- Which side sent each flag combination?
- What should each ACK acknowledge after one SYN?
- What evidence separates a reset from no visible response?

Check decisions, read the worked example and write one correction with its evidence reference. If every label matched, still explain the hardest choice; a lucky label is not evidence of understanding.

## 3. Independent case

Prepare challenge in a fresh folder. Classify each connection from its packet evidence. Identify which records support the classification and where the capture limits your conclusion. Keep reference outputs, the worked example and analyse closed until your decisions, evidence references and handover are saved. Use the README for syntax or vocabulary if needed and record that help. Afterwards, compare results and have another person assess the reasoning. A matching label alone does not establish understanding.

## 4. Changed conditions

Prepare changed separately and compare its evidence with guided; keep both attempts. Predict each result before revealing analysis.

- Can gallery be called established when the final ACK is not captured?
- Can archive be called failed when the capture begins with SYN-ACK?
- What capture location or duration information would help resolve either gap?

Write which fact changed, why the relevant rule changed or did not change, and what remains uncertain. Do not edit the shipped fixture or reference files to make an answer match.

## 5. Teach-back

Explain why three correctly named flags are not enough: demonstrate the two expected next numbers and one capture uncertainty. Use one record ID and a counterexample. If you need the worked example, say so in the help-used note, then try again later with it closed.

## 6. Later recall

Two days later, sketch the ordinary three-packet opening using new numbers 70 and 500. Write both ACK values, then list what an absent response does not prove. Record the date, what you recalled unaided, what you checked and one remaining question. This is a practice record, not a claim of complete real-world competence.

## Handover

Submit your own saved worksheet and a short note answering: "What is observed, where is the evidence, what is uncertain, and what should be checked next?" Include initial prediction, correction and help used. No upload or publication is part of this lab.
