# Worked example: Review MFA and recovery controls by account type

Open this after saving a prediction for the guided case. The reference explains
these fictional records; it does not assess your independent performance.

1. `helpdesk-user` has `password` and `totp`, but `enforced=false`. Record
   `enforce-mfa`, not `enrol-mfa`. Its recovery is a shared mailbox, so add
   `repair-recovery`: `enforce-mfa;repair-recovery`.
2. `platform-admin` is privileged. TOTP is enrolled and enforced, but this
   fictional privileged-account policy requires `security-key`. Use
   `use-phishing-resistant-mfa`. This does not claim all MFA methods are equal.
3. `nightly-export` is a service identity with interactive login, no owner,
   password-based long-lived credentials, and no monitoring. In order, use
   `disable-interactive-login;assign-owner;replace-static-workload-credential;monitor-workload-use`.
   Declaring it a service identity is not an exemption from these controls.
4. `emergency-owner` has a dated exception expiring on the review day,
   `2026-10-23`. It remains current today. The named owner, monitoring,
   controlled storage and 30-day test meet this model's other conditions.
   Recovery `none` is allowed for this emergency design. Use `exception-current`.

The handover should distinguish an observed inventory gap from a verified login
failure. Cite the actual fields and request provider-specific validation rather
than claiming the accounts are globally secure after a label changes.

After comparison, keep your original prediction and add a correction in
`notes.txt`. State the evidence that changed your judgment. Copying the answer
without reconstructing the evidence leaves independent understanding unassessed.
