# Check an indicator before using it

Someone gives you a list of addresses to watch. One report is old, one is a
copy, and one address is shared by many users. What does each claim actually support?



This original exercise uses fictional records. It is separate from coursework.
It makes no claim about a learner's past work or skill.

## Start here

Allow 25-40 minutes. Spend 5 reading, 10 making a first attempt, 10 checking,
and 5-15 explaining a changed case. You need Python 3.10 or newer, a terminal,
and a text editor. Use only the standard library. Practise dns-triage and email-triage first.
You do not need admin rights or an account. You do not need to install tools,
scan a live system or change security settings.

**Words:** An indicator is a detail used to help find related activity, such as
a domain. Provenance means where a claim came from. Confidence is how sure the
report author says they are. Expiry is when a claim needs review. Scope limits
where and how a claim applies. Corroboration means support from another source.

## Question and exact rules

The register has as_of and records. Each row names its id, value, type, source,
confidence, observed_at, reported_at, valid_until, scope, contradicted and evidence_id.
Types are domain (.test only) or ipv4 (the three address ranges set aside for
documentation). Source is direct or copied. Confidence is a whole number from
0-100, or null when it is not stated. Scope is single-host or shared-service.
A true contradicted flag means there is evidence that conflicts with the claim.
This calls for a review. It does not say which report is right. Times are UTC.
Observation <= report <= as_of; expiry must be after observation.

Use the first rule that fits, in this order:

1. Use **review-expiry** at or after valid_until.
2. Otherwise, use **resolve-conflict** when contradicted is true.
3. Otherwise, use **seek-origin** for a copied source, confidence that is not stated,
   or confidence below 70.
4. Otherwise, use **narrow-scope** for shared-service.
5. Otherwise, use **context-only-use**.

None of these labels means "malicious" or gives you the right to block anything.
The last label lets you use a current direct report as context while you check
other evidence. Review it at the earlier of expiry or as_of+7 days. Review all
other labels now. Repeated evidence_id values are a single source, even when
several records quote them. Do not count copies as separate support.

The case JSON is the input record. Its artifacts are readable copies of raw
evidence when prepared. Change only a run copy. For a repeated model check,
edit the evidence inside case.json; editing an extracted artifact alone does
not change case.json. Each program rejects unsupported structure. Record-level
rejections are named below where that is part of the lesson.

## Practice commands

Open a terminal in this lab folder. Replace `python` with `py -3` if needed.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. Save a prediction in notes.txt before seeing an answer.
Fill the decisions in answers.json with the exact vocabulary above. Add an
explanation and evidence IDs. Keep the first attempt; write corrections below it.

Create a register in notes.txt. Include the value, report ID, original source,
claimed confidence, scope, dates, decision and review date. Write out one weak
claim that you reject. For example, explain why a copied report cannot justify a
blanket block, even with high confidence. State which original evidence you need.
This is a paper assessment. You will not look up reputation or change a blocklist.

After your prediction and practical work, compare the model:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

Use the matching attempt path for the later cases. Prepare refuses to replace
an existing folder. Its output must be below run/. Other explicit paths are
relative to the terminal directory. Exit 0 means success or an answer match;
1 means a mismatch or missing writing; 2 means invalid input or a file error.
A match checks labels and the presence of writing. A person must review whether
the explanation is sound. Tests and verify check the package, not learner skill.

## Save evidence and hand over

Keep case.json, answers.json and notes.txt. Record the commands, outputs, first
prediction, observed facts, interpretation, unknowns, next check, and help used.
Give each fact a record ID. End with a short handover: question, scoped finding,
two evidence references, a competing explanation, and the next evidence needed.
Mark your stage as attempted, checked with help, or attempted again unaided.
Do not call a script match mastery.

Cleanup is optional. After saving your work elsewhere, remove only the chosen
run/attempt folder using your file manager. Check its full path first. No system
setting needs rollback. Keep supplied fixtures and first attempts.

## Limits

All indicators and reports are made up. No lookup, reputation check or block is run. Nothing is sent to an outside service.

A confidence number states how sure the report author is. It is not a measured chance or proof.

A repeated report gives no new source of support. A shared service can serve users who have no link to each other.

The seven-day review rule and 70 threshold were chosen for this lesson. STIX does not require them. This tool does not implement STIX.

## Primary sources

Opened on 25 October 2026. These sources support the concepts. The exact fields,
thresholds and answer rules are teaching choices, not official policy.

- [OASIS STIX 2.1: indicator validity and confidence](https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html)
- [NIST SP 800-61 Rev. 3: incident response](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
