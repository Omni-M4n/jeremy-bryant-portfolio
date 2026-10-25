# Scheduled task change review

Compare daily tasks with a small approved baseline. Check which differences have exact approval and which still need an explanation.

This made-up lab was written for beginners and runs offline. It is practice, not copied coursework or proof of work done in a job. No one has yet assessed your work or skill.

## Before you start

Allow **30-45 minutes**. Spend 5 minutes reading, then 10 on the evidence and your first choices. Spend 10 minutes checking and explaining your work. Allow 5-20 minutes for a changed case or one you try alone. You need Python 3.10+ with its built-in library, a terminal and a text editor. You should know how to open files, read a small table and make evidence notes. You do not need to write code, install Linux or have admin rights or cloud accounts. Basic network or Wireshark practice may help, but you can start without it.

A **baseline** is the agreed state used to compare changes. The **run-as account** is the identity a task uses. The **action** is the set path to the program. **Change approval** is evidence that allows a specific change. A **snapshot** is a partial view from one time.

## Evidence and exact rules

The case JSON is the source used for all results. The supplied cases are guided.json, changed.json and challenge.json. All data is made up. The artifacts field is empty, so there is no second copy to edit. Edit only a copy made by prepare. The analyser just works out results. It never runs text from the evidence as a command.

data has three lists: baseline, observed and approvals. Each row has id, daily_time, account and action. Use 24-hour HH:MM for daily_time. The action is a literal path under the made-up C:/Lab/ folder. Approval rows also need a reason with some text. Each ID must be unique within its list. An approval ID must also be in observed. The tool opens no path and runs no task command.

Check each ID in baseline or observed. Use the rules in this order. If it is absent from observed, use missing-from-snapshot. If its time, account and action match the baseline exactly, use matches-baseline. Otherwise, check the approval for that ID. If all three fields match it exactly, use approved-maintenance-difference. A new ID with no matching approval gets unregistered-task-review. Any other changed ID gets unapproved-change-review.

Compare the text exactly, including uppercase and lowercase letters. Do not treat different text as equal just because Windows may use it for the same path. Approval for one field does not allow changes to the other fields.

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

The tool compares daily time, account and the literal action path exactly. It does not parse Windows Task Scheduler XML. A match with approval or baseline does not check program contents or access rights. It does not prove that a task ran or that it is safe. No task was created or run.

Use WORKED-EXAMPLE.md after you save your first choices. Use DRILLS.md to try tasks with less help. Do not use these lesson rules to judge a real host. Do not change a real host as part of this lab.

## Primary references

These sources explain the ideas used here. The small data format and teaching rules belong to this lab. The links were checked when the lab was written on 23 October 2026. You need no internet link to run it.

- [Microsoft scheduled task fields](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create)
