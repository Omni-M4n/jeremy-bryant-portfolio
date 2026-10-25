# Cache notebook 1: worked example

First draw `www.school.test -> site.school.test`. At second 30, q01's alias has `0 + 60 - 30 = 30` seconds left. Its A record has `0 + 120 - 30 = 90`. Both are usable, so q01 is `cached-answer:192.0.2.20`. The source's new `.21` address does not rewrite this saved answer.

For q02, the AAAA record has `40 - 30 = 10` seconds left, so the answer is `cached-answer:2001:db8::20`. The A and AAAA timers are separate. For q03, the MX record has `90 - 30 = 60` seconds left. Its answer is `cached-answer:10 mail.school.test`. That value names a mail exchanger; a separate address lookup would be needed to connect to it.

Save the arithmetic beside each query ID. None of these answers proves that a host is reachable. A later source change, a missing refresh or a different resolver could give a different result. Keep the worked example closed during the later cases.
