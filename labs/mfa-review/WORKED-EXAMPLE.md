# Worked example: Review MFA and recovery controls by account type

Save a prediction for the guided case before you read this page. These are made-up records. The answer does not assess your skill at doing this alone.

1. `helpdesk-user` has `password` and `totp`. But `enforced=false`, so use `enforce-mfa` instead of `enrol-mfa`. Recovery uses a shared mailbox. Add `repair-recovery`. The full answer is `enforce-mfa;repair-recovery`.
2. `platform-admin` has extra access rights. TOTP is set up and required. But this lab requires `security-key` for this account type. Use `use-phishing-resistant-mfa`. Different MFA methods give different protection.
3. `nightly-export` is a software account. It allows a person to sign in. It has no owner and uses a long-lived password. Its use is not monitored. Use `disable-interactive-login;assign-owner;replace-static-workload-credential;monitor-workload-use`, in that order. Being a service account does not waive these checks.
4. The exception for `emergency-owner` ends on the review date, `2026-10-23`. It is still current today. The account has an owner, monitoring and controlled storage. Its test age is 30 days. Recovery `none` is allowed in this design. These meet the other lab rules. Use `exception-current`.

In your handover, keep record gaps separate from tested sign-in failures. Cite the fields you used. Ask for checks in the real provider's system. A changed label alone does not prove that all access is safe.

Keep your first prediction. Add a correction in `notes.txt` after you compare it with the answer. State which evidence changed your view. Work through the evidence yourself. Copying an answer does not show that you understand it.
