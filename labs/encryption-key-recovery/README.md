# Encoding, hashing and the key needed to recover a backup

Can changing how a note looks keep it secret? Does keeping a saved copy mean you
can get the original note back? A **backup** is a spare copy kept for recovery.
Use made-up text and records to work through these questions.

This lab runs on your computer. The helper changes how text is written and
compares values, as explained below. These are real checks. The file recovery
stories are made up. No real file is encrypted or decrypted. First complete the
file-integrity lab, which compares files for changes. You also need Python 3.10+.
Allow 30 minutes for the guided case and 20-30 minutes for each later case.
A person still needs to review your work and how you explain it.

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

The helper really converts Base64 and works out SHA-256 hashes. It uses tools
that come with Python. It also hashes the given dummy recovered text. Then it
compares the result with a saved digest. The encrypted-file, key and decryption
records are made up, also called synthetic. Checking them does not prove a real
restore took place. You need no real key data, account or online cloud service.
No extra tool install is needed.

A matching digest does not tell you who wrote a file. Someone who can replace
both a file and its unprotected saved digest can make the comparison look right.
A person can also hash a guessed message and compare it with a digest. A hash
therefore does not keep a short, guessable message secret. Storing passwords
safely needs a special password-hashing method, outside this lab.

## Run a small attempt

Open a terminal in this folder. Use your Python 3.10+ command (`python` below).
On Windows, the command may be `py -3`.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the three text ledgers in the attempt folder. Check which bytes the JSON
includes. Save predictions in `notes.txt`. Fill the blank decisions, reason and
evidence list in `answers.json`. Use IDs and ledger references. Only then run:

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
```

`check` compares decisions and requires written fields. A person must assess
your reasons. `analyse`, `reference/` and the worked example reveal answers.
Keep them closed while working alone. Use new attempt folders. Keep first
answers, tool output, help used and corrections. Do not put real secrets in
these records.

## Exact input and decision rules

`samples` records have a method (`base64` or `sha256`). They have a goal
(`transport`, `change-detection` or `confidentiality`). They also have exact
`source_text`, `supplied_output` and an evidence reference. Text uses UTF-8
without an added newline. JSON `\n` is one LF byte. Source text can be at most
1024 bytes. Base64 uses the standard canonical padded alphabet. It allows no
whitespace. SHA-256 uses 64 lowercase hex characters.

A sample decision is `method:matches-or-differs:fit`. The helper decodes Base64
and compares its bytes with the source. It works out SHA-256 again and compares
it with the given digest. `fits-stated-goal` means Base64 for transport or
SHA-256 for change detection. All other pairs are `wrong-purpose`. A method can
fit the goal even if the given output differs. Neither method keeps data secret.
Use a documented encryption tool for a real secrecy task. This package uses
given recovery records instead.

`keys` records have an `available`, `lost`, `disabled` or `unknown` state.
Operator access is `allowed`, `denied` or `unknown`. IDs point to inventory
records. They are not secrets. Each entry in `backups` names exactly one required
key. It states whether ciphertext is present, gives a ciphertext check and
records the attempt state. It also has a trusted `baseline_sha256` and
`restored_text`. Here, `null` means no text was given. In contrast, `""` is a
real zero-byte result. A success record with text triggers a real SHA-256 check
of that dummy text. Every attempt needs ciphertext, an available key and allowed
access. If the attempt did not succeed, restored text must be null. The helper
rejects conflicting records and duplicates. It also rejects unknown keys or
fields and badly formed encodings.

For backups, the helper reports the first condition that applies in this list.
Its output still records all the things needed for recovery:

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

The last result applies only to the given receipt and dummy content. A missing
ciphertext baseline does not block the restored-byte check. Those bytes can still
be compared with their trusted plaintext baseline. The missing ciphertext check
stays visible. A changed ciphertext record takes priority. It needs review even
if other records look good. This model has no plaintext copies, other wrapping
keys, caches, key copies or outside recovery path. Here, "unavailable" means
unavailable in this inventory. It does not mean recovery is always impossible.
A real provider may document exceptions or recovery steps for its service.

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

These check the helper and fixtures. They do not show real use of an encryption
tool or prove learner skill. For cleanup, save the evidence you want first.
Remove only your own new `run/attempt-*` folders. No host setting needs to be
restored. Keep original fixtures and first attempts unchanged.

## Primary sources and limits

Opened 25 October 2026:

* [RFC 4648, sections 4, 10 and 12](https://www.rfc-editor.org/rfc/rfc4648)
  defines Base64 and gives test examples. It states that encoding does not keep
  data secret.
* [NIST FIPS 180-4: Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
  defines digests used to detect changes. This lab uses SHA-256 from Python's
  standard library. You do not build a hash algorithm here.
* [NIST SP 800-57 Part 1 Revision 5](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
  explains how to manage keys. Key data needs protection and a plan for each
  stage of its use. This includes access and recovery.
* [AWS KMS: Delete an AWS KMS key](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html)
  gives a real example of how reading encrypted data depends on keys. It
  distinguishes deleting a key from disabling it and lists exceptions. This lab
  does not model every KMS state or give cloud deletion steps.

The helper does not check an encryption algorithm or whether tools work together.
It checks no real ciphertext, authentication tag, cryptographic randomness or
provider account state. Made-up success and failure receipts are task inputs.
They do not claim that the work was done.
