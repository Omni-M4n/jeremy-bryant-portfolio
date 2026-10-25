# Guided worked example

Read this after saving your first attempt. This is a fictional example, not a
claim that a learner or an author ran a real engagement.

Item-1 has a block rule. No test of that rule is shown. Write `configured-only`.
Do not claim that the path was proved isolated. Item-3 has the same gap.
Both need a later test within the owner's scope.

Item-2 was reachable. It lists a named service identity, a record permission
check and TLS. These are separate checks. Being on Wi-Fi proves none of them.
TLS protects data in transit; it does not grant record access.

A possible drawing is guest -> network rule -> service identity -> record
permission -> store. If the network rule fails, the service should still refuse
a record request with no permission. That claim needs its own test evidence.
No connection was tried for this example.

Expected guided decision strings:

```json
{
  "item-1": "configured-only;listed-service-checks-present",
  "item-2": "path-reachable;listed-service-checks-present",
  "item-3": "configured-only;listed-service-checks-present"
}
```

Keep the first attempt. Write corrections in a separate file, explaining which
fact changed your answer. A useful explanation names the evidence and its limit.
