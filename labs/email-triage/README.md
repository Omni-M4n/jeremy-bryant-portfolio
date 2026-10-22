# Email identity and message triage

Separate supplied receiver authentication evidence from untrusted header claims, then review domain discrepancies without declaring a message safe. These are original fictional practice cases, not copied coursework or completed professional work.

## Before starting

Prerequisites: DNS and domain-name basics. No mailbox access, real messages, DNS queries or email-security experience is needed. Use Python 3.10+ with the standard library. Run the commands from this lab folder. The learner reads evidence, makes decisions and edits a worksheet; programming is not required.

Allow **30-45 minutes** for the first guided pass: 5 minutes for vocabulary and scope, 15 for prediction, 10 for checking and correction, and 5-15 for explanation. Changed and later recall exercises are separate practice. Personal completion and independent competence have not been assessed.

## Vocabulary

**From domain:** the domain shown by the message author field. **MAIL FROM:** the SMTP envelope identity used in this SPF model. **DKIM domain:** the reported signing domain. **DMARC:** domain authentication alignment with From. **authserv-id:** the claimed reporting service. **Trust register:** separate supplied evidence of which records came from the receiving relay.

## Evidence and exact input model

Decoded synthetic From, Reply-To and link domains, Authentication-Results records, and an out-of-band fictional receiver trust register.

Each case has exactly `schema_version: 1`, `lab_id: "email-triage"`, `case_id` (`guided`, `changed`, `challenge`), `title`, `synthetic: true`, `context`, `data`, `artifacts`. `context.question` is nonempty text. Objects reject unknown/missing fields; record IDs are unique lowercase names. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). Files are small UTF-8 JSON; readable artifacts are supplied through prepare where relevant.

`context` adds `trusted_receiving_relay` with `authserv_id` (a `.test` name), unique `trusted_record_ids`, `alignment`=`strict`, and `provenance`=`fictional-receiver-export`. This context is supplied independently of the message, not extracted from a header. `data.messages` records have `id`, `expected_sender_domain`, `from_domain`, `reply_to_domain`, unique `link_domains`, and `authentication_results`. Each result has unique global `id`, `authserv_id`, `spf`, `mailfrom_domain`, `dkim`, `dkim_domain`, `dmarc`; result values are pass/fail/none/temperror. A DKIM none result has null dkim_domain; other DKIM results require a domain. All domains are ASCII `.test`; names compare case-insensitively. A result is trusted only when its ID is registered and its relay matches. At most one trusted result per message is supported. A registered absent ID, wrong relay or contradictory trusted DMARC result is rejected. JSON is authoritative; `artifacts.headers.txt` is an exact readable mirror, not a general email parser.

## Decision vocabulary

| Label | Exact meaning |
|---|---|
| `authentication-unverified` | No registered trusted receiver result exists for this message. |
| `domain-authentication-failed` | The trusted result reports DMARC fail. |
| `domain-authentication-unresolved` | Trusted DMARC is none or temperror. |
| `authenticated-domain-with-mismatch` | Trusted DMARC passes, but From differs from the expected sender, Reply-To differs from From, or a link domain differs from From. |
| `authenticated-domain-review-content` | Trusted DMARC passes and none of those domain discrepancies is present; content still needs review. |

Apply in that order. In this strict-alignment exercise, a trusted DMARC pass needs SPF pass with MAIL FROM exactly matching From, or DKIM pass with signing domain exactly matching From. A trusted fail with either aligned pass is contradictory. Untrusted claims do not gain authority by being internally plausible. Domain differences are review prompts, not automatic proof of phishing.

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

A measured triage note identifying trusted result records, domain alignment, discrepancies, a next check and unresolved content risk. Keep your first prediction and correction in the notes. Include an honest help-used statement. Use [the worked example](WORKED-EXAMPLE.md) for the guided case and [the drills](DRILLS.md) to reduce prompts over time.

Handover prompt: "What did you observe, which exact evidence supports it, what remains uncertain, and what narrow check should happen next?" A person should review your reasoning and an unfamiliar case before treating the practice as independently demonstrated.

## Limits and primary references

- Receiver trust is supplied out of band for this exercise; an Authentication-Results header or matching relay name alone is not proof.
- SPF authorises a sending domain context; DMARC relates authenticated domains to From. Neither authenticates a person or guarantees harmless content.
- Only decoded strict domain alignment is checked; no DNS, signature, ARC, relaxed alignment, attachment or URL-content analysis occurs.

Runtime is offline: no external target, packet transmission, email action or host configuration change occurs. All addresses and names are reserved fictional examples. The local decision rules are teaching choices; the references explain underlying concepts, not a claim of tool certification.

- [IETF RFC 8601, section 1.2: Authentication-Results trust boundary](https://www.rfc-editor.org/rfc/rfc8601.html#section-1.2)
- [IETF RFC 7208: SPF domain authorisation](https://www.rfc-editor.org/rfc/rfc7208.html)
- [IETF RFC 9989: DMARC alignment model](https://www.rfc-editor.org/rfc/rfc9989.html)
