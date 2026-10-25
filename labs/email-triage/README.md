# Email identity and message triage

Check which sender results came from the trusted receiver. Keep them separate from untrusted header claims. Then review domain names that differ. Do not claim that a message is safe. These made-up cases were written for practice. They are not copied coursework. They do not show work done in a job.

## Before starting

Know the basics of DNS and domain names first. You do not need mailbox access, real messages or email security experience. The lab makes no DNS queries. Use Python 3.10+ with its built-in library. Run each command from this lab folder. Read the evidence, choose labels and fill in a worksheet. You do not need to write code.

Allow **35-45 minutes** for the first guided case. Spend 5 minutes on terms and scope, then 15 on your first choices. Allow 10 minutes to check and correct them. Spend 5-15 minutes on your reasons. Do the changed case and recall tasks as separate practice. No one has yet assessed your work or skill.

## Vocabulary

The **From domain** is the domain in the message author field. **MAIL FROM** is the SMTP envelope identity used for SPF here. The **DKIM domain** is the domain said to have signed the message. **DMARC** checks how authenticated domains line up with From. **authserv-id** names the service that claims to report the result. The **trust register** is a separate supplied record. It says which results came from the receiving relay.

## Evidence and exact input model

You get made-up From, Reply-To and link domains that are already decoded. You also get Authentication-Results records. A separate trust register names results from the made-up receiver.

Each case needs `schema_version: 1` and `lab_id: "email-triage"`. The `case_id` is `guided`, `changed` or `challenge`. It also needs `title`, `synthetic: true`, `context`, `data` and `artifacts`. No other top-level fields are allowed. `context.question` must contain text. Each object must have the listed fields and no others. Each record ID must be a unique lowercase name. Read the [shared file and command contract](../FOUNDATION-CONTRACT.md). The files use UTF-8 JSON and are small. Where needed, prepare also makes a copy of the evidence that you can read.

`context` adds `trusted_receiving_relay`. This has `authserv_id`, which is a `.test` name, and unique `trusted_record_ids`. It also has `alignment`=`strict` and `provenance`=`fictional-receiver-export`. This context comes from a source separate from the message. It is not taken from a header.

Each `data.messages` record has `id`, `expected_sender_domain`, `from_domain` and `reply_to_domain`. It also has unique `link_domains` and `authentication_results`. Each result has `id`, `authserv_id`, `spf`, `mailfrom_domain`, `dkim`, `dkim_domain` and `dmarc`. A result ID must be unique across the whole case. Results use pass, fail, none or temperror. A DKIM none result needs a null dkim_domain. Other DKIM results need a domain. All domains use ASCII and end in `.test`. Uppercase and lowercase versions of a name compare as equal.

Trust a result only if its ID is in the register and its relay matches. There can be at most one trusted result per message. The tool rejects a registered ID that is missing or has the wrong relay. It also rejects trusted DMARC results that conflict with the strict rule below. JSON is the source used for results. `artifacts.headers.txt` must be an exact copy you can read. The tool does not parse email in general.

## Decision vocabulary

| Label | Exact meaning |
|---|---|
| `authentication-unverified` | No registered trusted receiver result exists for this message. |
| `domain-authentication-failed` | The trusted result reports DMARC fail. |
| `domain-authentication-unresolved` | Trusted DMARC is none or temperror. |
| `authenticated-domain-with-mismatch` | Trusted DMARC passes, but From differs from the expected sender, Reply-To differs from From, or a link domain differs from From. |
| `authenticated-domain-review-content` | Trusted DMARC passes and none of those domain discrepancies is present; content still needs review. |

Use the rules in the order shown. This lab uses strict alignment: the domain must match From exactly. For a trusted DMARC pass, at least one of two checks must pass. SPF can pass with MAIL FROM exactly matching From. Or DKIM can pass with its signing domain exactly matching From. A trusted DMARC fail conflicts with either of those aligned passes. An untrusted claim is still untrusted even if its fields seem to make sense. A domain difference is a reason to review the message. By itself, it does not prove phishing.

## Run the practice

Use a new attempt number if that folder already exists. Prepare writes only inside this lab's ignored `run/` folder. It rejects paths that already exist or use links.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and its evidence. Save your first choices before you view the analysis. Edit `run/attempt-01/answers.json`. Fill each blank decision with an exact label from the table. Write a paragraph in `explanation`. In the `evidence` list, cite the records, fields or lines you used. One entry can give a record ID and its field name. In `notes.txt`, keep your first choices, doubts, next check and help used. JSON text strings need double quotes. Do not add comments or a comma after the last item.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Repeat show/check/analyse with the path for your new attempt. The default case is `fixtures/guided.json`, beside the script. Input paths that you supply start from your current folder. The prepare output path starts from this lab folder.

Exit 0 means the command worked or your decision fields match. Exit 1 means a choice differs or your worksheet is incomplete. Exit 2 means the input is invalid or there is a file error. Analyse shows the set answers and reasons. Keep it closed until you save your first choices. Verify compares the three supplied cases with fixed expected outputs. It does not assess your skill. Check requires written reasons and sources. It cannot judge whether they are right.

## Deliverable and handover

Write a careful triage note. Name the trusted result records and show which domains line up. List differences, a next check and any content risk that is still unknown. Keep your first choices and any corrections in the notes. State what help you used. Use [the worked example](WORKED-EXAMPLE.md) for the guided case. Use [the drills](DRILLS.md) to try tasks with less help over time.

In your handover, answer: "What did you see? Which exact evidence supports it? What is still unknown? What small check should happen next?" Ask someone to review your reasons and your work on a new case. Until then, your skill without help has not been assessed.

## Limits and primary references

- Trust in the receiver comes from a separate source in this lab. An Authentication-Results header or matching relay name alone does not prove trust.
- SPF checks permission to send for a domain in a given context. DMARC links authenticated domains to From. Neither proves who the person is or that the content is harmless.
- The tool checks only decoded domains with strict alignment. It does not check DNS, signatures, ARC, relaxed alignment, attachments or URL content.

The lab runs offline. It contacts no outside target, sends no packets or email, and changes no host settings. All names and addresses are reserved for made-up examples. The rules were chosen for this lesson. The sources explain the ideas behind them. They do not certify this tool.

- [IETF RFC 8601, section 1.2: Authentication-Results trust boundary](https://www.rfc-editor.org/rfc/rfc8601.html#section-1.2)
- [IETF RFC 7208: SPF domain authorisation](https://www.rfc-editor.org/rfc/rfc7208.html)
- [IETF RFC 9989: DMARC alignment model](https://www.rfc-editor.org/rfc/rfc9989.html)
