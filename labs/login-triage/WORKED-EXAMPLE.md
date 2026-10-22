# Worked example: seed 41, baseline

Try the fixture yourself before reading this answer. This is a model explanation for guided practice, not a record of learner performance.

## First reconstruct the timeline

```sh
python lab.py timeline --user practice-staff-041
python lab.py timeline --user practice-editor-041
python lab.py timeline --user practice-sync-041
```

All times below are invented UTC times on **7 April 2032**. The CSV is shuffled, so reading rows from top to bottom would give the wrong sequence.

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

Default settings are five failures, a 300-second failure window and a 120-second later-success link. The result is **two qualifying windows across one account/address pair**:

| Window end | Inclusive failure window | Counted failures | Linked success |
| --- | --- | --- | --- |
| 09:26:40 | 09:21:40–09:26:40 | `SYN-0001`–`SYN-0005`, count 5 | `SYN-0007` at 09:28:20, 100 seconds later |
| 09:27:20 | 09:22:20–09:27:20 | `SYN-0001`–`SYN-0006`, count 6 | `SYN-0007` at 09:28:20, 60 seconds later |

These windows overlap and use the same later success. They describe one observed sequence and do not establish two incidents. The first window starts before the first available event because the start is a calculation from the window end. Do not infer that records exist for that earlier time.

Now widen the failure window to one hour:

```sh
python lab.py triage --window-seconds 3600 --output runs/worked-wide-report.json
python lab.py verify --report runs/worked-wide-report.json
```

The result is **four qualifying windows across two pairs**. The service account now reaches five and six failures within an hour. Its two windows have no linked success. If every match were labelled an attack, the service's stale saved password would be a false positive for that claim. The same records can deserve operational follow-up without evidence of a security incident.

## Example handover

> Review requested: the synthetic account `practice-staff-041` has six failed sign-ins from `192.0.2.52` between 09:24:00 and 09:27:20 UTC on 7 April 2032 (`SYN-0001`–`SYN-0006`), followed by a success at 09:28:20 (`SYN-0007`). With a five-failure/300-second rule and a 120-second success link, two overlapping windows describe the same sequence. The success is 60 seconds after the final failure. This could reflect password guessing or repeated legitimate errors; these records do not establish the actor or compromise. Please confirm the activity with the account owner and review device, additional sign-in verification and post-sign-in activity records. The editor's two failures align with the supplied typo note; the automated sync account's 11-minute failures align with its stale-password change note and need operational follow-up. No account actions were taken in this exercise.

The handover names evidence, retains uncertainty, separates likely explanations, and asks for checks that could change the decision. It does not claim that a successful attack or an independently verified benign explanation has been proven.
