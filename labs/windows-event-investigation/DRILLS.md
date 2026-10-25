# Practice with less support

## Guided

Open `guided.xml`. Highlight each process GUID once and each parent GUID once.
Draw only the matches on the same computer. Explain why the nearby record 104
does not join the 101 -> 102 -> 103 chain. Then inspect and compare your notes
with the worked example. Mark the help you used.

## Prompts only

Prepare a fresh worksheet. Hide the worked answer and use five prompts:

1. Which computer and record IDs am I using?
2. Where does each parent GUID match an actual creation record?
3. What would a PID-only match get wrong?
4. Which time field did I sort, and which other time did I preserve?
5. What remains unobserved, and what is the next useful evidence?

## Independent changed case

Read `changed.xml` without analysis output. Explain the two occurrences of PID
2000 and identify 203's parent by its full GUID. Describe what Event 1 cannot
tell you about when record 201's process ended. Use a fresh inspect run after
saving your answer; a matching numeric answer alone is not sufficient.

## Missing-parent challenge

Read `challenge.xml`. Write the chronological record order and decide whether
301 is 302's parent. Explain why an absent parent is not a finding of malicious
behaviour. Request one specific extra slice of evidence. Only then inspect it.

## Make one small evidence change

Prepare a new run, then manually save a copy of `challenge.xml` into it using a
new filename. Keep the original fixture unchanged. In the copy only, replace
302's `ParentProcessGuid` with 301's full process GUID. Predict the result, then
inspect the copy into another fresh run. The changed relationship demonstrates
how the parser follows supplied data; it does not authenticate either file.
Record that you deliberately edited synthetic evidence.

Change one timestamp to an invalid date in a second copy. Confirm the inspector
refuses it and creates no analysis run. Undo nothing in the original fixture.

## Optional real VM repetition

Follow the README in the disposable VM. Make a second fresh capture with a
different harmless printed marker. Do not reuse the synthetic GUIDs or record
IDs. Find your chain without searching the worked answer. Keep both exports
private and separate. Explain any missing parent rather than hiding the gap.

## Teach-back and later recall

Explain to another learner why an executable name, PID and process GUID answer
different questions. Demonstrate how you selected XML event data rather than
an XML filter query. Explain why no Event 3 records in this lab cannot prove no
network traffic. A day later, rebuild the chain from a fresh worksheet with the
answer closed and state which help you needed.

## Handover prompt

"My question was __. My evidence was synthetic / a capture I performed in __.
The source hash and window were __. Records __ support __ because __. I cannot
establish __. The next evidence I would request is __. I used __ for help."

Completing a command is not mastery. A reviewer should check the reasoning,
evidence references and honest limits, including an unfamiliar variation.
