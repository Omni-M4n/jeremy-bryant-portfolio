# Measure Windows file permissions

A class has a shared note. One person should read it but should not change it.
Can that person also delete it? Test each action, because a list of permissions
alone can hide the route that Windows uses.

This extends [access-review](../access-review/README.md) and
[linux-permissions](../linux-permissions/README.md). It adds Windows rule order,
inherited rules, and actual read/write/delete tests with a dummy account.
Start with access-review and [isolated-lab-workbench](../isolated-lab-workbench/README.md).

> **Words:** An account is a login identity. A group is a set of accounts. An ACL
> is a list of access rules. One rule is an ACE. Inheritance copies rules from a
> parent folder. A token lists the identities used for an access check.

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

`token` lists enabled identities. `file_aces` and `parent_aces` are the effective
rules already inherited onto those objects. Do not copy rules again. Each ACE
has `trustee`, `kind` (`allow` or `deny`), `inherited` (true/false), and `rights`.
Rules must be in this order: explicit deny, explicit allow, inherited deny,
inherited allow. This lesson has only one inheritance level.

For one requested data right (`read`, `write`, or `delete`), the first matching
file ACE settles the check. No matching rule means `deny`. A delete is `allow`
if either the file grants `delete` or the parent grants `delete-child`, even when
the file route is denied. Empty lists mean an empty ACL, never a missing ACL.
No share rules, privileges, disabled groups, owner rights or locks are modelled.
A real editor may request several rights; the helper checks one at a time.

## VM practice: read, change and delete three dummy files

Use a **new disposable Windows 11 VM**, a fresh local administrator account and
64-bit Windows PowerShell. Take a clean snapshot. Keep the administrator console
open for recovery. Disconnect the VM from networks. Do not run this on your host
or an existing VM. If `AclReader`, `AclClass`, or `C:\AclLesson` already exists,
stop and use a clean VM. These steps have not been run as part of this package.

In the VM administrator PowerShell, run:

```powershell
Get-LocalUser -Name AclReader -ErrorAction SilentlyContinue
Get-LocalGroup -Name AclClass -ErrorAction SilentlyContinue
Test-Path -LiteralPath C:\AclLesson
$pass = Read-Host 'Choose a new disposable VM password' -AsSecureString
New-LocalUser -Name AclReader -Password $pass
Add-LocalGroupMember -SID 'S-1-5-32-545' -Member AclReader
New-LocalGroup -Name AclClass
Add-LocalGroupMember -Group AclClass -Member AclReader
New-Item -ItemType Directory -Path C:\AclLesson
icacls C:\AclLesson /inheritancelevel:r
icacls C:\AclLesson /grant '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' 'AclClass:(OI)(CI)RX'
'read note' | Set-Content C:\AclLesson\read.txt
'write note' | Set-Content C:\AclLesson\write.txt
'delete note' | Set-Content C:\AclLesson\delete.txt
icacls C:\AclLesson\*
Get-LocalGroupMember AclClass
runas /user:.\AclReader powershell.exe
```

Enter the disposable password at the prompt. In the new reader window, run each
command separately. Record `whoami /groups`, output and any error. Never use
`runas /savecred`.

```powershell
whoami
whoami /groups
Get-Content C:\AclLesson\read.txt
Add-Content C:\AclLesson\write.txt 'second line' -ErrorAction Stop
Remove-Item -LiteralPath C:\AclLesson\delete.txt -ErrorAction Stop
```

Expect reading to work. Expect the other two actions to be denied. In the admin
window, save the before evidence (`icacls C:\AclLesson\*`) outside that folder.
Give only the write file an explicit modification rule:

```powershell
icacls C:\AclLesson\write.txt /grant 'AclReader:M'
icacls C:\AclLesson\write.txt
```

In the reader window, retry `Add-Content` and read the changed file. Record why
`M` is broader than this lesson's single `write` bit: it also includes deletion.
Do not delete the write file yet. For an inheritance check, in the admin window:

```powershell
icacls C:\AclLesson\read.txt /inheritancelevel:r
icacls C:\AclLesson\read.txt
```

Retry the read as AclReader; it should fail because its inherited grant was
removed. Restore that inheritance with `icacls C:\AclLesson\read.txt
/inheritancelevel:e` on one line, then verify the reader can read again.

Save an account/group map, all before/after ACL text and the three action tests.
Do not include passwords. Compare observed results with your prediction. If a
result differs, keep it and inspect the token and parent ACL. Do not silently
change the evidence. Close the reader window, export only redacted notes, then
revert the VM snapshot. This removes all dummy accounts and files together.

## Hand over

Give a reviewer your first prediction, rule order, actual operation results and
one limit of the model. Ask: which extra right did the real program request?
The Python checks verify the lesson data; they do not establish Windows behavior
on your machine or assess your skill.

## Primary sources opened for this lesson

- [Microsoft: access-check sequence](https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object) — matching identities and ordered rules.
- [Microsoft: icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) — inheritance, rule order and rights.
- [Microsoft: file deletion](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-deletefilew) — file delete and parent delete-child routes.
- [Microsoft: local group membership](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/add-localgroupmember) — adding the dummy account to the standard Users group by SID.
