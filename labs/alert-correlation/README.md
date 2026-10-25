# Alert deduplication and correlation

Separate repeat copies from unique alerts. Then group related evidence with a stated time-window rule. Alert counts do not prove how many incidents took place.

This made-up lab was written for beginners and runs offline. It is practice, not copied coursework or proof of work done in a job. No one has yet assessed your work or skill.

## Before you start

Allow **30-45 minutes**. Spend 5 minutes reading, then 10 on the evidence and your first choices. Spend 10 minutes checking and explaining your work. Allow 5-20 minutes for a changed case or one you try alone. You need Python 3.10+ with its built-in library, a terminal and a text editor. You should know how to open files, read a small table and make evidence notes. You do not need to write code, install Linux or have admin rights or cloud accounts. Basic network or Wireshark practice may help, but you can start without it.

A **delivery** is one received record. **Deduplication** removes repeat copies with the same ID and content. **Correlation** brings related evidence together. An **anchor window** starts at the first event. It is not measured from the most recent event. An **incident** needs more evidence than alert counts alone.

## Evidence and exact rules

The case JSON is the source used for all results. The supplied cases are guided.json, changed.json and challenge.json. All data is made up. The artifacts field is empty, so there is no second copy to edit. Edit only a copy made by prepare. The analyser just works out results. It never runs text from the evidence as a command.

data.window_seconds is a whole number from 1 to 3600. Each alert has an id, a made-up lowercase host.test, a simple account name and a UTC time to seconds. Its kind is auth-failure, auth-success or process-alert. Rows with the same ID and full content are repeat copies. The tool rejects rows that share an ID but differ in content. Different IDs stay separate.

Remove repeat copies before you count. Group by exact host/account. Sort each group by timestamp, then ID. Start a session at its first alert. This is the anchor. Keep alerts up to window_seconds after that anchor, including the exact end time. A later alert starts a new session. The window does not slide. Use host/account/session-number for each key.

Use these rules in order. If at least three failures occur strictly before a success in one session, use review-auth-sequence. Otherwise, a process-alert with either auth-failure or auth-success gives review-mixed-signals. Use retain-context for all other groups. These rules choose what to review in this exercise. They do not count confirmed incidents.

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

To remove a repeat copy, both the alert ID and all its content must match. Keep different IDs even when the text or times match. The lab does not check if clocks are right or sensors cover all events. It does not check who owns accounts or whether actions were approved. No service or endpoint was contacted.

Use WORKED-EXAMPLE.md after you save your first choices. Use DRILLS.md to try tasks with less help. Do not use these lesson rules to judge a real host. Do not change a real host as part of this lab.

## Primary references

These sources explain the ideas used here. The small data format and teaching rules belong to this lab. The links were checked when the lab was written on 23 October 2026. You need no internet link to run it.

- [NIST log management guidance](https://csrc.nist.gov/pubs/sp/800/92/final)
