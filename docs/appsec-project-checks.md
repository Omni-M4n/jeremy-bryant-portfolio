# Application security project checks

Checked on 7 November 2026 with Python 3.12 on Windows.

| Project | Repeatable check | Result |
| --- | --- | --- |
| Access Notes | `python -B -m unittest -v` in `projects/access-notes` with its requirements installed | 17 tests passed |
| Scan Report | `python -B -m unittest -v` in `projects/scan-report` | 24 tests passed |
| Source download | `node --test tests/source-downloads.test.mjs` from the repository root | Includes project code and guides. Excludes runtime databases, sessions and draft project folders. |

The web app was also checked through a browser. Login, note creation, logout
and a second login worked. Sam's account could not open the new note from
Alex's account. The result was the same missing-note page used for an unknown
ID. The browser check exposed a form-origin issue with the original referrer
policy. The policy was corrected and the normal login flow was checked again.

A separate code review found a Unicode form-token error and an out-of-range
note-ID error. Both were fixed and regression tests now cover those requests.
The report was also checked with eight writers targeting the same output
name. Exactly one complete output was created. The other writers received
a refusal. The supplied HTML report was viewed in a browser.

These results cover local software behaviour and the supplied synthetic cases.
The projects use fictional data. They do not establish production readiness
or that the learner can explain, adapt or rebuild the code independently.
Use the project practice guides to collect that separate learning evidence.
