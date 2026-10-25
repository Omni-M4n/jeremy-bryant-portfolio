# Review MFA and recovery controls by account type

Read a list of sign-in checks for each account. Check how a sign-in method is set up, required and recovered. Apply the rules for people, software and emergency access. An account's name or type does not prove it is safe.

**Time:** Allow 30-45 minutes for your first pass. Try the recall task on another day.
**Before you start:** You need to open files and edit a small JSON worksheet. JSON stores named fields and lists as text. Basic network and security terms will help. You do not need work experience, a cloud account or coding skills. You will not change code.

## Key words

**MFA** uses two or more different kinds of proof to check who signs in. **Enrolment** means setting up a method. **Enforcement** means requiring it at sign-in. **Recovery** means regaining access if a method is lost. A **workload identity** is an account used by software. **Breakglass** is a controlled account for emergency use. **Phishing resistance** helps stop a fake site from passing sign-in proof to the real site. **TOTP** is a short code that changes with time. A **Boolean** is `true` or `false`.

## Evidence and exact rules

The `data` field has `as_of` and an `accounts` list. The list must not be empty. Each account has these fields:

| Field | Allowed form |
| --- | --- |
| `id` | Account ID. |
| `type` | `human`, `service` or `breakglass`. |
| `interactive`, `privileged`, `enforced`, `monitored`, `controlled_storage` | Boolean flags. |
| `methods` | A list with no repeats. |
| `recovery` | `none`, `helpdesk-verified`, `backup-codes-secured` or `shared-mailbox`. |
| `owner` | A lowercase ID or null. |
| `credential_lifetime` | `none`, `short-lived` or `long-lived`. |
| `test_age_days` | A whole number of zero or more, or null. |
| `exception_until` | A date or null. |

Null means no value is supplied. An interactive account can be used for a person's sign-in. A privileged account has extra access rights. Monitoring means watching and recording use. Controlled storage means keeping emergency material in a place with restricted access.

Human and emergency accounts can use `password`, `totp` and `security-key`. Service accounts can use `password` and `federated-workload`. A security key is a sign-in device. With federation, a trusted identity service supplies the workload's sign-in proof. Human and emergency accounts must be interactive. Their lifetime must be `none`. Service accounts must have recovery `none` and enforcement false. The rules below check their controls instead.

Only emergency accounts may use an exception, test age or controlled storage. The tool rejects unknown fields and types.

Apply these practice rules in the listed order. Join all labels that apply with semicolons. Do not add spaces. Here, enrolled MFA means at least one `totp` or `security-key` method is listed. This is a claim in the record. The tool does not test a sign-in.

| Account | Ordered labels and trigger |
| --- | --- |
| Human | Use `enrol-mfa` if no MFA method is listed. Otherwise, use `enforce-mfa` if it is not enforced. Then use `use-phishing-resistant-mfa` if privileged without `security-key`. Then use `repair-recovery` unless recovery is `helpdesk-verified` or `backup-codes-secured`. |
| Service | Use `disable-interactive-login` if interactive. Then use `assign-owner` if owner is null. Then use `replace-static-workload-credential` unless it uses short-lived federation with no password. Then use `monitor-workload-use` if monitoring is false. |
| Breakglass | Start with the human enrol/enforce rules. Then use `use-phishing-resistant-mfa` if no `security-key` is listed. A current exception waives these three MFA checks. Next check `assign-owner`, `monitor-emergency-use`, `secure-emergency-material`, `test-emergency-access` and `repair-emergency-recovery`, in that order. Use the tests below. |

An emergency account must have an owner, monitoring and controlled storage. If a control is absent, use its label. The test age must be known and at most 90 days. Use `test-emergency-access` if it is missing or over 90 days. Recovery must be `none` or `backup-codes-secured`. Otherwise use `repair-emergency-recovery`.

An exception is current if its date is on or after `as_of`. This includes its end date. It never waives the rules for ownership, monitoring, storage, testing or recovery.

If no control is missing, an emergency account with a current exception gets `exception-current`. In all other cases with no missing control, use `meets-lab-controls`. These labels apply only to this lab. They do not certify an account or set a policy for all accounts.

## Run the exercise

From the repository root, enter this folder with `cd labs/mfa-review`.

Use Python 3.10 or newer. On Windows, you may use `py` in place of `python` if it is your installed launcher. You do not need to install packages or set up an account or billing. All commands run offline. They change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any `.txt` evidence files. Open the blank `run/attempt-01/answers.json` worksheet. Fill in each decision with an exact label from the rules above. Write your own reason for each choice. In `evidence`, cite record IDs or line numbers from this case. Use `notes.txt` to record your first prediction, doubts and any help used.

Save your prediction before you run these commands:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has just three fields:

- `decisions` is an object. It pairs each record ID with your chosen label.
- `explanation` is text. Write why you chose those labels.
- `evidence` is a list of text references. You could name a record ID and its field. Use IDs from your case. Do not invent them.

`check` compares the decision labels. It also checks that you filled in the written fields. A person must judge whether those words are right. `verify` checks the supplied test cases. It does not assess your skill.

The exit code tells you what happened. Code 0 means success or a match. Code 1 means a mismatch or blank written fields. Code 2 means invalid input. If you omit `--case`, the command uses the guided case beside the script. Input paths start from your current terminal folder. The `--out` path starts from this lab folder. It must name a new folder below `run/`.

Use fresh folders for the next cases:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with your chosen folder. Edit practice copies only. Do not overwrite the supplied fixtures or reference answers. Fixtures are the starting cases.

## Deliverable and handover

Save a filled worksheet and a short evidence note for each case. Include your first prediction and any change to it. State what is still unclear. Name one next check that these files cannot answer. Record any help used, including the worked example.

Ask a reviewer: "Can you reach my decision from these record IDs? Which claim goes beyond the evidence?" Your skill at doing this alone is still **unassessed**. A matching output does not prove skill, a qualification or work experience. These are made-up practice cases. They are not work for assessment.

## Limits

The tool does not try to sign in. A `security-key` label does not show how well it was set up. It does not prove that the user was checked or that backups exist. It cannot prove resistance to phishing in every sign-in flow. The emergency design and 90-day test limit are made-up policy. Real teams need a tested design for their provider. Software accounts still carry risk even though their controls differ from human MFA.

## Primary references

NIST covers the strength of sign-in methods and how they are managed and recovered. This lab's labels and service-account rules are teaching choices. So is its emergency exception policy. They do not claim to meet NIST's standard.

- [NIST SP 800-63B: authentication and authenticator management](https://pages.nist.gov/800-63-4/sp800-63b.html)

The links are optional extra reading. They were checked on 2026-10-23. The lab does not fetch them. Read [the worked example](WORKED-EXAMPLE.md) after you save your prediction. Use [the drills](DRILLS.md) for more practice.
