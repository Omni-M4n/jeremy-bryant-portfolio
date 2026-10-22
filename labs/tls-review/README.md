# TLS certificate review

Check decoded certificate dates and DNS names at a fixed observation time while keeping supplied trust reports separate from verified trust. These are original fictional practice cases, not copied coursework or completed professional work.

## Before starting

Prerequisites: Domain names, UTC time and HTTPS basics. No certificate command-line utility or coding experience is required. Use Python 3.10+ with the standard library. Run the commands from this lab folder. The learner reads evidence, makes decisions and edits a worksheet; programming is not required.

Allow **30-45 minutes** for the first guided pass: 5 minutes for vocabulary and scope, 15 for prediction, 10 for checking and correction, and 5-15 for explanation. Changed and later recall exercises are separate practice. Personal completion and independent competence have not been assessed.

## Vocabulary

**SAN:** subject alternative name, including a certificate DNS identity. **notBefore/notAfter:** the inclusive validity interval. **Wildcard:** here, one entire leftmost DNS label. **Chain report:** a supplied claim about validation, not work performed by this script.

## Evidence and exact input model

Decoded fictional DNS subject alternative names, validity timestamps, requested hosts and an explicitly supplied chain report.

Each case has exactly `schema_version: 1`, `lab_id: "tls-review"`, `case_id` (`guided`, `changed`, `challenge`), `title`, `synthetic: true`, `context`, `data`, `artifacts`. `context.question` is nonempty text. Objects reject unknown/missing fields; record IDs are unique lowercase names. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). Files are small UTF-8 JSON; readable artifacts are supplied through prepare where relevant.

`data` contains exactly `evaluation_time` (UTC `YYYY-MM-DDTHH:MM:SSZ`), `renew_within_days` (integer 0-365), and `certificates`. Each certificate has `id`, `requested_host`, unique `dns_names` (possibly empty), `not_before`, `not_after`, and `chain_report` (`verified`, `failed`, `unverified`). Hosts and names are ASCII `.test` domains; a SAN may start with a single whole-label `*.`. DNS comparison is case-insensitive. Calendar dates must exist, and notBefore must not exceed notAfter. `artifacts` is empty; decoded JSON is the only source. No common-name fallback, IP SANs or internationalised-name conversion is implemented.

## Decision vocabulary

A decision is either `fields-and-reported-chain-pass`, or the following applicable labels joined by `|` in this order: `not-yet-valid` (time before notBefore) **or** `expired` (time after notAfter); `hostname-mismatch` (no SAN match); `chain-failed` **or** `chain-unverified` (the supplied report); then `renewal-due` (time currently within the validity interval and seconds remaining <= days x 86400).

At exactly notAfter the date is still within the interval and renewal is due. Wildcards match one label only, so `*.museum.test` matches `east.museum.test` but neither `museum.test` nor `a.east.museum.test`. Passing these fields is a narrow result; the script has not validated a certificate chain.

## Run the practice

Use a new attempt number if the destination already exists. Prepare writes only beneath this lab's ignored `run/` folder and refuses existing or linked paths.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and its readable evidence. Before viewing the analysis, edit `run/attempt-01/answers.json`: replace every blank decision with an exact label above, write `explanation` as a paragraph, and put record/field/line references in the `evidence` list. Keep predictions, uncertainty, next check and help used in `notes.txt`. JSON strings use double quotes; do not add comments or trailing commas. An evidence entry can be a record ID plus the relevant field name.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Repeat show/check/analyse with the new attempt path. Default case is `fixtures/guided.json` beside the script. Explicit input paths are relative to your current directory; prepare output is relative to this lab. Exit 0 means command success or matching decision fields, 1 means differences/incomplete worksheet, and 2 means invalid input or a filesystem error. Analyse shows the reference reasoning and should stay closed until a prediction is saved. Verify compares three shipped fixtures with fixed reference outputs; it does not assess a learner. Check requires prose and references but cannot judge their accuracy.

## Deliverable and handover

A certificate review listing date/name issues, the remaining renewal window, supplied chain status and the next verification needed. Keep your first prediction and correction in the notes. Include an honest help-used statement. Use [the worked example](WORKED-EXAMPLE.md) for the guided case and [the drills](DRILLS.md) to reduce prompts over time.

Handover prompt: "What did you observe, which exact evidence supports it, what remains uncertain, and what narrow check should happen next?" A person should review your reasoning and an unfamiliar case before treating the practice as independently demonstrated.

## Limits and primary references

- Certificate fields and a supplied chain report are synthetic; no signature, chain, revocation, protocol or cipher verification is performed.
- Only ASCII DNS SAN names and a single leftmost wildcard are modelled; a matching name does not establish application safety.

Runtime is offline: no external target, packet transmission, email action or host configuration change occurs. All addresses and names are reserved fictional examples. The local decision rules are teaching choices; the references explain underlying concepts, not a claim of tool certification.

- [IETF RFC 5280, section 4.1.2.5: validity](https://www.rfc-editor.org/rfc/rfc5280.html#section-4.1.2.5)
- [IETF RFC 9525, section 6.3: DNS identity comparison](https://www.rfc-editor.org/rfc/rfc9525.html#section-6.3)
