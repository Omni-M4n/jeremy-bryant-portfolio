# Can you recover the right password records?

A club has separate accounts for its library, garden and bookings. Different
passwords help limit a problem to one account. A backup also needs to work
when the usual file cannot be used. You will practise both checks with fake
accounts.

This is a new core topic. Do mfa-review first. Allow 20 minutes for the local
file exercise. Allow 20-30 minutes for the vault app exercise if KeePass 2 is
already on your computer. This lab does not include installing it.

## Words used here

A **password vault** is a protected store of passwords. A **master password**
unlocks it. A **backup** is a copy kept for recovery. **Restore** means putting a
usable copy back. **Plaintext** is readable data without encryption.
**Encryption** protects data using a key. A **recovery path** is the set of
things you need to regain access.

## Set up a first attempt

Use Python 3.10 or newer, already on your computer. It works on Windows,
macOS or Linux. You need no extra packages, cloud account or network link.
A terminal is where you type commands. From the project folder, open one in
`labs/password-vault-recovery`. The commands use `python`. If your Python 3
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


## Part A: perform a local file recovery

The supplied helper is a **plaintext dummy store, not a password manager**.
It makes three different fake passwords. It copies bytes, keeps the original
and restores from the copy. Use it to practise how to handle and check files.
It cannot show that you can unlock an encrypted vault or store secrets safely.

From this lab folder, run:

```text
python vault.py init --folder run/vault-01
python vault.py backup --folder run/vault-01
python vault.py hold --folder run/vault-01
python vault.py restore --folder run/vault-01
python vault.py verify --folder run/vault-01
python vault.py export --folder run/vault-01
```

Expect three entries. Backup, restore and export report whether the copied
bytes match. Hold moves the active file to held-original.json. This keeps
the original. Verify must report unique=true and matches_backup=true.
It also gives a SHA-256 file fingerprint, a value made from the file's bytes.
Matching fingerprints help show that the bytes match. The output says
real_vault_unlock is not tested.

Look at export.json on your computer. You can read the fake passwords in it.
Do not include its contents or the store in a handover. Save only redacted
command results and your reasons. Redacted means secret values are left out.
The backup is in the same folder. It cannot protect you if that folder or its
disk is lost.

After saving redacted evidence, remove only these generated files:

```text
python vault.py clean --folder run/vault-01
```

Cleanup refuses unexpected files. If a step fails, keep its error and start
a fresh named folder. It does not overwrite an existing store. Removing these
files does not prove that their data can never be recovered.

## Part B: use an existing encrypted vault app

This part needs KeePass 2 already on your computer. If you do not have it,
record **not run: encrypted-vault recovery**. Part A does not replace this
part's evidence.

1. Create a new folder named run/vault-app-01. In KeePass choose File > New. Save only a new training.kdbx there. Use a fresh master passphrase just for training. Do not reuse a real password. Do not open or import a real vault.
2. Add three entries named library.test, garden.test and club.test. Use the built-in password generator for each. Set it to at least 20 characters. Check on your computer that the three passwords differ. Do not copy their values to notes.
3. Save and close the database. Copy training.kdbx to backup.kdbx in the exercise folder. Rename training.kdbx to held-original.kdbx. Never delete the original as part of this test.
4. Open backup.kdbx with the training passphrase. Check that all three entries open. Save a checklist with secret values left out. Include the file used, entry count, whether unlock worked and what you needed. Do not capture password fields or keys.
5. Close it. For a real recovery plan, where would you keep an encrypted backup and its unlock tools? Write how to keep them apart. This exercise's copy is in the same folder, so it does not test that protection. Do not move real secrets.
6. If you inspect export behaviour, use only this dummy database. Choose File > Export. Choose a readable CSV or XML format and save inside run/vault-app-01. Inspect it on your computer. Note that you can read its values. Then delete only that dummy export. Keep its contents out of your evidence.
7. Close the training database. Keep your evidence with secrets removed. When you no longer need the dummy files, remove only those in run/vault-app-01. Use the file manager.

A key file is an extra part that may be needed to unlock a vault. This beginner
exercise uses just a training passphrase. Losing a required part can stop you
from opening a backup even if its bytes are intact. Keep a copy of your recovery
instructions outside the locked vault.

## Exact worksheet rules

Input entries have id, account, secret_label, generated and length.
Labels stand for fake password values. Do not put passwords in these test files.
If a label is repeated, use reused. If generated is false, add
generation-unverified. If length is below 20, add below-practice-length.
Join flags with + in that order. If none apply, use meets-practice-checks.
Twenty characters is the target chosen for this exercise. It is not a rule
for all passwords.

The backup object has format (encrypted/plaintext), copy_exists, unlock_test,
separate_location and recovery_in_same_store. Check findings in this order.

1. Use copy-missing if there is no copy.
2. Add restore-untested if unlock has not been tested.
3. Add same-location-risk if the copy is not in a separate place.
4. Add plaintext-exposure if the format is plaintext.
5. Add circular-recovery if the recovery steps are in the same store.

Join findings with +. If none apply, use meets-practice-checks.
The helper rejects an unlock test or separate copy location when no copy exists.
Those claims conflict with each other. It also rejects unknown fields and
invalid account names.

## Evidence, limits and sources

In your handover, show that the passwords differ without showing their values.
Include your backup and restore result, what recovery needs and how you handled
the export. Include the worksheet and record IDs. State which parts you ran.
Report the file exercise, encrypted-vault exercise and recovery on a separate
device as separate items. Mark each as run or not run. The supplied helper
tests do not show that you completed either workflow.

The generated flag and length do not prove a password is strong. A matching
file hash shows that files have the same bytes. It does not show that the
contents are private or that the vault will unlock. It cannot prove a recovery
plan will work. This lab changes no real account.

The authors opened these source documents when they prepared this lab.

- [KeePass generator](https://keepass.info/help/base/pwgenerator.html) - generates passwords from chosen character sets.
- [KeePass master key](https://keepass.info/help/base/keys.html) - all required key components are needed to open a database, and key-file backups need protection.
- [KeePass import/export](https://keepass.info/help/base/importexport.html) - formats have different fields and portability limits.
