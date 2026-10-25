# Check a small backup before choosing it

A recent backup may still miss a file or contain changed bytes. In this lab, check the file list, age and bytes of tiny fictional copies. Then choose a copy that meets the case's rules.

The tool decodes the supplied file data in memory and checks its hashes. It does not restore a real disk or app. These are practice materials, not copied coursework or evidence of learner skill.

## Before you start

Allow **30–45 minutes**, or split the work into short sessions. Spend 5 minutes reading, 10 on evidence and predictions, and 10 on checks and notes. Use the last 5–20 minutes for another case.

You need Python 3.10 or later, a terminal and a text editor. Python's standard library is enough. You need to open files, read a small table and save notes. You do not need to write code, use admin rights, install Linux or open a cloud account. Earlier network or Wireshark practice may help, but is not required.

These terms will help:

- **RPO:** recovery point objective. It sets how much recent data loss is acceptable. Here, it is the maximum allowed age of a copy.
- **RTO:** recovery time objective. It sets how long recovery may take. That is a different check from RPO.
- **Retention:** how long a copy is kept.
- **SHA-256:** a hash used here to compare the exact file bytes.
- **Restore test:** trying a recovery and checking its result. Always state what was actually restored.

## Read the case

The case JSON is the one source of input. The supplied files are guided.json, changed.json and challenge.json. The artifacts field is empty, so there is no second copy to edit. Work on a prepared copy below run/. The analyser never runs the evidence text as code.

The data section has:

- recovery_time: the time of the recovery check, in UTC with seconds.
- rpo_hours: a whole number from 0 to 168.
- required_sha256: the required filenames and their expected SHA-256 hashes. These are simple .txt or .csv names, with no folder path.
- backups: the copies to check. Each has an ID, captured_at, retained_until and payload_base64.

Base64 stores bytes as text. Each payload name must be in the required file list, but a copy may lack some required files. Bad base64, future capture times and invalid retention periods are rejected. The expected hashes are supplied in the case. The tool does not fetch them from your disk.

## Use the rules

Decode each copy's payloads and measure their SHA-256 hashes. Compare at recovery_time. A copy expires exactly at retained_until. Its age in seconds is recovery_time minus captured_at.

Use the first rule that fits, in this order:

1. **retention-expired:** the retention period has ended.
2. **required-scope-missing:** at least one required file is missing.
3. **restore-bytes-mismatch:** at least one measured hash differs from its expected hash.
4. **rpo-exceeded:** the copy is older than the allowed RPO.
5. **qualified-synthetic-copy:** all those checks pass for this fictional copy.

Age exactly equal to the RPO still meets the limit. The decision uses the first failure, but the observations show all measured file, hash and age results.

For the recovery decision, choose the most recent copy that qualifies. Use `select:<backup-id>`, replacing `<backup-id>` with its exact ID. For example, use `select:copy-a` for a selected copy named copy-a. If capture times tie, choose the greatest ID in case-sensitive string order. This is not numeric order. Use `no-qualified-copy` if no copy qualifies.

## Run the exercise

Open a terminal in this lab folder. Use your Python command (`python`, or `py -3` if that is how Python is installed). The examples use `python`.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
python inspect_payloads.py --case run/attempt-01/case.json
```

The inspector shows each file's UTF-8 text, exact bytes in hexadecimal, byte length and measured SHA-256. If the bytes are not valid UTF-8, decoded_utf8 is null. The hexadecimal form still shows the exact bytes.

The inspector gives measurements only. It does not call the analyser, label a match or choose a copy. It decodes the embedded dummy data in memory. It writes no recovered files and runs no payload text. Exit 0 means it produced measurements. Exit 2 means bad input or a file problem. With no --case, it uses the guided fixture. An explicit --case path starts from your terminal's current folder.

Before you open the answer:

1. Compare each measured sha256 with that filename in required_sha256 in case.json.
2. Check for missing required files.
3. Use the case timestamps to work out age and retention.
4. Record these measurements. Predict each decision in run/attempt-01/answers.json.
5. Add your explanation and exact evidence references, such as b1/notes.txt and its hash.
6. In notes.txt, separate facts, your interpretation, remaining doubt, a next check and help used.

Then check the saved answer:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py test_inspect_payloads.py
python lab.py verify
```

Use the matching attempt folder in show, inspect_payloads.py, analyse and check for each later case. Run the inspector before saving your prediction. Open analyse only afterwards.

The prepare command refuses an existing folder. Its --out path starts from this lab and must stay below run/. Explicit input paths start from your terminal's current folder. If you omit --case, analyse and show use the guided fixture.

Exit 0 means the command worked or the decisions match. Exit 1 means a mismatch or missing written fields. Exit 2 means bad input or a file problem. The checker checks decisions and the presence of text. A person must judge its quality. The verify command checks the supplied examples, not learner skill.

## Save the result and state its limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. Give the question, conclusion, two exact evidence references, one limit or other explanation, and a next check. Record help used, including the worked example. A matching label does not prove understanding or work experience.

This check handles only dummy bytes held in memory. It does not restore a real backup, disk file or app. A saved payload for an expired copy does not prove that copy would still be available. The model trusts the supplied retention dates. It does not check media health, encryption keys or a full recovery process.

Read WORKED-EXAMPLE.md after your first prediction. Use DRILLS.md for less support on later attempts. Do not change a real host or treat this small check as proof that a real backup works.

## Primary reference

This source explains recovery planning. The input format and decision rules belong to this lab. The link was checked on 23 October 2026. You can run the lab offline.

- [NIST contingency planning guidance, updated revision](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
