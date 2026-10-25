# Apply a small update and prove rollback

A program reports "update complete", but the old version still runs. Another
update shows the new version but breaks the one job you need. Measure both the
version and the job, then prove that you can restore the earlier state.

This extends [dependency-review](../dependency-review/README.md) and
[vulnerability-retest](../vulnerability-retest/README.md). It adds an actual
file update and a test of a useful job. You then restore the exact saved bytes.
There are also steps for an official package update in a disposable VM. Start
with those two labs and
[isolated-lab-workbench](../isolated-lab-workbench/README.md).

> **Words:** A patch is an update. A baseline is the saved starting state.
> A smoke check tests a small useful job. A regression is a new failure after a
> change. Rollback returns to the old state. A hash is a fingerprint of bytes.

## Run the evidence cases

Use Python 3.10+ and a text editor. Allow 25-40 minutes. No extra Python packages
are needed. Start in this lab folder.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Save first predictions in `answers.json`, using the exact labels below. Add
reasons and record IDs in `explanation` and `evidence`. Use `notes.txt` to list
help used and things you are unsure of. Keep first attempts before checking.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

The helper reads made-up JSON cases only. Unknown fields, repeated IDs and values
outside the rules are errors. A person must assess your reasons. A label match
does not prove skill. The local practice helper below is a separate tool.

## Exact evidence rules

Each `changes` record names the starting version, target and installed version.
It also has a source status, install exit code, smoke-test result and rollback
evidence. Version strings must start with a digit. The helper checks for an exact
match. It does not decide which version is newer. `official` means the case gives
a checked official source. Do not use that label for a download you have not checked.

Apply this order:

1. Unverified source: `source-unverified`.
2. Nonzero install exit: `install-error-investigate`.
3. Installed version differs from target: `version-not-confirmed`.
4. Smoke check not run: `need-smoke-test`.
5. If the smoke check fails, use `regression-rollback-verified` only if both
   rollback checks pass. The restored version must match baseline. Its smoke
   check must pass too. If either check fails or is missing, use
   `regression-recovery-needed`.
6. If the smoke check passes, use `update-and-rollback-verified` when both rollback
   checks pass. With a rollback version but no proof that both checks passed,
   use `update-verified-rollback-incomplete`. With no rollback version, use
   `update-verified-rollback-untested`.

An empty rollback version requires `rollback_smoke: "not-run"`. Update evidence
shows what you saw **before** rollback. It does not show the version left after
rollback. Keep both times in real notes.

## Safe local file practice

This helper changes only toy JSON package files in a new temporary folder below
this lab's ignored `run/` folder. It does not install software or change settings.
The toy job is to print `Hello Sam`. Read `practice.py` first. Predict the greeting
and smoke result for each run. Then run:

```text
python practice.py --receipt run/file-check-01.json
python practice.py --regression --receipt run/file-check-02.json
```

Both candidate files change version 1.0 to 1.1. Each run applies one candidate
and checks the greeting. It then restores the backup and checks its hash and
greeting. Last, it removes its temporary files and saves a receipt. It refuses
to replace an existing receipt. Compare the results with your predictions. Keep
both receipts. Explain why matching bytes alone do not prove a useful update.
This is real file practice. It does not patch an operating-system package.

Receipt paths must start with `run/` and end in `.json`. Nested folders are fine.
Use letters A-Z, digits, dots, underscores and hyphens in each name. Each name
must start with a letter or digit and must not end with a dot. Spaces, colons,
Windows device names such as `NUL`, and dot-only path parts are refused before
any files are made. Use at most 80 characters per name and 240 for the whole
path. The same rules apply to folder names.

## Separate VM package practice (not run for this package)

Use a **new disposable Debian VM** and an admin console. Use an approved official
Debian repository, with `hello` already installed at an older version. A repository
is a package source. Keep the original VM untouched. Take a clean snapshot and
record its name. If no newer `hello` version is offered, stop. Do not invent an
update or switch sources. Allow 30-45 minutes plus download time. Network access
here is only to the VM's approved official package repository. Never use an
unknown mirror or script.

In the new VM, record its repository files and baseline:

```sh
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d
cat /etc/apt/sources.list.d/*.sources
cat /etc/apt/sources.list.d/*.list
dpkg-query -W -f='${Package} ${Version} ${Status}\n' hello
hello
sudo apt-get update
apt-cache policy hello
```

Some source files may not exist. Record that fact. Inspect each source file that
does exist. Check that its URI (address) is an approved official Debian source.
Signature checking must be turned on. Stop on update or signature errors. Record
the installed and candidate versions from `apt-cache policy`. Put the exact
candidate version in place of `VERSION` below. Never type `VERSION` literally.

```sh
sudo apt-get -s install --only-upgrade hello=VERSION
```

Read the simulation, which lists the planned changes. Continue only if it upgrades
hello alone. It must not remove or add other packages. If it asks for more changes,
stop and choose another clean lab snapshot. Then run the same command without
`-s`. Keep the exact version:

```sh
sudo apt-get install --only-upgrade hello=VERSION
echo $?
dpkg-query -W -f='${Package} ${Version} ${Status}\n' hello
hello
```

Save the install output and the exit status shown just after it. Then save the
version query and `hello` output as separate records. This package has no service.
Record service health as **not applicable**. Do not mark it "passed". Compare the
greeting with baseline. Export notes, revert the VM snapshot, and rerun the version
query and `hello`. Check that both the old version and its useful job returned.
Reverting the snapshot is the rollback route here. Do not assume a package
downgrade from a repository is safe.

## Hand over and limits

Hand over evidence from before the update, after it, and after rollback. Include
the official source check, smoke result and one dependency you did not test.
A dependency is something the program needs. Python tests cover the toy files
and made-up cases. They do not prove that an OS update was applied or a security
flaw was fixed. They also do not show that every part of the program still works.

## Primary sources opened for this lesson

- [Debian: apt-get](https://manpages.debian.org/bookworm/apt/apt-get.8.en.html) — version selection, simulation and one-package updates.
- [Debian: dpkg-query](https://manpages.debian.org/bookworm/dpkg/dpkg-query.1.en.html) — querying package state and version.
- [Microsoft: file names](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file) — reserved device names and filename limits.
