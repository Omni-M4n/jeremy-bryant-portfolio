# Worked example: desk connection

The intended pair is user `labuser` with key `k1`. The host fingerprint was
checked. The direct console was tested, so `r1` is `recovery-tested`.

Trial `t1` used that pair. The method was `publickey`. It was accepted,
so record `intended-key-accepted`. Trial `t2` offered `k2` to the same user. The
server rejected the key login, so record `alternate-key-rejected`.

Cite the expected pair, host check, recovery field and both trial records.
These records show only the tests made. They do not prove that all other accounts
or keys are denied. In live practice, keep the client and server lines for each
test. The phrase "login failed" alone does not say why it failed.
