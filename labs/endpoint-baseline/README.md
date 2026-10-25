# Build a small endpoint baseline

A study computer must do useful work. It must also lock when no one is using it.
Write four rules, test them, and keep dated reasons for any short-term exception.
A stricter setting only helps if you can still do the work you need.

This is a new core lesson. Start with
[shell-troubleshooting](../shell-troubleshooting/README.md),
[patch-rollback](../patch-rollback/README.md) and
[access-review](../access-review/README.md). Use
[isolated-lab-workbench](../isolated-lab-workbench/README.md) before VM practice.

> **Words:** An endpoint is a computer used for work. A baseline is a small set
> of required settings. A control is one rule you can test. An observation is
> what you measured. An exception gives dated approval to differ from a rule.
> Normal use means the everyday jobs the computer must still do.

## Run the evidence cases

Use Python 3.10+ and a text editor. Allow 25-40 minutes. Start in this folder.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Save your first answers in `answers.json`. Use the exact labels below. Add
reasons and record IDs under `explanation` and `evidence`. Keep each first attempt.
List help used in `notes.txt` before you check the answers.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

The helper reads made-up JSON cases only. It changes no settings. Unknown fields,
repeated IDs, future observation dates and wrong value types are errors. A person must read
your reasons. Matching labels do not prove skill.

## Exact offline rules

`as_of` is the review date. Supply exactly one of each control kind:

| Kind | Required and observed values | How they match |
| --- | --- | --- |
| `service-active` | true or false | Equal values |
| `updates-pending` | Whole numbers, 0-10000 | Observed count is no more than required |
| `standard-user` | true or false | Equal values |
| `lock-seconds` | Whole seconds, 0-86400 | Observed is positive and no more than required |

For `lock-seconds`, observed 0 means that the lock is off. It does not mean instant
lock. The required lock time must be greater than zero. Each observed value needs
`observed_on` and an `evidence` reference. A missing value uses JSON `null`.
Its date and evidence fields must be empty. Dates use `YYYY-MM-DD`.

An exception needs a known control ID, reason, `approved_by` and `expires_on`.
The case supplies the approval. Writing your own name does not approve a real
exception. It remains active on its expiry date.

Check each control in this order. A missing value is `not-observed`. One older
than seven days is `recheck-stale`. A fresh value that meets the rule is
`matches-requirement`. A fresh value that differs is `exception-active` if its
approval has not expired. It is `exception-expired` if that approval has expired,
or `change-needed` with no approval. This exercise uses a seven-day evidence
window. Other work may use a different one. An exception cannot fill a gap in
evidence or make old evidence fresh.

`normal_use` is `pass`, `fail` or `not-run`. The reserved result `u1` is
`normal-use-passed`, `normal-use-failed` or `normal-use-not-tested`. Keep this
result apart from the controls. A setting can meet a rule and still break a job.

## VM practice: observe four controls and test one setting

Use a **new disposable Debian GNOME desktop VM**. Make a fresh admin login and a
separate fresh standard desktop account. Take a clean snapshot. Keep the admin
console open. Do not change your host or an existing VM. Use a password made only
for this guest. Test that it unlocks the guest before you change the lock settings.
These desktop steps have not been run for this package. Allow 30-45 minutes after setup.

Choose these study-desk rules before you collect evidence:

| Control | Requirement | Evidence to save |
| --- | --- | --- |
| Logging service | systemd-journald active | Service state and date |
| Update assessment | No pending package updates | Official source check, refresh date and package list |
| Everyday account | Standard user, no general sudo access | Account/group and sudo-policy output |
| Idle lock | Lock within 300 seconds of no input | Settings plus a timed observation |

In the VM, collect service evidence:

```sh
date -I
systemctl is-active systemd-journald.service
systemctl show systemd-journald.service -p ActiveState -p SubState
```

Do not stop or disable the logging service. If it fails the rule, record that
fact and a next check. From the fresh admin console, inspect the package sources,
as in patch-rollback. They must be approved official Debian sources. They must
also have signature checking turned on. Only then use:

```sh
sudo apt-get update
echo $?
apt list --upgradable
```

Stop on refresh errors. Count the package rows, but not the heading. Save the
list and time. A zero count from old indexes is weak evidence. Do not install
updates in this lesson. If packages are pending, record `change-needed`. Use the
patch-rollback lesson for one small update. If this guest is not approved to use
the network, leave this control unobserved.

Sign into the fresh **standard desktop account**. In its terminal:

```sh
id
sudo -l
```

Record the account and full sudo-policy result. A nonzero user ID alone does
not prove the account has limited rights. This fresh account must have no broad
admin rule. If policy grants broad admin rights, record the difference. Do not
remove groups or rewrite policy in this exercise.

Before you change lock settings, record their old values in GNOME Settings. Under
Power, choose a one-minute Screen Blank delay. Under Privacy & Security (or
Privacy on an older GNOME), open Screen Lock, turn Automatic Screen Lock on and
choose the shortest lock delay shown. If these controls are missing or managed,
stop and record that limit. Do not change organisation policy.

Open a text editor in that guest account. Type a harmless two-line note. Save it
as `baseline-note.txt` in the guest Documents folder. Use a new name if that file
exists. Start a timer outside the guest just after your last input. Do not touch
the guest until it locks. Record the time taken. Check that you need the guest
password to return to the desktop. If only the screen goes blank and no password
is needed, record that the lock test failed.

Unlock it. Reopen the note, add a third line, save and reopen it again. This is
the normal-use check. Save the lock time, settings, unlock result and note-edit
result. A picture of a switch alone does not show that the screen locked.
Restore the old lock settings and check them. Remove private details from your
notes, then export them. Revert the VM snapshot to remove the test accounts and note.

## Exceptions and handover

If you cannot meet a rule, name the control and give the exact reason. State the
short-term measure, requested expiry date and reviewer. Keep it a **proposed**
exception until that reviewer approves it. Do not turn a failed check into a
pass. Recheck evidence when it grows old, even if an exception is still active.

Hand over the rule table, before/after evidence, lock time and normal-use result.
Include approved or proposed exceptions and tests you did not run. These four
controls do not cover every setting that could make a computer safer. They do
not give an overall safety score. An update count cannot show that all installed
software still gets support.

## Primary sources opened for this lesson

- [GNOME: automatic screen lock](https://help.gnome.org/gnome-help/privacy-screen-lock.html) — automatic lock and unlock behavior.
- [systemd: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) — service state inspection.
- [Debian: apt](https://manpages.debian.org/bookworm/apt/apt.8.en.html) — package-index refresh and upgradeable package lists.
- [Debian: sudo policy](https://manpages.debian.org/bookworm/sudo/sudoers.5.en.html) — command privilege scope.
