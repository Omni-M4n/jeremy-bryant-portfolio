# Worked example: the guided dummy note

Read after saving your first prediction. The source is exactly three UTF-8 bytes,
hex `61 62 63`, with no newline. This is dummy text, not a password.

1. `transforms.txt T1` supplies `YWJj`. Standard Base64 decoding gives `abc`,
   hex `616263`, exactly the source. Anyone can apply that public decoding rule;
   there is no key. The correct comparison does not meet the stated secrecy
   goal. `encoded-note` is `base64:matches:wrong-purpose`.
2. T2 supplies SHA-256
   `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`.
   Computing SHA-256 over those exact three bytes gives that digest. A digest is
   appropriate for this stated comparison goal, assuming the baseline is
   trusted. `digest-note` is `sha256:matches:fits-stated-goal`. This does not prove
   origin, preserve a recoverable copy of the message or hide a guessable message.
3. `restore-ledger.txt R1` reports an intact encrypted copy requiring `blue-v1`.
   `key-ledger.txt K1` lists that exact key as available with allowed access.
   R1's explicitly fictional decryption receipt reports success and supplies
   `abc`. The helper hashes that supplied text and compares it with the stated
   trusted plaintext baseline; they match. `blue-copy` is
   `restore-verified-in-supplied-evidence`.

The helper really performed the Base64 and SHA-256 operations, but did not decrypt
anything. There is no ciphertext or key material in the package. The evidence
supports a claim about a supplied synthetic receipt plus a dummy content check,
not a real encrypted-file restore or future recovery capability.

An appropriate plan records that this object needs `blue-v1`, which authorised
custodian can recover it, where a protected recovery copy should be held, and how
a later isolated restore would be compared with the trusted baseline. Those
arrangements are not demonstrated by K1; label them as next checks. Do not
substitute a key ID, a newly generated replacement key, a hash or a Base64 string
for the required key material.
