# Prove an SSH key login in a lab

A login works, but did it use the key or fall back to a password? A second login
fails, but was the key rejected or could it not reach the server? Save evidence
to answer each question. Keep a working console so you can still get in.

This extends [ssh-config-review](../ssh-config-review/README.md). It adds live
login tests. You check who can use key files, which server you reach and how to recover.
Start with that lab, [linux-permissions](../linux-permissions/README.md), and
[isolated-lab-workbench](../isolated-lab-workbench/README.md).

> **Words:** SSH is a tool for remote login. It encrypts data sent over the link.
> A private key stays with its owner. Its public key can go on a server.
> Authentication checks who is trying to log in. A host fingerprint is a short
> way to check the server key. A console gives direct VM access without SSH.
> Transport here means reaching the server.

## Run the evidence cases

Use Python 3.10+ and a text editor. Allow 25-40 minutes. Start in this folder.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Save your first decisions in `answers.json`. Add reasons and record IDs under
`explanation` and `evidence`. Keep first attempts and list help in `notes.txt`.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

The helper reads made-up JSON cases only. It makes no keys or network links.
Unknown fields, repeated IDs and facts that conflict are errors. A person must
review your reasons. Matching labels do not prove skill.

## Exact offline rules

`expected_user` and `expected_key` name the intended login pair. Key names such as
`k1` are labels, not real keys. `host_fingerprint_match` and
`recovery_console_tested` sum up evidence as true or false. Decision `r1` is
`recovery-tested` or `recovery-not-tested`. It is reserved for recovery.

Each trial has an ID, user, offered key, result and method used. Results are
`accepted`, `auth-rejected`, `transport-error` or `not-run`. Accepted logins must
name `publickey` or `password`; all others must use `none`.

- If the host was not verified, every trial is `host-unverified-stop`.
- A trial not run is `not-tested`; a transport error is `transport-inconclusive`.
- An authentication rejection is `intended-key-rejected` for the intended pair,
  or `alternate-key-rejected` for another pair.
- A password success is `other-method-accepted`; it proves no key login.
- A public-key success is `intended-key-accepted` for the intended pair, or
  `unexpected-key-access` for another pair.

These records do not model a full server. Test that the intended key works and
that the server rejects the other key. These tests are useful only if you have
checked the host and tested recovery.

## Two-VM practice (not run for this package)

Use **two new disposable Debian VMs** with OpenSSH client/server already installed.
Use no existing account, key, host or original VM. Take clean snapshots of both.
Keep the server's admin console open. Prove you can sign in there before you do
anything with SSH. Allow two 30-45 minute sessions after setup.

Use an isolated **internal VM network**, with no NAT, bridge, router or external
route. Assign only these two guests addresses `192.0.2.10/24` (client) and
`192.0.2.20/24` (server) in their network settings, with no gateway or DNS.
These addresses are set aside for examples. Use them only in this disconnected lab.
Confirm `ip -br address` and `ip route` on both. Stop if there is an external
route. Also stop if either address belongs to anything outside these new guests.

On the client, make two new keys in a new temporary folder. Use a fresh passphrase
made only for this lab when prompted. Do not add the keys to an agent or reuse them.

```sh
keydir=$(mktemp -d)
chmod 700 "$keydir"
ssh-keygen -t ed25519 -f "$keydir/key-one" -C lesson-one
ssh-keygen -t ed25519 -f "$keydir/key-two" -C lesson-two
ssh-keygen -lf "$keydir/key-one.pub"
ssh-keygen -lf "$keydir/key-two.pub"
cat "$keydir/key-one.pub"
```

Copy **only** the one-line public key shown by the last command to the server
console. Never copy the private key or put it in notes. Do not copy
`key-two.pub`; it is the alternate key for the rejection test.

On the server console, stop if account `labuser` or `/var/tmp/key-lesson` exists.
Create a fresh dummy account and exercise folder:

```sh
getent passwd labuser
test -e /var/tmp/key-lesson
sudo adduser labuser
sudo install -d -m 700 -o labuser -g labuser /home/labuser/.ssh
sudo install -d -m 755 /var/tmp/key-lesson
sudo -u labuser sh -c 'umask 077; cat > /home/labuser/.ssh/authorized_keys'
```

Paste the **public** key line and press Ctrl+D. Then check the file permissions.
Make a separate server host key. This key marks the temporary server you will run.

```sh
sudo stat -c '%U %a %n' /home/labuser /home/labuser/.ssh /home/labuser/.ssh/authorized_keys
sudo ssh-keygen -t ed25519 -N '' -f /var/tmp/key-lesson/host-key
sudo ssh-keygen -lf /var/tmp/key-lesson/host-key.pub
sudo sh -c 'cat > /var/tmp/key-lesson/sshd.conf'
```

The home folder must belong to labuser. The group and other users must not be
able to write to it. `.ssh` should be 700 and `authorized_keys` 600. If these facts
differ, stop. Correct only these fresh dummy paths. Paste this separate config,
then press Ctrl+D:

```text
Port 2222
ListenAddress 192.0.2.20
HostKey /var/tmp/key-lesson/host-key
PidFile /var/tmp/key-lesson/sshd.pid
AuthorizedKeysFile /home/labuser/.ssh/authorized_keys
AllowUsers labuser
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
UsePAM yes
StrictModes yes
LogLevel VERBOSE
AllowAgentForwarding no
AllowTcpForwarding no
X11Forwarding no
```

Do not edit `/etc/ssh/sshd_config` or the normal SSH service. This separate server
process is called a daemon. It uses its own config, host key, port and PID file.
The PID file holds the process ID. Check the config first. Then run it in the
foreground in a second admin console, where you can see its logs:

```sh
sudo /usr/sbin/sshd -t -f /var/tmp/key-lesson/sshd.conf
sudo /usr/sbin/sshd -T -f /var/tmp/key-lesson/sshd.conf
sudo /usr/sbin/sshd -D -e -f /var/tmp/key-lesson/sshd.conf
```

`LogLevel VERBOSE` adds the detail needed for a rejected key from a valid user.
Keep it only in this exercise config. The `-e` option sends these logs to the
foreground console. No log file or logging change is made to the normal service.

Stop on syntax or startup errors. Do not change the regular service to get past
them. Leave the original recovery console open. On the client, run this one
command. The backslashes continue it across lines:

```sh
ssh -v -F /dev/null -p 2222 -i "$keydir/key-one" \
  -o IdentitiesOnly=yes -o IdentityAgent=none \
  -o PreferredAuthentications=publickey -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no \
  -o UserKnownHostsFile="$keydir/known_hosts" -o GlobalKnownHostsFile=/dev/null \
  labuser@192.0.2.20 id -un
echo $?
```

At the host prompt, compare the fingerprint with the host-key fingerprint on the
server console. Accept only an exact match. Enter the lab key's passphrase if
prompted. It unlocks the local key. It is not the server account password. Save
the public-key authentication line, `labuser` output and exit 0.

Repeat the exact command with `key-two` in place of `key-one`. The server should
reject the login. A timeout does not show a key rejection. Save the exit status
and server log line for that test. On the client, look for the offered `key-two` fingerprint
and `Permission denied (publickey)`. On the server, look for `Failed publickey`
with user `labuser`, client address `192.0.2.10` and the same key fingerprint.
Match the test and time on both sides. A line that only says the link closed
does not prove a rejected key. Neither does the exit status alone. If the lines
above are missing, mark the result as inconclusive: you do not yet know. This
live logging test has not been run here.

## Recovery, cleanup and handover

Test the direct server console again. Stop the exercise daemon with Ctrl+C.
A repeat test from the client should now fail to connect. This is a transport
failure. It does not mean the server rejected a key. Record the difference.
Remove private details from the config, useful log lines and recovery notes.
Export only those records and public fingerprints. Never export passwords or
private keys. Revert **both** VM snapshots. This removes the dummy account, key
files and temporary server together. Do not remove or replace keys in any normal account.

Stopping that daemon ends its detailed console logs. Save the few lines you need
with private details removed, then close its console. Revert the server snapshot
to remove the separate config and any guest log traces. Keep only those redacted
notes. Leave the normal SSH service and its log settings untouched.

Hand over proof that the intended key worked and the other key was rejected.
Include the method used, fingerprint check and console recovery test. Mark every
step you did not run. No Python test here proves a live SSH login or that the
whole server is secure.

## Primary sources opened for this lesson

- [OpenSSH: ssh](https://man.openbsd.org/ssh) — client identity files and diagnostic output.
- [OpenSSH: ssh-keygen](https://man.openbsd.org/ssh-keygen) — separate keys and fingerprints.
- [OpenSSH: sshd](https://man.openbsd.org/sshd) — separate config, syntax tests and foreground mode.
- [Debian: sshd_config](https://manpages.debian.org/bookworm/openssh-server/sshd_config.5.en.html) — authentication settings and the VERBOSE log level.
