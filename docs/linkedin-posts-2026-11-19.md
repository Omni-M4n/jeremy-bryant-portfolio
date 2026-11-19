# LinkedIn post set — 19 November 2026

These three first-person cybersecurity notes are grounded in the public portfolio and lab sources. They contain no private review notes.

## Reachability Is Not Administrator Access

A page appeared on my LG television. The evidence supported two narrow claims: the television could reach the test page and display it. It did not establish root access, successful authentication, or a secure management path.

This came from a personal, owner-controlled home lab using an LG webOS television and existing community software. The first launch route, `adoverlayex`, failed to load the page. A second route, `voiceweb`, loaded it successfully. That difference helped isolate the problem, but loading the page remained an intermediate result.

The project tested the next questions separately:

- Was administrator access verified independently?
- Did key-based SSH replace the potential password-free Telnet path?
- Did management access still work after a restart?
- Could the stock LG Home interface be restored if needed?

The recorded checks supported those specific outcomes: root SSH was verified separately, SSH used a key and pinned host identity, Telnet was disabled, management access was checked after restart, and the LG Home fallback was exercised.

These are historical results from one owned device, not a live status report. The project used existing research and software; it was not an original exploit discovery or a comprehensive security assessment.

The practical lesson is to define a pass/fail question for every layer. A response can prove reachability without proving authentication. Authentication can succeed without proving the required privilege. A configuration can work once without proving persistence or recovery.

Keeping those claims separate makes troubleshooting clearer and prevents an encouraging intermediate result from becoming a conclusion the evidence cannot support.

Sources: [LG webOS home-lab case study](https://jeremy-bryant.pages.dev/lg-webos-lab/) · [RFC 4252](https://www.rfc-editor.org/rfc/rfc4252)

## A Backup Is Not Yet a Restore

I ran a small local restore drill with two expected files. The restore operation completed, but only one file came back.

The scenario used disposable dummy data. I recorded the original two-file inventory, created a deliberately incomplete backup, and then changed the current version of one file. The backup was restored into a new folder rather than over the working data.

The receipt showed three useful results:

- `item-01.txt` returned in its older baseline version, as expected from the backup.
- `item-02.txt` was missing.
- No unexpected files appeared in the restored folder.

That made the failure specific. The restore mechanism copied what the backup contained, but the recovered set did not meet the required inventory.

The method is straightforward to repeat:

1. Record the complete expected inventory.
2. Restore into a separate, empty location.
3. Compare every expected file with the restored set.
4. Report missing and unexpected files independently.
5. Confirm which saved version was recovered.
6. Measure copying and verification separately.
7. Assess completeness, version age, and the time target as separate requirements.

The receipt recorded copy and verification durations independently. Those measurements help describe this local operation, but timings from two tiny files cannot establish disaster-recovery performance. They exclude application startup, permissions, infrastructure provisioning, key recovery, network transfer, and operational coordination.

The practical takeaway is that a successful copy command answers only one question. Recovery confidence requires evidence that the expected data returned, the correct version was recovered, and the result meets the needs defined before the test.

Sources: [Public restore-drill lab](https://jeremy-bryant.pages.dev/lab-files/restore-drill/) · [NIST SP 800-34 Rev. 1](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)

## Removing a Secret Is Only Half the Response

A secret disappeared from the current configuration. The problem was not gone.

In this fictional offline lab, a dummy export token was replaced in a local configuration with a secret-store reference. That reduced one exposure path. But the exact marker still appeared in a removed line within a shared diff and in a public debug log. The case also recorded the credential as active.

That creates two separate decisions.

First, credential validity: contain the exposure, revoke the active value, and replace or rotate it while keeping the required service working. Editing a file cannot make copied credentials stop authenticating.

Second, retained copies: identify who can see each artifact, preserve necessary incident or audit evidence under restricted access, and address unnecessary exposed copies through approved retention, redaction, or repository-remediation processes. Removing one visible copy cannot guarantee that every copy has been recalled.

The lab makes the reasoning testable. For each dummy secret:

- check the exact marker;
- identify the artifact—configuration, diff, or log;
- record its audience—local, shared, or public; and
- compare that visibility with its state—active or revoked.

An active credential in shared or public material requires containment and revocation, not just tidier configuration.

This was not a real incident or assessed professional work. The helper searches only for listed exact markers in supplied files. It can miss encoded, split, reformatted, or unknown secrets, and it never contacts a service to confirm that revocation succeeded.

The practical takeaway is to ask two questions: “Can this credential still work?” and “Where do copies remain?” They require coordinated but different actions—and necessary evidence should be protected, not casually destroyed.

Sources: [Public secret-handling lab](https://jeremy-bryant.pages.dev/lab-files/secret-handling/) · [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
