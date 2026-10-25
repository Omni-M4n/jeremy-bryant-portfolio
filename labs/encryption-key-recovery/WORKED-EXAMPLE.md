# Worked example: the guided dummy note

Read this after saving your first prediction. The source is exactly three UTF-8
bytes, hex `61 62 63`. It has no newline. This is dummy text, not a password.

1. `transforms.txt T1` gives `YWJj`. Standard Base64 decoding gives `abc`,
   hex `616263`. This matches the source. Anyone can use that public decoding
   rule. There is no key. A correct comparison does not meet the stated secrecy
   goal. Thus `encoded-note` is `base64:matches:wrong-purpose`.
2. T2 supplies SHA-256
   `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`.
   Hashing those exact three bytes gives that digest. A digest fits this
   comparison goal if the baseline is trusted. Thus `digest-note` is
   `sha256:matches:fits-stated-goal`. This does not prove who wrote the message.
   It does not keep a copy you can recover or hide a message someone can guess.
3. `restore-ledger.txt R1` reports an intact encrypted copy that needs `blue-v1`.
   `key-ledger.txt K1` lists that exact key as available with allowed access.
   R1's made-up decryption receipt says it succeeded and gives `abc`.
   The helper hashes that given text. It compares the digest with the trusted
   plaintext baseline, and they match. Thus `blue-copy` is
   `restore-verified-in-supplied-evidence`.

The helper's Base64 and SHA-256 checks are real. It does not decrypt anything.
This package has no ciphertext or key data. The evidence covers a made-up
receipt and a dummy content check. It does not show a real encrypted-file restore
or prove that a later recovery will work.

A plan should state that this object needs `blue-v1`. Name who is approved to
recover the key. State where a protected spare copy should be kept. Explain how
to check a later isolated restore against the trusted baseline. K1 does not
prove that these plans are in place. Mark them as next checks. The required key
data cannot be replaced by a key ID, a newly made replacement key, a hash or a
Base64 string.
