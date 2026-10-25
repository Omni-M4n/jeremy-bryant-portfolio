# Worked example: Library account record

Open this after your prediction. e1 has label-a once. e2 has label-b once.
Both records say generated=true and length=24. Each gets
meets-practice-checks under the worksheet's limited rules.

The backup exists and is encrypted. But unlock_test=false means no one has
tested whether it can be opened. separate_location=false means one lost
location could cost both copies. recovery_in_same_store=true means the
recovery steps may be locked away when needed. Join the findings to give
restore-untested+same-location-risk+circular-recovery.

A useful note says: "The record shows that the file was copied.
It does not show a restored copy being opened. I need to test unlock and
check its entries while keeping the original safe."
Do not claim from these records that the account is secure.

In Part A, hold keeps store.json as held-original.json. Restore copies
backup.json back to store.json. Equal bytes after restore show that the
dummy file was recovered. They do not prove an encrypted vault will unlock.
Only a separately recorded Part B run can give that evidence.
