# Enrol, challenge and recover a training account

A club member knows a password and also uses a changing code. What happens
when the code is wrong, used again, or lost? You will try those events in a
training service on your computer. Then you will read its event log with the
secret values left out. This is called a redacted log.

This extends [mfa-review](../mfa-review/README.md). That lab checks flags
that show whether an account is enrolled. Here, you enrol a local account,
try signing in, use recovery once and enrol again. Then you check how the
saved state changed. This is an extension to the earlier lab.

Do mfa-review and session-lifecycle first. Allow 30-40 minutes.
Use Python 3.10+ and PowerShell already on your computer for the steps below.
The service does not listen for network traffic. It needs no extra packages
and uses no real account.

## Words used here

**MFA** means multi-factor authentication. It checks more than one kind of
proof when you sign in. A **TOTP** is a time-based one-time password.
This short code is made from a shared secret and a clock. An **authenticator**
is a device or app that gives proof. **Enrolment** registers it for use.
A **recovery code** is a backup proof to help you regain access.
A **session** stands for a successful login. **Replay** means trying to reuse
a proof that was already accepted.

## Set up a first attempt

Use Python 3.10 or newer, already on your computer. It works on Windows,
macOS or Linux. You need no extra packages, cloud account or network link.
A terminal is where you type commands. From the project folder, open one in
`labs/mfa-hands-on`. The commands use `python`. If your Python 3
command has a different name, use that name.

```text
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the small JSON file. JSON stores values with names. Here, `true` means
yes, `false` means no, and `null` means no value was given. Predict each
result first. Save it in `run/attempt-01/answers.json`. Fill in each decision
and explain why. List the record IDs in `evidence`. An ID is a record's name.
Keep this first attempt.

Run these commands only after you save your prediction.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The check looks at your answer words and checks that written fields are
filled in. A person must still review your reasons. Exit codes show how a
command ended. Code 0 means success. Code 1 means a mismatch or an unfinished
worksheet. Code 2 means the input is not valid. The `verify` command checks
the supplied cases. It does not score your work. These commands stay on your
computer and do not contact a cloud service.

Prepare `changed` in `run/attempt-02`. Prepare `challenge` in
`run/attempt-03`. Edit only these copies. Use a new output folder each time
so you keep each earlier attempt. To undo an edit, prepare a fresh copy.
Keep your evidence until someone reviews it. Later, remove only the named
practice folder you made. Never put personal records in it.


## Perform the local lifecycle

The supplied service.py is a training service run with commands. It saves
its state between steps. The same computer holds both fake factors.
Its state file is plaintext, so its contents are readable. It uses a fixed
fake password and a clock you control. These choices make it unsafe for real
accounts. It does not enrol real MFA.

In PowerShell, from this lab folder:

```powershell
$setup = python service.py new --folder run/account-01 | ConvertFrom-Json
$recovery = $setup.dummy_recovery_code
$code = python service.py device --folder run/account-01 --at 60
python service.py confirm --folder run/account-01 --at 60 --password training-pass --proof $code
python service.py challenge --folder run/account-01 --at 60 --password training-pass --proof $code
$code = python service.py device --folder run/account-01 --at 90
python service.py challenge --folder run/account-01 --at 90 --password wrong --proof $code
python service.py challenge --folder run/account-01 --at 90 --password training-pass --proof $code
python service.py recover --folder run/account-01 --at 120 --password training-pass --proof $recovery
$code = python service.py device --folder run/account-01 --at 150
python service.py confirm --folder run/account-01 --at 150 --password training-pass --proof $code
python service.py recover --folder run/account-01 --at 180 --password training-pass --proof $recovery
python service.py evidence --folder run/account-01
```

Predict each result before you run its line. The device command acts as the
training authenticator. It reads the local dummy seed, the secret used to
make codes. The first confirm enrols it. The service rejects a code reused
in the same time step. It rejects a wrong password without using up a valid
code. A later successful challenge makes one model session.

Successful recovery removes all model sessions. It uses up the recovery
code and replaces the seed. You must then enrol again. Trying the old
recovery code after this fresh enrolment must fail.

The expected event order is accept, reject, reject, accept, accept, accept,
reject. Include only the evidence output in your handover. Do not include
state.json, the setup output, the seed, codes or recovery value.
Do not take a screenshot of those secrets. The setup variables hold fake
secrets. Never use real sign-in details in their place.

The first accepted confirmation and a challenge cannot share a time step.
The test clock uses whole seconds in 30-second windows. It does not accept
codes from the window before or after the current one. Action times cannot
go backwards. Codes use the RFC 6238 SHA-1 method and have six digits.
The tests also check known eight-digit examples from that standard.
You control the clock, so you can test a time boundary without waiting.

Exit 0 means an accepted action or read command. Exit 1 means a rejected
challenge or recovery. Expect this for the steps meant to fail. Exit 2 means
bad input or a problem with the files. If you make a mistake, keep the first
event log. Start a fresh run/account-02 instead of editing state.json.

The state file must have only one file name. A hard link gives the same file
another name. A write could then change a file outside the practice folder.
The service refuses hard-linked state before it reads or changes it.
It also refuses symbolic links and Windows junctions. These are links that
point to files or folders elsewhere. Use a fresh practice folder.

After saving redacted evidence:

```powershell
python service.py clean --folder run/account-01
Remove-Variable setup, recovery, code -ErrorAction SilentlyContinue
```

Cleanup removes only that generated state file. It refuses extra files.
This does not prove the removed data can never be recovered.
No real account settings change.

## Exact worksheet rules

The separate case files show event samples. Each stands on its own.
They are not a log of events in time order. Each records id, operation,
password_ok, enrolled, proof_matches, proof_used and observed (accept/reject).
The operations are confirm, challenge and recover.

For any expected accept, the password must be correct. The proof must match
and must not have been used. Confirm also needs enrolled=false.
Challenge and recover need enrolled=true. Use matches-model if the expected
result agrees with the observed result. Otherwise, use investigate-mismatch.
Explain your comparison. A mismatch alone does not show its cause.
Unknown fields are errors. Flags must be true or false.

## Evidence, limits and sources

Save a table of challenge and recovery results. Keep the redacted evidence
output and session counts before and after recovery. Save your first worksheet
answers and name a weakness recovery still has. In your handover, state what
you ran and which step failed as expected. Explain what changed after recovery
and what a real service would still need.

This service shows state changes. It does not keep the two factors safely
apart. It has no limit on how fast requests can arrive. Its secrets are not
encrypted. It has no real clock or channel to deliver codes. It does not
resist phishing, where a fake site tricks someone into giving up a code.
It cannot safely save several actions at once and keep them after a fault.
It does not issue real session tokens. Do not expose or deploy it.
A code on this same computer does not prove use of a separate second device.
A passing script test does not show that you completed the workflow.

The authors opened these source documents when they prepared this lab.

- [RFC 6238](https://www.rfc-editor.org/rfc/rfc6238) - time-step calculation and published test vectors.
- [NIST authentication guidance](https://pages.nist.gov/800-63-4/sp800-63b.html) - authenticator lifecycle, one-time-code handling and recovery requirements. This exercise does not claim conformance.
