# Small SSH server configuration review

Review a deliberately small SSH server configuration against a fictional explicit baseline and notice first-value precedence and access-route gaps.

This is an original, fictional, offline exercise for an introductory security learner. It is independent practice, not copied coursework or a claim of professional experience. Completion and competence remain unassessed.

## Before you start

Allow **30-45 minutes**: 5 minutes reading, 10 inspecting and predicting, 10 checking and explaining, and 5-20 for a changed or independent case. You need Python 3.10+ (standard library only), a terminal and a text editor. Comfort opening files, reading a small table and basic evidence notes is enough; programming, administrator rights, a Linux installation and cloud accounts are unnecessary. Previous introductory network or Wireshark practice is useful but not required.

> **Vocabulary:** sshd: the SSH server. Directive: a configuration keyword/value. Public-key authentication: a method using possession of a private key, with server authorisation also required. Keyboard-interactive: an authentication mechanism distinct from PasswordAuthentication. Precedence: which repeated value takes effect.

## Evidence and exact rules

The case JSON is the single authoritative input. Fixtures are guided.json, changed.json and challenge.json. All data is synthetic; artifacts is empty to avoid competing editable copies. Edit only a prepared run copy. The analyser is a pure calculation and never executes evidence text.

data.config is the authoritative raw configuration text. The only supported directives are PermitRootLogin, PasswordAuthentication, KbdInteractiveAuthentication, PubkeyAuthentication, PermitEmptyPasswords and MaxAuthTries. Keywords are case-insensitive; values are case-sensitive. Lines must be one plain keyword and value, with empty lines and whole-line # comments allowed. Quoting, inline comments, Match, Include, unknown directives and other complex syntax are rejected. This is deliberately narrower than sshd_config.

For supported directives, first occurrence wins and later occurrences are reported as ignored. The fictional baseline is root/password/keyboard-interactive/empty-password settings no, public-key setting yes, and MaxAuthTries 1-4. MaxAuthTries accepts 1-100 for comparison. Each setting is matches-lab-baseline, differs-from-lab-baseline or missing-explicit-setting. No missing default is guessed. access-route is insufficient-explicit-method-settings when any of the three authentication settings is missing; otherwise public-key-method-enabled if keys are enabled, alternative-method-enabled if only another supported method is enabled, or no-supported-method-enabled if all three are off.

## Run the exercise

Open a terminal in this lab folder. Use your Python command (`python`, or `py -3` if that is how Python is installed). Commands below use `python` consistently.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. In run/attempt-01/answers.json, fill each decision with an exact label from the rules; add an explanation and evidence references such as record IDs or configuration line numbers. In notes.txt, separate observation, interpretation, uncertainty, next check and help used. Save your prediction before opening the answer.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

For changed/challenge use the corresponding attempt folder in show/analyse/check. prepare refuses an existing output folder. --out is relative to this lab and must be below run/; explicit input paths are relative to your terminal directory. analyse/show default to the guided fixture if --case is omitted. Exit 0 means command success or decision match; 1 means differences/incomplete written fields; 2 means invalid input or a filesystem problem. The checker verifies decision fields and the presence of writing, not the quality of reasoning. verify checks shipped examples, not learner mastery.

## Deliverable and limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. Deliver a short handover: the question, your conclusion, two precise evidence references, one alternative explanation or limitation, and the next evidence you would request. State whether you used the worked example and whether you completed a fresh case unaided. Do not describe an automated match as assessment or professional experience.

Only six explicit directives are modelled. Missing settings are unknown here; no version-specific defaults are assumed. Match, Include, unknown directives and complex syntax are rejected. First occurrence wins for these supported directives. This text review is not sshd validation and cannot establish keys, PAM behaviour, network exposure or a working recovery login. No host configuration was read or changed.

Use WORKED-EXAMPLE.md after making a first prediction, and DRILLS.md for progressively less support. Do not use these rules as an operational security verdict or modify a real host as part of this exercise.

## Primary references

The following documentation supports the underlying concepts; the tiny schema and explicit teaching rules above are specific to this lab. Links were checked during authoring on 23 October 2026. Running the lab needs no internet connection.

- [OpenSSH sshd_config manual](https://man.openbsd.org/sshd_config)
