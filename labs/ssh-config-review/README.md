# Review a small SSH server file

A server file can list the same setting twice. Which value takes effect?
Is a way to sign in still enabled? Use six settings to answer those questions.

This is an offline exercise with made-up data. It is separate from coursework.
It does not claim that you have used a real server or passed a skills test.

## Start here

Allow 30–45 minutes. Read for 5 minutes, inspect for 10, then check and explain.
Use the time left for another case. You need Python 3.10 or newer, a terminal
and a text editor. You do not need to write code or have a Linux machine.
No admin rights or cloud account are needed.

| Word | Meaning here |
| --- | --- |
| SSH | A tool used to sign in to a remote machine |
| sshd | The SSH server |
| Directive | One setting name and its value |
| Public-key sign-in | Prove you hold the private key; the server must also allow that key |
| Keyboard-interactive | A sign-in method separate from the password setting |
| Precedence | Which value takes effect when a setting appears twice |
| Baseline | The stated rules used for this lab's check |

## Read the evidence

Use the case file as the source. It holds the server text in `data.config`.
There are three cases: guided, changed and challenge. All are made up.
There are no separate data copies in `artifacts`. Edit only a prepared run copy.
The script reads the text as data. It never runs that text as a command.

The parser reads only the six settings below. A parser is code that reads a
file's structure. Each line must have one plain name and one value.
Blank lines and whole lines starting with `#` are allowed.
Setting names ignore letter case. Values are case-sensitive.

| Setting | Lab baseline | Allowed input |
| --- | --- | --- |
| PermitRootLogin | no | yes, no, prohibit-password or forced-commands-only |
| PasswordAuthentication | no | yes or no |
| KbdInteractiveAuthentication | no | yes or no |
| PubkeyAuthentication | yes | yes or no |
| PermitEmptyPasswords | no | yes or no |
| MaxAuthTries | 1–4 | Whole number from 1 to 100 |

This small reader rejects quotes, comments after a value, and unknown settings.
It also rejects `Match` and `Include`. It cannot read every real server file.
The first value wins. A later value for that setting is shown as ignored.
A missing setting stays unknown. The script does not guess the server's default.

## Choose a result

Use one of these exact labels for each setting:

| Label | Meaning |
| --- | --- |
| matches-lab-baseline | The first value fits the baseline column |
| differs-from-lab-baseline | The first value does not fit the baseline column |
| missing-explicit-setting | The setting is absent |

The `access-route` result uses the three sign-in method settings. Read these
rules in order. Stop at the first row that fits.

| Condition | Exact label |
| --- | --- |
| Any method setting is missing | insufficient-explicit-method-settings |
| Public-key method is enabled | public-key-method-enabled |
| Another supported method is enabled | alternative-method-enabled |
| All three methods are off | no-supported-method-enabled |

An enabled method does not prove that a key works. The account, key and network
still need their own checks. Do not use this result to change a real server.

## Run the exercise

Open a terminal in this lab folder. The commands use `python`.
Use `py -3` instead if that is your installed Python command.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the case. Open `run/attempt-01/answers.json` and fill each blank decision.
Use an exact label from the tables. Add your reason and the lines that support
it. In `notes.txt`, keep facts, meaning, unknowns, next checks and help used apart.
Save your first prediction before opening the answer.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

Use the matching attempt path for each later case. Prepare needs a new folder
below `run/`. It will not replace an old attempt. Its output path is relative
to this lab. Other paths are relative to your terminal's current folder.
Show and analyse use the guided case if you leave out `--case`.

| Exit code | Meaning |
| --- | --- |
| 0 | Command ran, or decision fields match |
| 1 | Decisions differ, or written fields are incomplete |
| 2 | Invalid input or a file error |

The checker checks labels and whether writing is present. It cannot judge the
quality of your reasons. Verify checks the supplied cases, not your skill.

## Save and explain

Keep the case, answers and notes together in your run folder. Write a short
handover: the question, your result, two exact evidence references, one limit,
and the next check. State which help you used. State whether the case was fresh
and you attempted it without help.

Open WORKED-EXAMPLE.md after your first prediction. Use DRILLS.md to practise
with less help. A script match is not a skills assessment or work experience.

## Limits and source

Only six explicit settings are checked. The script reads and writes local
practice files. It does not inspect or change your SSH settings.
It cannot prove that real sshd accepts the file. It does not test
keys, PAM sign-in rules, network access or a recovery login.

The baseline is a teaching choice. It is not a rule for every real server.
The manual supports the real setting names and their meaning. The link was
checked on 23 October 2026. No internet is needed to run this lab.

- [OpenSSH sshd_config manual](https://man.openbsd.org/sshd_config)
