# Worked example: Small SSH server configuration review

Try the guided case before reading this page. Use `python lab.py prepare --scenario guided --out run/worked-01` if you need a fresh ignored copy.

The guided text has PermitRootLogin prohibit-password. This still permits some root authentication methods, so it differs from the lab requirement no. PasswordAuthentication yes also differs. Keyboard-interactive no, public keys yes, empty passwords no and MaxAuthTries 4 match. access-route says public-key-method-enabled because that method is explicitly enabled; it does not say that a working key or recovery login exists. The exercise never loads host configuration or starts a server.

The reference decision fields for guided are:

```json
{
  "permitrootlogin": "differs-from-lab-baseline",
  "passwordauthentication": "differs-from-lab-baseline",
  "kbdinteractiveauthentication": "matches-lab-baseline",
  "pubkeyauthentication": "matches-lab-baseline",
  "permitemptypasswords": "matches-lab-baseline",
  "maxauthtries": "matches-lab-baseline",
  "access-route": "public-key-method-enabled"
}
```

Now open `python lab.py analyse --case run/worked-01/case.json` and compare observations, not only labels. Record one difference between your first prediction and the reference. If there was no difference, explain the rule that produced each decision rather than copying the label.

Handover prompt: explain what this evidence establishes, cite its exact IDs or lines, give a plausible alternative or remaining uncertainty, and name the smallest next check. Record any help used. A correct label by itself is not evidence of independent understanding.
