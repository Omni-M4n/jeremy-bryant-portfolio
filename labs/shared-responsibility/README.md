# Cloud shared responsibility: assign a task, then ask for evidence

Who should install a security fix, choose who can use an app, or check files
brought back from a backup? A **backup** is a spare copy used to recover lost or
damaged files. The **customer** is the team using a service. The **provider** is
the company running that service for them.

Follow a made-up team as it changes services. Make a table showing who must do
each job and which records support your answer. Being responsible for a job does
not prove that the job was done.

All cases and records are made up. Work happens on your computer. You will not
open an account or change an online service. First complete the cloud storage
review and backup verification labs. You also need Python 3.10+ and its built-in
tools, called its standard library. Allow 25-35 minutes for the guided case.
Allow 20 minutes each for the later cases. A person still needs to review your
own work and how you explain it.

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

Open a terminal in this lab folder. `python` means your Python 3.10+ program.
Use `py -3` on Windows if that is the installed command.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read `service-description.txt` and `checks.txt` in the new attempt folder. In
`notes.txt`, write a prediction before opening the worked example. Fill
`answers.json`. Each decision uses the three-part form below. Add your reason
and a list of exact evidence references. Save the first attempt before checking.
Then run:

```text
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py analyse --case run/attempt-01/case.json
```

The first command checks labels and requires written fields. A reviewer still
needs to assess your reasons. `analyse`, `reference/` and
`WORKED-EXAMPLE.md` reveal answers. Keep them closed while working alone.
Make a new attempt folder for each case. The helper refuses to overwrite one.

## Exact model

Each JSON case has `services` and `controls`. Services give a model, a specific
backup-copy agreement and an evidence reference. Controls give a task and say
which team owns it. They also give `pass`, `fail` or `missing` evidence. Text
files show these records in a readable form. If you edit a copy, update both
forms. The helper reads the JSON. It cannot check whether a note is a true
account of a real check.

| Narrow task | IaaS | PaaS | SaaS |
| --- | --- | --- | --- |
| `physical-host-patching` | provider | provider | provider |
| `workload-os-patching` | customer | provider | provider |
| `application-code-patching` | customer | customer | provider |
| `tenant-access` | customer | customer | customer |
| `data-sharing` | customer | customer | customer |
| `backup-copy-creation` | explicit agreement | explicit agreement | explicit agreement |
| `restore-acceptance` | customer | customer | customer |

Application code means the customer's code in IaaS/PaaS. In SaaS it means the
ready-to-run app supplied by the provider. It leaves out platform runtime
patching, tenant settings and customer extensions. Running a restore job differs
from checking that the restored files meet the customer's needs. The made-up
agreement sets the task split here. This table does not cover every real
provider or product.

A decision is `owner:assignment:evidence-state`:

* `owner`: `customer`, `provider` or `unspecified`.
* `assignment`: use `clarify-agreement` when the backup agreement names no owner.
  Otherwise, use `assign-owner` when the team names no owner. Use `owner-matches`
  when its claim matches, or `correct-owner` for any other claim. This includes
  a vague `shared` claim.
* `evidence-state`: `evidence-pass`, `evidence-fail` or `evidence-missing`.
  Copy this from the given check for that task. Missing is not proof of failure.

Who owns a task and whether it passed are separate questions. A passing check
does not fix a wrong owner claim. An unclear agreement stays unclear even if
someone made a copy. Each service/task pair may appear once. The helper rejects
unknown models, tasks and fields. It also rejects repeated IDs, states it does
not support and links to missing services.

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

For cleanup, first save the evidence you want. Remove only your own new
`run/attempt-*` folders. No account or security setting changes. Nothing is
installed, so no rollback is needed. Keep the fixtures and first attempts intact
while practising.

## Limits and sources

Real contracts, regions, linked tools, extensions and service options can change
the task split. The helper does not judge legal duties or live controls. A backup
job record alone leaves open several questions. Does it cover all needed files?
What history is kept? What is the recovery goal? Are the restored files useful?

Primary sources opened 25 October 2026:

* [Microsoft: Shared responsibility in the cloud](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility)
  explains how service models differ. Customers keep duties for data, identity
  and settings. Its broad shared app category needs named actions. This lab's
  table splits those actions using a made-up agreement.
* [AWS: Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/)
  separates provider equipment from EC2 guest and app duties. The split also
  depends on the service. It treats provider and customer patching as distinct
  tasks, each needing evidence for its scope.
