# Pairing-format converter

`chiaki_pairing_converter.py` is an AI-assisted utility prepared during the Remote Play extension. It converts one PS5 registration from a native chiaki-ng Qt INI export into the JSON format expected by the inspected chiaki-lg v0.1.2 client. It does not contact a TV or console.

It decodes Qt escaping, checks byte-array lengths, rejects ambiguous registrations, avoids copying OAuth tokens and creates a new output file without overwriting an existing one. Diagnostics report counts and byte lengths rather than credential values. The source documents the upstream format references.

```text
python tools/chiaki_pairing_converter.py --input PRIVATE_EXPORT --account-id BASE64_ACCOUNT_ID --host PRIVATE_PS5_IP --output NEW_PRIVATE_JSON
```

Keep actual input/output outside this repository: both can contain credentials. No real input or output is published here. This converter's successful local/readback validation does not establish that streaming or every controller input works on a particular TV.

Synthetic tests are in `tests/test_chiaki_pairing_converter.py`. The converter does not replace device-specific compatibility testing.
