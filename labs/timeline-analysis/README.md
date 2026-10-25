# Put event times in order

Two logs may show different times for the same moment. In this lab, put times on the UTC scale. Then correct a known clock error. Use the remaining margin of error to decide whether one event must have come first.

These are fictional practice records. They are not copied coursework or records from a real incident. The materials do not show that a learner has completed the work.

## Before you start

Allow **30–45 minutes**, or split the task into short sessions. Spend 5 minutes reading, 10 on evidence and predictions, and 10 on checks and notes. Use the remaining 5–20 minutes for another case.

You need Python 3.10 or later, a terminal and a text editor. Python's standard library is enough. You need to open files, read a small table and save notes. You do not need to write code, use admin rights, install Linux or open a cloud account. Earlier network or Wireshark practice may help, but is not required.

Four terms matter here:

- **UTC offset:** how far a displayed time is ahead of or behind UTC.
- **Clock skew:** an error in a device's clock, compared with a reference clock.
- **Uncertainty bound:** how far the true time may be from your estimate.
- **Causation:** one event causing another. Time order alone does not prove this.

## Read the case

The case JSON is the one source of input. The supplied files are guided.json, changed.json and challenge.json. The artifacts field is empty, so there is no second copy to edit. Work on a prepared copy below run/. The analyser does maths on the records. It never runs text from them as code.

Each record in data.events has an ID, timestamp, clock_offset_seconds, uncertainty_seconds and description. A timestamp must include seconds and either Z or a numeric UTC offset. Dates with no timezone, or impossible dates, are rejected.

The signed clock offset can be from -86400 to +86400 seconds. Uncertainty can be from 0 to 3600 seconds. Each item in data.pairs has a unique comparison ID and two different event IDs. Both events must exist in the case.

## Use the rules

1. Convert the recorded time to UTC.
2. Subtract clock_offset_seconds. A positive value means the device clock was fast.
3. Treat this corrected time as the centre of a range. Subtract uncertainty_seconds for its lower bound. Add it for the upper bound. Both endpoints belong to the range.
4. Compare the two ranges, using these exact labels:

- **definitely-before:** the left event's upper bound is strictly below the right event's lower bound.
- **definitely-after:** the left event's lower bound is strictly above the right event's upper bound.
- **order-uncertain:** every other case. The ranges may overlap, touch at one endpoint or be identical.

These labels describe time order. They do not say that one event caused another.

## Run the exercise

Open a terminal in this lab folder. Use your Python command (`python`, or `py -3` if that is how Python is installed). The examples use `python`.

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the records. In run/attempt-01/answers.json, give each pair an exact decision label. Add your explanation and event IDs as evidence. In notes.txt, keep facts, your interpretation, remaining doubt, the next check and help used separate. Save this first answer before viewing a solution.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python lab.py prepare --scenario changed --out run/attempt-02
python lab.py prepare --scenario challenge --out run/attempt-03
python -m unittest -v test_lab.py
python lab.py verify
```

Use the matching attempt folder in show, analyse and check for each later case. The prepare command refuses an existing folder. Its --out path starts from this lab and must stay below run/. Explicit input paths start from your terminal's current folder. If you omit --case, analyse and show use the supplied guided case.

Exit 0 means the command worked or the decisions match. Exit 1 means a mismatch or missing written fields. Exit 2 means bad input or a file problem. The checker looks for decision matches and written text. It cannot judge the quality of that text. The verify command checks the supplied examples, not learner skill.

## Save the result and state its limits

Keep case.json, answers.json and notes.txt together in the ignored run folder. Write a short handover. Give the question, conclusion, two exact evidence references, one limit or other explanation, and a next check. Record help used, including the worked example. A matching label does not prove understanding or work experience.

This model takes the given clock error and uncertainty as valid. Uncertainty is a bound, not a probability. Delays in collecting logs, rounded timestamps and missing events need their own checks.

Read WORKED-EXAMPLE.md after your first prediction. Use DRILLS.md for less support on later attempts. Stay with the local files. Do not change a real host or use this small model to declare a real system safe.

## Primary reference

This source explains log management. The small input format and decision rules belong to this lab. The link was checked on 23 October 2026. You can run the lab offline.

- [NIST Guide to Computer Security Log Management](https://csrc.nist.gov/pubs/sp/800/92/final)
