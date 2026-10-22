# Review MFA and recovery controls by account type

Read an authentication-control inventory and separate enrolment, enforcement, recovery, workload identity and emergency-access controls. An account label alone never proves that its controls are adequate.

**Time:** 30-45 minutes for a first pass; use the later recall task on another day.
**Prerequisites:** Basic file navigation, editing a small JSON worksheet, and introductory networking/security vocabulary. No professional security experience, cloud account, coding background or programming changes are required.

> **Vocabulary:** **MFA**: authentication using distinct factors. **Enrolment**: registering a method. **Enforcement**: requiring a method at login. **Recovery**: regaining access after a method is lost. **Workload identity**: an identity used by software. **Breakglass**: a controlled emergency account. **Phishing resistance**: protection against authentication being relayed to an impostor.

## Evidence and exact semantics

`data` contains `as_of` and nonempty `accounts`. Each account has `id`,
`type` (`human`, `service`, `breakglass`), Boolean `interactive`, `privileged`,
`enforced`, `monitored`, `controlled_storage`, a unique `methods` list,
`recovery`, `owner` (lowercase ID or null), `credential_lifetime`,
`test_age_days` (nonnegative integer or null), and `exception_until` (date or null).

Human/emergency methods are `password`, `totp`, `security-key`. Workloads allow
`password` and `federated-workload`. Recovery is `none`, `helpdesk-verified`,
`backup-codes-secured`, or `shared-mailbox`. Credential lifetime is `none`,
`short-lived`, or `long-lived`. Human/emergency records must be interactive and
use lifetime `none`. Service records use recovery `none` and enforcement false;
their controls are assessed explicitly below. Only emergency records may use
an exception, test age or controlled storage. Unknown fields/types fail.

The fictional policy evaluates these exact decision labels in the listed order.
Join applicable labels with semicolons, without spaces. "Enrolled MFA" in this
model means at least one `totp` or `security-key` method; it is a record claim,
not a test of the actual ceremony.

| Account | Ordered labels and trigger |
| --- | --- |
| Human | `enrol-mfa` if no MFA method; otherwise `enforce-mfa` if not enforced; `use-phishing-resistant-mfa` if privileged without security-key; `repair-recovery` unless helpdesk-verified or backup-codes-secured. |
| Service | `disable-interactive-login` if interactive; `assign-owner` if owner null; `replace-static-workload-credential` unless short-lived federation with no password; `monitor-workload-use` if monitoring false. |
| Breakglass | First the human enrol/enforce rules and `use-phishing-resistant-mfa` if no security-key, unless a current exception waives those three MFA checks; then `assign-owner`, `monitor-emergency-use`, `secure-emergency-material`, `test-emergency-access`, `repair-emergency-recovery` as explained below. |

Emergency ownership, monitoring and controlled storage must be present. Test
age must be at most 90 days inclusive. Recovery must be `none` or secured backup
codes. An exception dated on or after `as_of` is current, including expiry day;
it never waives ownership, monitoring, storage, testing or recovery controls.
With no missing labels, use `exception-current` for an emergency account with
a current exception; otherwise use `meets-lab-controls`. The labels are a
decision vocabulary, not a certification or a universal account policy.

## Run the exercise

From the repository root, enter this folder with `cd labs/mfa-review`.
Use Python 3.10 or newer. On Windows, `py` may replace `python` if that is your
installed launcher. No package install, account, cloud subscription or billing
setup is needed. Commands run entirely offline and change no real service.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case and any extracted `.txt` evidence. Edit the blank
`run/attempt-01/answers.json`: fill every decision with the exact vocabulary
below, write your own explanation, and cite record IDs or line references in
`evidence`. Keep `notes.txt` for prediction, uncertainty and help used.
Only after saving your prediction:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The worksheet has exactly `decisions` (object), `explanation` (text), and
`evidence` (list of text references). For example, an evidence entry can be a
record ID plus its field name. Use your own case IDs, not invented references.
`check` compares decision strings and requires nonempty written fields; a person
must assess their accuracy. `verify` checks shipped fixtures, not learner skill.
Exit codes are 0 for success/match, 1 for differences or incomplete written
fields, and 2 for invalid input. Default `--case` is the guided fixture beside
the script. Explicit input paths are relative to the working directory; `--out`
is relative to this lab and must be a new folder below `run/`.

For the next cases, prepare fresh folders:

```text
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
```

Replace `attempt-01` in `show`, `analyse` and `check` with the chosen folder.
Edit practice copies only. Do not overwrite fixture or reference files.

## Deliverable and handover

Save one completed worksheet and a short evidence note for each case. Include
your prediction, changed judgment, uncertainty, and one next check you cannot
perform from this evidence. Record whether you used the worked example or help.
Ask a reviewer: "Can you reproduce my decision from these record IDs, and which
claim goes beyond the evidence?" Your independent status remains **unassessed**;
matching output is not a qualification, professional experience or proof of
mastery. These are original fictional practice cases, not assessment submissions.

## Limits

No login is attempted. A security-key label does not establish registration quality, user verification, backup arrangements or resistance in every provider flow. The emergency design and 90-day boundary are fictional policy; real organisations need a provider-specific tested design. Workload risk remains even though human MFA is not the workload control.

## Primary references

NIST distinguishes authenticator strength, lifecycle and recovery. The local check labels, workload branch and emergency exception policy are teaching choices and do not claim NIST compliance.

- [NIST SP 800-63B: authentication and authenticator management](https://pages.nist.gov/800-63-4/sp800-63b.html)

Links are optional further reading, checked 2026-10-23. Running this lab does
not fetch them. See [the worked example](WORKED-EXAMPLE.md) after your prediction
and [the drills](DRILLS.md) for varied practice.
