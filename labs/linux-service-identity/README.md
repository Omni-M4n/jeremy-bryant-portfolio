# Trace a Linux service account

A small background job needs to read its own files. It does not need to control
the whole computer. Check which account actually runs it, then test exactly what
one helper account may do with sudo.

This extends [linux-permissions](../linux-permissions/README.md). It adds a live
service process identity and a permitted-versus-denied sudo command test.
Start with that lab and [isolated-lab-workbench](../isolated-lab-workbench/README.md).

> **Words:** A service is a background job. A process is a running program.
> Root is the Linux administrator. Sudo runs a command as another account when
> policy permits it. Arguments are the words after a command. Scope is the
> exact set of actions a rule covers.

## Try the evidence cases

In this folder, use Python 3.10+ and a text editor. No extra Python packages are needed.
Allow 25-40 minutes for the offline cases. Allow another 30-45 minutes for the VM
practice, after the VM is ready. A VM is a separate guest computer run by software.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the prepared `case.json`. Save predictions in `answers.json` before opening
an answer. Use the exact decision words below. Add your reasons and record IDs in
`explanation` and `evidence`. Keep your first attempt. Record help in `notes.txt`.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

A matching answer is a useful check, not proof of skill. A person must read your
reasons. JSON is the sole input; there are no second copies of the evidence.
Unknown fields, repeated IDs and unsupported values are errors. The helper only
reads fictional data. It does not run the commands in the VM instructions.

## Exact offline rules

`service` has an ID, configured and observed user names, and `active` or `inactive`.
For this **system** service, an empty configured user means root. An active
service needs an observed user. An inactive service must have an empty observed
user and gets `not-running`. Otherwise the result is `identity-matches` or
`identity-mismatch`. Matching root with root is a match, not a safety verdict.

`rules` lists exact `(run_as, executable, arguments)` tuples. Each request gets
`allowed-by-listed-rule` only if all three match; otherwise `not-listed`.
This is a small supplied rule list, not a full sudoers parser. No glob, alias,
shell, PATH search or unseen group policy is assumed. `not-listed` alone does
not prove a live command will be denied under a machine's complete policy.

## VM practice: a sleeping service and a narrow rule

Use a **new disposable Debian VM with systemd and sudo already installed**.
Use a fresh administrator login. Take a clean snapshot and keep its console
open. Disconnect networking. Do not change your host or an existing VM. Stop if
any named account, unit, file or `/etc/sudoers.d/lesson-scope` already exists.
These VM steps have not been run as part of this package.

In the VM administrator terminal, confirm paths and names first:

```sh
command -v sudo systemd-run systemctl visudo
ls -l /usr/bin/id /usr/bin/sleep
getent passwd labsvc
getent passwd labops
systemctl status lesson-identity.service --no-pager
sudo test -e /etc/sudoers.d/lesson-scope
```

The last four checks should find no existing exercise objects. Create two dummy
accounts. `labops` must not join an administrator group.

```sh
sudo useradd --system --no-create-home --shell /usr/sbin/nologin labsvc
sudo useradd --create-home --shell /bin/bash labops
sudo systemd-run --unit=lesson-identity --uid=labsvc /usr/bin/sleep 600
systemctl show lesson-identity.service -p User -p MainPID -p ActiveState
pid=$(systemctl show lesson-identity.service -p MainPID --value)
ps -o pid,user,group,args -p "$pid"
```

Save the configured user and the observed process user. If the ten-minute sleep
has ended, record that state and start a new named run after stopping the old one.
Do not report an inactive process as an identity mismatch.

Make a rule in a temporary file, check its syntax, then install only that file:

```sh
rulefile=$(mktemp)
printf '%s\n' 'labops ALL=(labsvc) NOPASSWD: /usr/bin/id -u' > "$rulefile"
sudo visudo -cf "$rulefile"
```

Continue only if the syntax check succeeds:

```sh
sudo install -o root -g root -m 0440 "$rulefile" /etc/sudoers.d/lesson-scope
sudo visudo -c
sudo -u labops sudo -n -l
sudo -u labops sudo -n -u labsvc /usr/bin/id -u
sudo -u labops sudo -n -u labsvc /usr/bin/id -un
```

The numeric ID command should succeed as labsvc. The name command should be
denied: `-un` is not `-u`. Retain output and exit status (`echo $?` immediately
after each test). If both work, inspect all policy with `sudo -l -U labops`;
do not treat that result as a successful boundary. These two commands only read
identity information. Never broaden the exercise rule to a shell or `ALL`.

Save the unit details, `ps` output, rule text, syntax check, command results and
the next check for any mismatch. Remove the temporary file with `rm -- "$rulefile"`
only while that variable still names the file created here. Stop the unit with
`sudo systemctl stop lesson-identity.service`. Export redacted notes, then revert
the VM snapshot. Reversion removes the accounts and sudo rule together.

## Hand over and limits

Explain why an account match is different from least privilege (only the access
needed for a job). Include the permitted and denied command evidence. Files,
capabilities, service code and other sudo rules may still add privilege. A person
must review those limits and your reasons. Offline tests do not prove VM results.

## Primary sources opened for this lesson

- [systemd: execution identity](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html) — system service User setting.
- [systemd: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) — show and service state.
- [systemd: transient services](https://www.freedesktop.org/software/systemd/man/latest/systemd-run.html) — creating the bounded sleeping service.
- [Debian's sudo manual](https://manpages.debian.org/bookworm/sudo/sudoers.5.en.html) — run-as scope and command arguments.
