# Worked example: seed 41, baseline

Try the fixture yourself before reading this answer. This answer is a guide for practice. It is not a record of learner performance.

## First reconstruct the timeline

```sh
python lab.py timeline --user practice-staff-041
python lab.py timeline --user practice-editor-041
python lab.py timeline --user practice-sync-041
```

All times below are made-up UTC times on **7 April 2032**. The CSV rows are shuffled. Reading from top to bottom would give the wrong order.

| Account and source | Observed sequence | Interpretation and remaining gap |
| --- | --- | --- |
| `practice-staff-041`, `192.0.2.52` | `SYN-0001`–`SYN-0006`: six failures at 09:24:00, 09:24:40, 09:25:20, 09:26:00, 09:26:40 and 09:27:20. `SYN-0007`: success at 09:28:20. | Repeated failures followed by success warrant review. Password guessing is possible; repeated user error is also possible. There is no user confirmation or device evidence. |
| `practice-editor-041`, `198.51.100.108` | `SYN-0008` and `SYN-0009`: failures at 09:25:10 and 09:25:35. `SYN-0010`: success at 09:26:10. Later successes at 09:40:40, 09:54:00 and 10:04:00. | Two mistakes followed by a successful attempt agree with the invented helpdesk note. There is no five-failure match. This supports lower priority, not certainty about who signed in. |
| `practice-sync-041`, `203.0.113.157` | `SYN-0011`–`SYN-0016`: six failures from 09:24:30 to 10:19:30, exactly 11 minutes apart. No success appears. | The invented change note says an automated job still has an old password. This supports an operational fault. At most one of these failures fits in any five-minute window. |

## Compare the rule with your count

```sh
python lab.py triage --output runs/worked-report.json
python lab.py verify --report runs/worked-report.json
```

The default threshold is five failures. The failure window is 300 seconds. The later-success link lasts 120 seconds. The result is **two qualifying windows across one account/address pair**:

| Window end | Inclusive failure window | Counted failures | Linked success |
| --- | --- | --- | --- |
| 09:26:40 | 09:21:40–09:26:40 | `SYN-0001`–`SYN-0005`, count 5 | `SYN-0007` at 09:28:20, 100 seconds later |
| 09:27:20 | 09:22:20–09:27:20 | `SYN-0001`–`SYN-0006`, count 6 | `SYN-0007` at 09:28:20, 60 seconds later |

These windows overlap and use the same later success. They describe one sequence. They do not prove two incidents. The first window starts before the first event we have. Its start is calculated from the window end. That does not mean records exist for the earlier time.

Now widen the failure window to one hour:

```sh
python lab.py triage --window-seconds 3600 --output runs/worked-wide-report.json
python lab.py verify --report runs/worked-wide-report.json
```

The result is **four qualifying windows across two pairs**. The service account now reaches five, then six failures within an hour. Its two windows have no linked success. Calling every match an attack would create a false positive here. The old saved password is a service fault. These records can need follow-up without proving a security incident.

## Example handover

> Please review the made-up account `practice-staff-041`. It has six failed sign-ins from `192.0.2.52` on 7 April 2032. They run from 09:24:00 to 09:27:20 UTC (`SYN-0001`–`SYN-0006`). A success follows at 09:28:20 (`SYN-0007`). The rule uses five failures in 300 seconds. Its success link is 120 seconds. Two overlapping windows describe the same sequence. The success is 60 seconds after the final failure. Password guessing is one possible cause. Repeated errors by a valid user are another. These records do not identify the actor or prove a break-in. Please ask the owner to confirm the activity. Review device records, extra sign-in verification and actions after sign-in. The editor's two failures fit the supplied typo note. The sync account's failures are 11 minutes apart. They fit its stale-password change note and need service follow-up. No account actions were taken in this exercise.

The handover names evidence and leaves room for doubt. It gives possible causes and checks that could change the decision. It does not claim an attack worked. It does not claim the harmless explanation has been verified.
