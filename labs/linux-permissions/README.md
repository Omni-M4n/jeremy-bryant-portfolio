# Linux mode bits and directory traversal

Check a made-up user's access to files and folders. Use the owner, group and other mode bits. Explain why a user may have read access to a file but still be unable to reach it.

This is a made-up, offline exercise for a new security learner. It is original practice, not copied coursework. It does not count as work experience. Completion and skill remain unassessed.

## Before you start

Allow **30-45 minutes**. Spend about 5 minutes reading and 10 checking the evidence and making predictions. Use 10 minutes to check and explain your answers. Allow 5-20 minutes for a changed case or a case on your own.

You need Python 3.10 or newer, a terminal and a text editor. Only Python's standard library is used. You should be able to open files, read a small table and write evidence notes. You do not need coding skills, admin rights, Linux or a cloud account. Some basic network or Wireshark practice may help, but is not required.

## Key words

A **directory** is a folder. **Owner, group and other** are three classes of access rights. Only one class is used for each check. **Mode bits** store those rights. **Octal** is base eight. Here each digit is a sum of 4, 2 and 1. **Directory search** lets a user pass through a folder to find a named item. An **ancestor** is a folder above an item in its path. An **ACL** adds access rules outside this model. **Metadata** is data about a file, such as its size.

## Evidence and exact rules

The case JSON is the sole input. JSON stores named fields and lists as text. The starting cases are guided.json, changed.json and challenge.json. All data is made up. The artifacts field is empty, so there are no extra copies to edit. Edit only a prepared run copy. The tool works out results from this data. It never runs the evidence text as code.

The data field holds these records:

| Record | Required content |
| --- | --- |
| actor | Name and full list of groups. |
| nodes | A canonical absolute path, type, owner, group and three-digit octal mode for each node. |
| requests | An ID, path and operation for each request. |

A node is a file or folder in the case. Include `/` and every ancestor folder. An absolute path starts at `/`. Canonical means one clear path form. It has no `.` or `..` parts, repeated slashes or trailing slash, except for `/` itself. The model accepts only ordinary files and folders. The actor must not be root, the account with system-wide powers. Special mode bits, links and missing ancestors are rejected. The tool does not inspect or change your computer's real access rights. It reads case files and creates practice files when you use prepare.

Select one class of bits for each node:

1. Use owner bits if the actor owns it.
2. Otherwise, use group bits if the node's group is in the actor's group list.
3. Otherwise, use other bits.

Do not switch to a class with more rights if the chosen class fails. Read is 4, write is 2, and execute or search is 1. Every ancestor folder must allow search.

| Target operation | Required target bits |
| --- | --- |
| `read-file` | 4: read. |
| `write-file` | 2: write. |
| `execute-file` | 1: execute. |
| `list-dir` | 4: read. |
| `search-dir` | 1: search. |
| `create-entry` | 3: write plus search. |

Use `allowed-by-mode` only if all required target bits and all ancestor search checks pass. Otherwise use `denied-by-mode`. `list-dir` means listing names only. It does not mean reading file contents or metadata.

## Run the exercise

Open a terminal in this lab folder. Use your Python command. It may be `python`, or `py -3` if that is how you installed it. All commands below use `python`.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the evidence. Open run/attempt-01/answers.json. Fill each decision with an exact label from the rules. Add your reasons and evidence references. These could be record IDs or settings line numbers. In notes.txt, keep separate notes for what you saw, what it means, doubts, your next check and help used. Save your prediction before you open the answer.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

For changed and challenge, use the right attempt folder in show, analyse and check. The prepare command refuses a folder that already exists. The --out path starts from this lab folder and must be below run/. Input paths start from your current terminal folder. Without --case, analyse and show use the guided case.

Exit code 0 means success or a decision match. Code 1 means a mismatch or blank written fields. Code 2 means invalid input or a file system problem. The checker compares decisions and checks that writing is present. It does not judge your reasons. The verify command checks the supplied cases. It does not assess your skill.

## Deliverable and limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. This folder is left out of version control. Write a short handover with the question, your conclusion and two exact evidence references. Add one other possible explanation or limit. State what evidence you would seek next. Record whether you used the worked example and tried a fresh case unaided. A tool match is not an assessment or work experience.

Owner bits take priority over group bits, then other bits. There is no fallback to a class with more rights. All ancestor folders need search access, also called execute. This model checks only ordinary mode bits for a made-up user without special powers.

It leaves out ACLs, SELinux, capabilities, special bits, symlinks and mount restrictions. These are other Linux rules or features that can affect access. It has not inspected or changed your host's access rights.

Use WORKED-EXAMPLE.md after your first prediction. Use DRILLS.md to practise with less help. Do not treat these rules as a verdict on a real system's safety. Do not change a real host for this exercise.

## Primary references

These guides explain the core ideas. The small data format and teaching rules belong to this lab. The links were checked when the lab was written on 23 October 2026. You do not need the internet to run the lab.

- [Linux path resolution manual](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
- [Linux inode and mode manual](https://man7.org/linux/man-pages/man7/inode.7.html)
