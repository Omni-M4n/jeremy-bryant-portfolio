# Endpoint process context triage

Read a small process tree. Explain which links need a closer look. A link alone does not prove that a program is malware.

This made-up lab was written for beginners and runs offline. It is practice, not copied coursework or proof of work done in a job. No one has yet assessed your work or skill.

## Before you start

Allow **30-45 minutes**. Spend 5 minutes reading, then 10 on the evidence and your first choices. Spend 10 minutes checking and explaining your work. Allow 5-20 minutes for a changed case or one you try alone. You need Python 3.10+ with its built-in library, a terminal and a text editor. You should know how to open files, read a small table and make evidence notes. You do not need to write code, install Linux or have admin rights or cloud accounts. Basic network or Wireshark practice may help, but you can start without it.

A **parent** is the process recorded as starting another process. A **process tree** shows these parent and child links. A **signature** gives evidence about a signed file. It does not promise that the file is harmless. **Triage** means choosing what to inspect next. A **false positive** is a signal with a harmless cause.

## Evidence and exact rules

The case JSON is the source used for all results. The supplied cases are guided.json, changed.json and challenge.json. All data is made up. The artifacts field is empty, so there is no second copy to edit. Edit only a copy made by prepare. The analyser just works out results. It never runs text from the evidence as a command.

Each row in data.processes has a unique ID and parent ID, or null for no parent. It also has an image, role, location, signature evidence, approved_change and a command string. approved_change is true or false. The command is text to read, never to run. Each named parent must be present. Parent links must not form a loop. Roles are desktop, document, shell, service or utility. Locations are system, program or user-temp. Signatures are verified, unsigned or unknown. These labels come with the case. The lab does not find them on your computer.

Use the rules in this order. First look for either of two triggers. One is a shell whose direct parent is a document process. The other is a process run from user-temp. With no documented approval, either trigger gives prioritise-context-review. Any documented change gives documented-change-context. If neither rule applies, an unsigned or unknown signature gives signature-context-incomplete. All remaining rows give no-modelled-triage-trigger. A verified signature never cancels a trigger from the process context. Put these exact labels in answers.json.

## Run the exercise

Open a terminal in this lab folder. Use your usual Python command: `python`, or `py -3` if your setup needs it. The steps below all use `python`.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. Open run/attempt-01/answers.json. Fill each decision with an exact label from the rules. Add your reasons and cite the evidence. You can use record IDs or the line numbers in settings files. In notes.txt, state what you saw and what you think it means. Then state what is unknown, what to check next and what help you used. Keep these parts separate. Save your first choices before you open the answer.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

For changed/challenge, use that attempt folder in show/analyse/check. prepare rejects an output folder that already exists. --out starts from this lab and must be inside run/. Input paths that you supply start from your terminal folder. analyse/show use the guided case if you omit --case.

Exit 0 means the command worked or your decision fields match. Exit 1 means a choice differs or written fields are incomplete. Exit 2 means the input is invalid or there is a file error. The checker checks decision fields and whether you wrote something. It cannot judge your reasons. verify checks the supplied cases. It does not assess your skill.

## Deliverable and limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. Write a short handover. Include the question, your finding and two exact sources from the evidence. Give one other possible cause or limit of the evidence. State what evidence you would ask for next. Say if you used the worked example or tried a fresh case on your own. A match from the checker is not an assessment or proof of job experience.

A suspicious link is a reason to review the process. It does not prove malware. A verified signature does not prove safety. This small tree leaves out memory, file contents and network activity. It also leaves out gaps in collected data. No host was inspected.

Use WORKED-EXAMPLE.md after you save your first choices. Use DRILLS.md to try tasks with less help. Do not use these lesson rules to judge a real host. Do not change a real host as part of this lab.

## Primary references

These sources explain the ideas used here. The small data format and teaching rules belong to this lab. The links were checked when the lab was written on 23 October 2026. You need no internet link to run it.

- [Microsoft Sysmon event documentation](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon)
