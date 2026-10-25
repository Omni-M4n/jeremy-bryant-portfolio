# Worked example: Small SSH server configuration review

Try guided before reading this page. To make a fresh copy, use `python lab.py prepare --scenario guided --out run/worked-01`.

The guided text sets PermitRootLogin to prohibit-password. This still allows some ways to log in as root. It differs from the lab's required value, no. PasswordAuthentication yes also differs from the baseline.

Four settings match: keyboard-interactive no, public keys yes, empty passwords no and MaxAuthTries 4. The access-route result is public-key-method-enabled. The text enables that method. It does not show that a working key or recovery login exists. The exercise reads no host settings and starts no server.

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

Run `python lab.py analyse --case run/worked-01/case.json` after saving your own answer. Compare the facts, not just the labels. Keep the first answer and add corrections. If it matched, explain the rule behind each result.

For a handover, state what the evidence shows. Cite exact IDs or lines. Give one other explanation or remaining doubt, then the smallest next check. Include help used. A correct label alone does not show that you understand it.
