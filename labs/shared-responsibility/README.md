# Cloud shared responsibility: assign a task, then ask for evidence

Who should install a security fix, choose who can use an app, or check files
brought back from a backup? A **backup** is a spare copy used to recover lost or
damaged files. The **customer** is the team using a service. The **provider** is
the company running that service for them.

Follow a made-up team as it changes services. Make a table showing who must do
each job and which records support your answer. Being responsible for a job does
not prove that the job was done.

All cases and records are made up. Work happens on your computer; you will not
open an account or change an online service. First complete the cloud storage
review and backup verification labs. You also need Python 3.10+ and the tools
that come with it, called its standard library. Allow 25-35 minutes for the
guided case and 20 minutes each for the later cases. Your own work and ability
to explain it still need a person's review.

## Vocabulary

| Term | Meaning here |
| --- | --- |
| Physical computer | A real machine with parts such as memory and a disk. A cloud provider runs these machines in its buildings. |
| Virtual machine (VM) | A computer made by software inside a physical computer. For example, one physical computer can run several separate VMs. |
| Operating system (OS) | Software that manages a computer's files and programs, such as Linux. A VM's OS is also called its guest OS. |
| App code and app binary | App code gives a program its instructions. An app binary is a ready-to-run program file. A report app is one example. |
| Platform and runtime | A platform supplies tools for running apps. A runtime is software an app needs to run; Python is one example. |
| Infrastructure | The basic equipment a service needs, such as physical computers and network cables. |
| Tenant | One customer's part of a shared service, including its users and settings. For example, a team can choose who may read its reports. |
| IaaS: Infrastructure as a Service | Here, the team rents a VM. The provider looks after the physical computer; the team looks after the VM's OS and apps. |
| PaaS: Platform as a Service | Here, the team supplies its app code. The provider looks after the OS and runtime used to run it. |
| SaaS: Software as a Service | Here, the team uses a ready-made app. The provider runs the app; the team still chooses its users and settings. |
| Security control | A step or setting meant to protect something. For example, a setting can limit who may read a report. |
| Atomic task | One small, named job, such as installing an OS security fix. It does not mean every job needed to protect a service. |
| Assurance evidence | A record of what was checked and what happened. For example, a dated update report can show which security fixes were installed. |
| Restore acceptance | Checking that files brought back from a backup are useful. For example, the customer checks that a recovered report has the expected rows. |

## Start and preserve a first attempt

Open a terminal in this lab directory. `python` means your Python 3.10+ executable;
use `py -3` on Windows if that is the installed command.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `service-description.txt` and `checks.txt` in that new attempt folder. In
`notes.txt`, record a prediction before opening the worked example. Fill
`answers.json`: each decision uses the three-part form below; add your explanation
and a list of precise evidence references. Save the original attempt before
checking it. Then run:

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
```

The first command checks decision strings and whether written fields are present.
A reviewer still needs to assess the explanation. `analyse`, `reference/` and
`WORKED-EXAMPLE.md` reveal answers; keep them closed during independent work.
Make a new attempt folder for each case. The helper refuses to overwrite one.

## Exact model

Each JSON case has `services` and `controls`. Services supply a model, a specific
backup-copy agreement and an evidence reference. Controls supply a task, a team
owner claim and `pass`, `fail` or `missing` evidence. Text files are readable
companions to those records. For edited experiments update both; the helper reads
the JSON and cannot establish whether a note truthfully describes a real check.

| Narrow task | IaaS | PaaS | SaaS |
| --- | --- | --- | --- |
| `physical-host-patching` | provider | provider | provider |
| `workload-os-patching` | customer | provider | provider |
| `application-code-patching` | customer | customer | provider |
| `tenant-access` | customer | customer | customer |
| `data-sharing` | customer | customer | customer |
| `backup-copy-creation` | explicit agreement | explicit agreement | explicit agreement |
| `restore-acceptance` | customer | customer | customer |

Application code means the customer's deployed code in IaaS/PaaS and the
provider-delivered binary in SaaS. It excludes platform runtime patching, tenant
settings and customer extensions. Restore acceptance is distinct from the act of
operating a restore job. The fictional agreement is the authority for these
narrow assignments; the table is not a complete provider product matrix.

A decision is `owner:assignment:evidence-state`:

* `owner`: `customer`, `provider` or `unspecified`.
* `assignment`: `clarify-agreement` when the backup agreement is unspecified;
  otherwise `assign-owner` for an unspecified team claim, `owner-matches` when it
  matches, or `correct-owner` for any other claim, including a vague `shared`.
* `evidence-state`: `evidence-pass`, `evidence-fail` or `evidence-missing`, copied
  from the supplied scoped check. Missing is not proof of failure.

Responsibility and evidence are independent. Passing evidence does not correct a
wrong assignment. An unclear agreement remains unclear even if a copy was made.
Every service/task pair may occur once. Unknown models/tasks/fields, duplicate
IDs, unsupported states and broken service references are rejected.

## Evidence to save and hand over

Keep the case, first answers, notes, check output and corrections in `run/`.
For each task, answer these short questions in a table:

* Who must do this job?
* Which part of the service agreement says so?
* What record shows whether the job was done?
* What is still missing, and who should check it next?

Add one question the service description leaves unanswered. For example, which
files are included in each backup, or how long would recovery take? When you hand
over your work, say: "This job needs attention. Here is the record I used. Here is
what I still need to find out." Matching the worksheet answers shows a practice
step is complete; it does not prove you can do the work on your own.

To validate the supplied materials:

```text
python test_lab.py
python lab.py verify
```

Cleanup is limited to your own new `run/attempt-*` folders after preserving the
evidence you want. No account, installation, security setting or rollback is
involved. Keep the fixtures and first attempts intact while practising.

## Limits and sources

Real contracts, regions, integrations, extensions and individual service options
can change the split. The helper evaluates neither legal liability nor live
controls. A backup job record cannot establish complete coverage, retained
history, a recovery objective or usable restored data.

Primary sources opened 25 October 2026:

* [Microsoft: Shared responsibility in the cloud](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility)
  explains service-model differences and retained customer data, identity and
  configuration duties. Its broad shared application category must be split into
  concrete actions; this lab's atomic table is an authored fictional agreement.
* [AWS: Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/)
  distinguishes provider infrastructure, EC2 guest/application duties and
  service-dependent responsibilities. Its control discussion separates patching
  at infrastructure and customer layers and calls for scoped evidence.
