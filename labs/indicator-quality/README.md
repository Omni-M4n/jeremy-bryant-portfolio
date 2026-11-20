# Assess supplied indicator quality and expiry

Use a small fictional register to decide how one supplied indicator record may
be retained for later investigation. The task is to preserve what the register
says without turning its metadata into verified truth. It is a paper-based practice worksheet; not an assessment.

All values and reports are synthetic. This package is separate from coursework
and records no learner attempt, completion, mastery, professional use or
independent assessment.

## Start here

Allow 25-40 minutes. You need Python 3.10 or newer, a terminal and a text editor.
The helper uses only the Python standard library. Practise
[DNS triage](../dns-triage/README.md) and
[email identity and message triage](../email-triage/README.md) first. You need no
account, administrator access, network connection or installed security tool.

An **indicator** here is a supplied domain or IPv4 value that may provide
context for a later investigation. **Provenance** is the supplied `source`
label. **Confidence** is the report author's stated number, not a measured
probability. **Scope** is the supplied limit on where the record may apply.
**Expiry** is the supplied time when the record must be reviewed. A supplied
conflict flag says only that this exercise marks a conflict; it does not settle
which claim is true.

## Exact question and decision rules

For each record, preserve its value, type, evidence ID, observation time,
report time, expiry, the case's `as_of` time, supplied conflict flag, supplied
source, stated confidence and supplied scope. Then use the first matching rule:

1. At or after `valid_until`, use `review-expiry`.
2. Otherwise, when `contradicted` is true, use `review-conflict`.
3. Otherwise, when `source` is `copied`, confidence is null, or confidence is
   below 70, use `seek-support`.
4. Otherwise, when scope is `shared-service`, use `narrow-scope`.
5. Otherwise, use `retain-as-context`.

For `retain-as-context`, set the review date to the earlier of `valid_until` or
exactly seven days after `as_of`. At exactly seven days the two dates are equal.
For every other decision, set the review date to `as_of`. Expiry therefore takes
precedence over conflict, support/provenance, shared scope and retained context.
Conflict takes precedence over support/provenance and scope. These are local
teaching rules, not STIX requirements or an operational policy.

These five labels do not mean malicious, safe, allow or block. They do not
attribute a domain or address to a person, organisation, device, action, intent
or cause. The helper performs no DNS or address lookup, reputation check,
blocking action or external submission.

## Supported case format

`case.json` is authoritative; this package has no extracted artifacts.
`artifacts` must therefore be an empty object. Editing another text file cannot
change the analysis. The eight-field case envelope follows the shared runtime.
For this package, `context` must contain exactly one `question`: 1-200 trimmed,
printable ASCII characters. `data` must contain exactly `as_of` and `records`.
There must be 1-30 records, and each record has exactly these fields:

`id`, `value`, `type`, `source`, `confidence`, `observed_at`, `reported_at`,
`valid_until`, `scope`, `contradicted`, `evidence_id`.

Record and evidence IDs are unique lowercase identifiers: they start with a
letter, contain only lowercase letters, digits or hyphens, and have at most 40
characters. An evidence ID may appear only once. The helper has no registry that
could prove two uses of an evidence ID were separate evidence.

Type is `domain` or `ipv4`. A domain is lowercase ASCII, ends in `.test`, has a
total length of at most 253 characters and has nonempty 1-63 character labels
made from letters, digits and internal hyphens. IPv4 accepts only the three
RFC 5737 documentation blocks: `192.0.2.0/24`, `198.51.100.0/24` and
`203.0.113.0/24`. Source is `direct` or `copied`. Scope is `single-host` or
`shared-service`. Confidence is null or a whole number from 0 through 100;
booleans are not numbers here. `contradicted` is exactly true or false.

Every time is an exact UTC timestamp with seconds and `Z`. The dates must
satisfy `observed_at <= reported_at <= as_of`. `valid_until` must be after
`observed_at` and cannot precede `reported_at`. Equality between `as_of` and
`valid_until` is expired under rule 1.

All of these fields are supplied training metadata. A `direct` label does not
verify the original source, collection method or reliability. The original
source is unknown unless supplied; this model supplies no such
source material. Confidence, scope, dates and the conflict flag are not verified
truth, reliability, independence or corroboration. `seek-support` requests
better support for this one record; it does not claim that another record
corroborates it.

## Practice commands

Open a terminal in this folder. On Windows, use `py -3` instead of `python` if
needed.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Before checking, complete the blank `answers.json` and the register in
`notes.txt`. Cite every supplied field listed above, choose one exact decision,
show the review-date arithmetic and state what remains unknown. Preserve your
first answer and record help used.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python test_lab.py
python lab.py verify
```

Use the matching case and answer paths for attempts 02 and 03. `prepare` writes
only to a new folder below this package's ignored `run/` directory. Exit code 0
means a command succeeded or a completed worksheet matched the expected labels;
1 means worksheet differences or missing writing; 2 means invalid input or a
file error. `check`, `verify`, unit tests and shipped references check bounded
package behavior. They cannot judge reasoning or assess a learner.

## Deliverable and handover

Keep `case.json`, the first `answers.json`, notes and any corrected answer. Save
the case ID, Python version, exact commands, each field-based observation,
decision, review-date calculation, uncertainty, smallest next evidence request,
correction and help used.

Use this exact handover prompt:

> Which supplied fields determined the decision and review date, what do those
> fields not verify, and what smallest support would you request next?

Mark the work as guided practice, changed-case practice or solo rehearsal
awaiting human review. Do not call a matching label independent skill.

Cleanup is optional. After retaining your work elsewhere, remove only your own
chosen `run/attempt-NN` folder with a file manager after checking the full path.
No network, host or security state was changed, so there is nothing to roll back.

## Boundary from cross-source corroboration

This package assesses each register row independently from its supplied fields.
It does not align clocks, compare events from different sources, test whether
identifiers or recorded hashes match, or decide whether two records describe
the same activity. Two rows may contain the same indicator value, but they remain
separate decisions; equality is not deduplication, support or corroboration.
Those are separate skills in
[cross-source corroboration](../cross-source-corroboration/README.md). Do not use
this package's `evidence_id`, source label or decision as proof of a cross-source
link.

## Limits and primary sources

All records, metadata and conflict flags are made up and supplied. A shared
service can serve unrelated users. A current, direct, high-confidence record is
still only context. Nothing here establishes current infrastructure, ownership,
identity, intent, harm, attribution, factual accuracy or an appropriate response
on a real system. The helper does not implement STIX.

This JSON is not a STIX Indicator object, and its raw domain and IPv4 values are
not STIX patterns. `observed_at`, `reported_at`, `source`, `scope`,
`contradicted` and the five decisions are local lesson fields and rules. In STIX
2.1, `valid_until` is optional, must be later than `valid_from` when present and
means the Indicator should no longer be considered valid at that time. This
lesson instead requires `valid_until` and routes its boundary to a review label;
that is a teaching workflow, not STIX semantics or policy.

These sources were opened on 25 October 2026. They support the general concepts;
the five labels, their precedence, seven-day interval and 70 threshold are
teaching choices.

- [OASIS STIX 2.1: indicator validity and confidence](https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html)
- [NIST SP 800-61 Rev. 3: incident response](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [RFC 2606: reserved `.test` names](https://www.rfc-editor.org/rfc/rfc2606.html)
- [RFC 5737: IPv4 documentation address blocks](https://www.rfc-editor.org/rfc/rfc5737.html)
