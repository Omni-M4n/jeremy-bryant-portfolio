# Review a TLS certificate's names and dates

A site name can fit a certificate while its date has expired. A date can fit
while the name is wrong. Check both, then ask what evidence of trust is missing.
A certificate is a signed record used to help check a site's identity.

These cases are made up. This is offline practice, separate from coursework.
It does not claim past work or proven skill.

## Start here

You need basic domain names, UTC time and HTTPS. Use Python 3.10 or newer,
a terminal and a text editor. You do not need to write code or use a real
certificate tool. Run commands from this lab folder.

Allow 30–45 minutes. Read for 5 minutes, predict for 15, then check for 10.
Use the time left to explain your result. Do the later cases in fresh sessions.
No one has assessed your skill from these files.

| Term | Meaning here |
| --- | --- |
| SAN | A name listed in a certificate's subject alternative name field |
| notBefore | First valid date and time, including that exact instant |
| notAfter | Last valid date and time, including that exact instant |
| Wildcard | A star that can stand for one leftmost name part |
| Chain report | A supplied claim about a trust check, not a check this script ran |

## Read the case

The case holds names, dates, a requested host and a chain report. It is the
only source. The `artifacts` object is empty. There are no real certificates.
Read the [shared file rules](../FOUNDATION-CONTRACT.md) for the case file format.

| Case field | Required value |
| --- | --- |
| schema_version | 1 |
| lab_id | tls-review |
| case_id | guided, changed or challenge |
| title | Case title |
| synthetic | true |
| context.question | Nonempty question |
| data | Fields in the next table |
| artifacts | Empty object |

The parser rejects missing or extra fields. IDs must be unique lowercase names.
Files use UTF-8 JSON. That is a text format made from named fields and values.

| Data field | Meaning and range |
| --- | --- |
| evaluation_time | Time used for every check: UTC YYYY-MM-DDTHH:MM:SSZ |
| renew_within_days | Whole number from 0 to 365 |
| certificates | List of records |
| id | Unique record name |
| requested_host | Host name being checked |
| dns_names | Unique SAN names; the list can be empty |
| not_before, not_after | First and last valid times, in the same UTC form |
| chain_report | verified, failed or unverified |

The last five rows describe each certificate record. Dates must be real
calendar dates. The first valid time must not be after the last one.
Hosts and names use ASCII characters and end in `.test`. Letter case does not
change a name match. A SAN may start with one `*.` wildcard.

The wildcard matches one name part only. For example, `*.museum.test` matches
`east.museum.test`. It does not match `museum.test` or `a.east.museum.test`.
There is no fallback to a common name. IP address SANs and name conversion
for other character sets are outside this lab.

## Choose a result

Use `fields-and-reported-chain-pass` when no issue below applies.
Otherwise join the matching labels with `|` in this order:

| Order | Condition | Label |
| --- | --- | --- |
| 1 | Check time is before the first valid time | not-yet-valid |
| 1 | Check time is after the last valid time | expired |
| 2 | No SAN name matches the host | hostname-mismatch |
| 3 | Supplied chain report says failed | chain-failed |
| 3 | Supplied chain report says unverified | chain-unverified |
| 4 | Date is valid now and renewal is due | renewal-due |

Only one date-state label and one chain-state label can apply.
Renewal is due when seconds left are at most the day count times 86,400.
Apply that rule only while the date is valid. At the exact last valid instant,
the date still fits and renewal is due. A pass here does not prove trust.

## Run the practice

Prepare writes under this lab's `run/` folder. It refuses old or linked paths.
Use a new attempt number if your folder already exists.

```console
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case before viewing the answer. Fill each blank in
`run/attempt-01/answers.json` with an exact label above. Add a short reason.
In the evidence list, give record IDs and field names. Keep your prediction,
unknowns, next check and help used in `notes.txt`. JSON needs double quotes.
Do not add comments or commas after the last item.

```console
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python lab.py verify
python test_lab.py
```

Use the matching path for later attempts. The default is the guided fixture.
Input paths are relative to your current folder. Prepare output is relative
to this lab. Analyse shows the answer, so save a prediction first.

| Exit code | Meaning |
| --- | --- |
| 0 | Command ran, or decision fields match |
| 1 | Decisions differ, or the worksheet is incomplete |
| 2 | Invalid input or a file error |

Verify checks the three supplied cases against fixed answers. It does not
assess your skill. Check needs reasons and references, but cannot judge them.

## Save and explain

Write a short review of the names, dates, time left and supplied chain status.
State the next trust check needed. Keep both your first answer and correction.
Note any help used. Open [the worked example](WORKED-EXAMPLE.md) after your
first attempt. Use [the drills](DRILLS.md) to practise with less help.

In a handover, state what you saw and cite exact evidence. Then state what you
still do not know and what you would check next. A person should review your
reasoning and a fresh case before treating the skill as shown.

## Limits and sources

The script checks fields from made-up records. It does not check signatures,
trust chains, revoked certificates, protocol versions or cipher choices.
A name match cannot show that an application is safe. Nothing is sent over
a network, and no host settings are changed.

These sources explain the concepts. The small model's rules are teaching
choices; passing them is not a tool qualification.

- [IETF RFC 5280: validity](https://www.rfc-editor.org/rfc/rfc5280.html#section-4.1.2.5)
- [IETF RFC 9525: DNS identity checks](https://www.rfc-editor.org/rfc/rfc9525.html#section-6.3)
