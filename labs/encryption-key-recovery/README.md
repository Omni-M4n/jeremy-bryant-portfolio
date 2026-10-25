# Encoding, hashing and the key needed to recover a backup

Can changing how a note looks keep it secret? Does keeping a saved copy mean you
can get the original note back? A **backup** is a spare copy kept for recovery.
Use made-up text and records to work through these questions.

This lab runs on your computer. The helper does real text-conversion and
comparison checks, explained below. The stories about recovering files are made
up. No real file is encrypted or decrypted. First complete the file-integrity
lab, which compares files for changes. You also need Python 3.10+. Allow 30
minutes for the guided case and 20-30 minutes for each later case. Your own work
and ability to explain it still need a person's review.

## Vocabulary and the right question

| Concept | Purpose and limit |
| --- | --- |
| Readable text, or plaintext | The message before encryption, such as "bring a pencil". It is also the text you want to get back. |
| Secrecy, or confidentiality | Keeping a message from people who should not read it. For example, only the chosen reader should see a private note. |
| Key, in this lab | Secret data used to protect a file and read it again. Think of a key that fits one lock. The key's name is not the key itself. |
| Encryption and decryption | Encryption uses a key to turn readable text into encrypted text. Decryption uses the matching key to get the readable text back. This lab does neither operation. |
| Encrypted text, or ciphertext | The result of encryption. It is meant to hide the message from someone who lacks the right key. |
| Permission | Approval to do something, such as use a key. A key may exist even when a particular person is not allowed to use it. |
| Byte and UTF-8 | A byte is a small unit of stored data. UTF-8 is a rule for turning text into bytes. The letter A uses one byte; some characters use more. |
| Encoding and Base64 | Encoding changes how data is written so it can be sent or stored. Base64 writes `cat` as `Y2F0`. Anyone can reverse that rule without a secret key, so it provides no secrecy. |
| Cryptographic hash, or digest | A fixed-length check value calculated from a file's bytes. SHA-256 is one method. Compare it with a saved value to check for changes; you cannot decode the digest to recover the file. |
| Authenticated encryption | Encryption designed to detect unwanted changes to the encrypted data as well as hide its contents. This lab does not use it. |
| Key ID | A label for a key, such as `key-2026`. It points to the key data but does not contain it. A newly made replacement key is not a copy of the old key. |
| Trusted baseline | A saved value you trust for comparison, such as a digest kept safely before a file was damaged. This lab assumes that trust; calculating a hash cannot prove it. |
| Recovery dependency | Something you need to get a file back. For example, you may need both the right key and permission to use it. |
| Receipt or ledger | A written record of an action or a list of records. Here, these records are made up for practice. |

The helper really converts Base64 and calculates SHA-256 hashes using tools that
come with Python. It also hashes the supplied dummy recovered text and compares
the result with a saved digest. The encrypted-file, key and decryption records
are fictional, also called synthetic. Checking them does not prove that a real
restore took place. You need no real key data, account, installation or online
cloud service.

A matching digest does not tell you who wrote a file. Someone who can replace
both a file and its unprotected saved digest can make the comparison look right.
A person can also hash a guessed message and compare it with a digest. A hash
therefore does not keep a short, guessable message secret. Storing passwords
safely needs a special password-hashing method, outside this lab.

## Run a small attempt

Open a terminal in this directory. Use your Python 3.10+ command (`python` below;
`py -3` may be the Windows command).

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the three text ledgers in the attempt folder and the JSON byte boundaries.
Save predictions in `notes.txt`; fill the blank decisions, explanation and
evidence list in `answers.json`. Use IDs and ledger references. Only afterwards:

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
```

`check` compares decisions and requires nonempty written fields; a person must
assess the reasoning. `analyse`, `reference/` and the worked example reveal
answers. Keep them closed for independent work. Use fresh attempt folders to
preserve first answers, tool output, help used and corrections. No real secret
belongs in these records.

## Exact input and decision rules

`samples` records have a method (`base64` or `sha256`), goal (`transport`,
`change-detection` or `confidentiality`), exact `source_text`, `supplied_output`
and evidence reference. Text uses UTF-8 without an added newline. JSON `\n` is
one LF byte. Source text is at most 1024 bytes. Base64 uses the standard canonical
padded alphabet, with no whitespace; SHA-256 uses 64 lowercase hex characters.

A sample decision is `method:matches-or-differs:fit`. Base64 is decoded and its
bytes compared with the source. SHA-256 is recomputed and compared with the
supplied digest. `fits-stated-goal` means Base64 for transport or SHA-256 for
change detection; all other combinations are `wrong-purpose`. A method can fit
the goal while the supplied output differs. Neither supported method fits
confidentiality. Choose a documented encryption tool for a real confidentiality
exercise; this package intentionally uses supplied recovery evidence.

`keys` records contain `available`, `lost`, `disabled` or `unknown` state and
`allowed`, `denied` or `unknown` operator access. IDs are inventory references,
not secrets. `backups` name exactly one required key, ciphertext presence, a
supplied ciphertext check, an attempt state, a trusted `baseline_sha256`, and
`restored_text`. `null` means no text supplied; `""` is an actual zero-byte result.
A reported success with supplied text causes a real SHA-256 comparison of that
dummy text. Any attempt requires present ciphertext, an available key and allowed
access; non-success attempts must have null restored text. Contradictions,
duplicates, unknown keys/fields and malformed encodings are rejected.

For backups the helper reports the first applicable condition in this order;
its observation retains every dependency:

| Condition | Decision |
| --- | --- |
| No ciphertext | `ciphertext-missing` |
| Ciphertext check differs | `ciphertext-changed-investigate` |
| Required key marked lost | `required-key-unavailable` |
| Required key disabled | `key-disabled-review-recovery` |
| Key state unknown | `key-state-unknown` |
| Access denied / unknown | `key-access-denied` / `key-access-unknown` |
| No attempt | `restore-unproven` |
| Attempt failed | `decrypt-failed-investigate` |
| Success, supplied restored bytes differ | `restored-content-mismatch` |
| Success, no restored text supplied | `restored-content-unverified` |
| Success and restored digest matches baseline | `restore-verified-in-supplied-evidence` |

The last result is scoped to the supplied receipt and dummy content. A missing
ciphertext baseline does not prevent comparing restored bytes with their trusted
plaintext baseline; the absent ciphertext check remains visible. A changed
ciphertext record takes priority and requires investigation, even if other
records look encouraging. The model has no plaintext copies, alternate wrapping
keys, caches, replicas of key material or external recovery path. "Unavailable"
is bounded to this inventory, not a universal assertion that recovery is
mathematically impossible. A provider may have documented exceptions and
service-specific recovery procedures.

## Evidence and a recovery plan

Explain what encoding, hashing and encryption are for. Save your byte comparisons.
Make a table of what each recovery needs, which record supports it and what is
still missing. Then write a short plan for the made-up case by answering:

* Which exact key does this saved file need?
* Who looks after that key, and who has permission to use it?
* Where is a protected spare copy of the key kept? What record shows it exists?
* Which new folder would hold the recovered files, without replacing originals?
* Which trusted saved digest would you use to check the recovered text?
* When should someone repeat the recovery check?

If a record does not answer a question, write "unknown" and name the next check.
Do not invent spare keys. Describe a proposed step as a plan, not completed work.
Never put real key data in the plan or leave an unprotected key beside its
encrypted file.

When you hand over your work, explain: "This is what the recovery still needs.
This record supports my answer. This is the next check an approved person could
make." Keep the difference between made-up receipts and checks you actually ran.

```text
python test_lab.py
python lab.py verify
```

These validate the helper and fixtures. They do not demonstrate practical use of
an encryption tool or learner mastery. Cleanup means removing only your own
new `run/attempt-*` folders after retaining the evidence you want. There is no
host setting to roll back. Keep original fixtures and first attempts unchanged.

## Primary sources and limits

Opened 25 October 2026:

* [RFC 4648, sections 4, 10 and 12](https://www.rfc-editor.org/rfc/rfc4648)
  specifies Base64, provides test vectors and states that encoding offers no
  computational confidentiality.
* [NIST FIPS 180-4: Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
  defines message digests for detecting changes. This lab uses SHA-256 through
  the standard library; it is not a cryptographic implementation exercise.
* [NIST SP 800-57 Part 1 Revision 5](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
  supplies the key-management context: key material needs protection and lifecycle
  planning, including availability and recovery.
* [AWS KMS: Delete an AWS KMS key](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html)
  provides a real service example of decryption dependence on key material,
  distinguishes deletion from disabling and documents exceptions. This lab is
  not a KMS state machine and gives no cloud deletion instructions.

No encryption algorithm, tool compatibility, real ciphertext, authentication tag,
cryptographic randomness or provider account state is verified. Fictional
success/failure receipts are exercise inputs, never a claim of completed work.
