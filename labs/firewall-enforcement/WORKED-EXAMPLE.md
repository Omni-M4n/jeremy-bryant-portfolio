# Connection notebook 1: worked example

Both p01 and p02 connect before the change. That establishes a useful baseline. During the change, p01 still connects on port 8000, giving `permitted-supported`.

Port 8001, p02, now times out. A timeout by itself is weak evidence. Here its listener is still present, the isolated matching drop counter rises by three packets, and the allowed control still works. Together those support `deny-supported-by-control-and-counter`. Three packets do not mean three connections; retries may account for them.

After removal, both paths connect. The rule is recorded as removed and the saved exports have the same hash. That supports `rollback-supported` for this limited change. Inspect the source exports too; a fingerprint cannot tell you whether the baseline was appropriate. These are supplied invented observations, not proof of a real rule change.
