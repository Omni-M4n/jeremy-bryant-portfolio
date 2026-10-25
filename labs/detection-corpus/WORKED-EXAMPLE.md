# Worked example: record set A

Read this after saving your first attempt.

At threshold 3, tune a1=3 and a2=6 both alert and are exercise rows: TP=2.
a3=1 does not alert and is routine: TN=1. a4=4 alerts but is routine: FP=1.
There are no missed exercise rows. Write **tp=2,fp=1,fn=0,tn=1**.
False alarms are **1/2 routine rows**, not 1/4. Alerts are **3/4 all rows**.
The false share of alerts is **1/3 alerts**. Those three fractions differ.

At threshold 5, tune gives TP=1, FP=0, FN=1, TN=2. It loses a1. On holdout,
threshold 5 gives TP=1, FP=1, FN=1, TN=1: b2 alerts, b4 is a false alarm, and b1
is missed. The tune result did not promise the same holdout result. Record which
error costs you chose to accept. The tool does not choose a universal best rule.

Write the evidence separately from your interpretation. State one thing these
records cannot establish. Keep the first answer and the corrected answer.
