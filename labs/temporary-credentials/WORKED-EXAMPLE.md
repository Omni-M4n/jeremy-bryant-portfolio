# Worked example: Library session timeline

Open this after your guided prediction. The human `h1` is trusted to use
`role1`. That role permits read. Session `t1` starts at 10 and ends at 70.
Write the interval as [10,70). The square bracket means 10 is included.
The round bracket means 70 is left out.

- q1 is at 9, before issue. Use `not-yet-issued`.
- q2 is a read at 10. Use `allowed-in-model`.
- q3 is at 69, within the time window. But it asks to write, so use `action-not-granted`.
- q4 is at 70. Use `expired`.

For q3, cite role1.actions and t1's times. Being within the time window does
not grant an action. A log that names h1 records who the session came from.
It does not prove who later held the details used to access it.

No real role or credential was created. Record this as an offline timeline
exercise.
