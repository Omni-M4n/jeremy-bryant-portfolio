# Practice with less support

## Guided

Open `guided.xml`. Mark each process GUID once and each parent GUID once. Draw only matches on the same computer. Explain why nearby record 104 does not join the 101 -> 102 -> 103 chain. Save your notes, then inspect the file. Compare with the worked example. State what help you used.

## Prompts only

Prepare a fresh worksheet. Hide the worked answer and use these five prompts:

1. Which computer and record IDs am I using?
2. Where does each parent GUID match a real creation record?
3. Could a match based only on PID be wrong?
4. Which time field did I sort? Which other time did I keep?
5. What is still unseen? What evidence would help next?

## Independent changed case

Read `changed.xml` with the analysis closed. Find any repeated PIDs. Use full GUIDs to test the possible parent links. State what these Event 1 records can and cannot tell you about each process. Save your reasons. Then use a fresh inspect run to check them. A matching number alone is not enough.

## Independent challenge

Read `challenge.xml`. Put the records in time order. Use the full GUIDs to test the possible parent links. Explain what the file does and does not show. Ask for one specific extra slice of evidence. Save your answer before you inspect it.

## Make one small evidence change

Prepare a new run. Save a copy of `challenge.xml` in it with a new name. Keep the original unchanged. In the copy only, replace 302's `ParentProcessGuid` with 301's full process GUID. Predict the result. Then inspect the copy into another fresh run. Explain how the parser uses the supplied data. It cannot prove that either file is authentic. Note that you edited made-up evidence on purpose.

In a second copy, change one time to an invalid date. Check that the inspector refuses it and creates no analysis run. Do not change the original case file.

## Optional real VM repetition

Follow the README in your disposable VM. Make a second fresh capture with a different harmless printed marker. Do not reuse made-up GUIDs or record IDs. Find your chain with the worked answer closed. Keep both exports private and separate. Explain any missing parent. Do not hide the gap.

## Teach-back and later recall

Explain why a program name, PID and process GUID answer different questions. Show how you chose XML event data instead of an XML filter query. Explain why a lack of Event 3 records here cannot prove a lack of network traffic. A day later, rebuild the chain from a fresh worksheet with the answer closed. State which help you needed.

## Handover prompt

"My question was __. My evidence was made up / a capture I performed in __. The source hash and window were __. Records __ support __ because __. I cannot show __. The next evidence I would request is __. I used __ for help."

Finishing a command does not prove mastery. A reviewer should check the reasons, evidence references and stated limits. That review should include a less familiar case.
