# Investigate DNS records and caching

A school changes its website address. One computer still remembers the old address for another minute. That can be a valid remembered answer even after the source changes. This lab asks **which saved DNS entries can answer a question at a given second?**

This extends [dns-triage](../dns-triage/README.md). That lab matches requests and replies. This lab adds chains of names and checks when saved records expire. First complete the earlier lab's evidence task. Allow 25 minutes, then 10 minutes to recall it later.

## Words before fields

- **DNS** is the name lookup system. A **record** is one piece of its answer.
- **A** gives an IPv4 address. **AAAA** gives an IPv6 address. These are two address systems; neither proves the website works.
- **CNAME** says to follow another name. **MX** gives a mail server name and a preference number; smaller numbers are preferred. MX does not give a website address.
- A **cache** stores an earlier answer. **TTL** is its time limit in seconds.
- **NXDOMAIN** says the name did not exist. **NODATA** says this record type was absent. Both can be saved as a **negative answer**. **SOA** is a zone's control record. Here, its TTL and MINIMUM field set the time limit for a saved negative answer.

## Run the supplied exercise

Python 3.10+ on Windows, Linux or macOS is enough. No libraries, resolver settings or internet connection are needed. From this folder:

```text
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Save your record map, predicted answers and calculations in `run/attempt-01/notes.txt`. Fill `answers.json`. Keep the first attempt, then use:

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

Use a new folder for every attempt. `analyse` and the reference folder reveal answers. `check` compares decision fields and requires written notes. A person must review those notes. These checks do not show that you used a real tool or reached a skill level.

## Exact small model

The three input lists are `records`, `negatives` and `queries`. A query is a question sent to DNS. Queries do not update the supplied cache. Each record has one owner name, type, value, receipt time and TTL. The receipt time is when it was saved. There is only one value per owner/type. Names use `.test`; addresses use `192.0.2.0/24` or `2001:db8::/32`. Seconds are whole numbers from 0 to 86400. Every query is at or after all receipt times. The helper rejects unknown fields, repeated entries and alias loops. An alias loop leads back to a name already checked. It also rejects positive and negative evidence that conflict.

Remaining life is `max(0, received + TTL - at)`. If this is above zero, the saved record can be used. Zero means it must be refreshed. This includes the exact expiry second and any record with TTL zero. When following an alias to answer another record type, each alias and the final answer must be fresh. A direct CNAME question needs only the fresh alias record. The source change in the notebook does not shorten a TTL that was already saved. The old value can still be used until it expires. Do not call every old value expired.

For a negative entry, replace TTL with the smaller of `soa_ttl` and `minimum`. NXDOMAIN covers the listed record types for the same exact name. NODATA covers only its recorded type. This model leaves out rules for child names and saved errors. It also leaves out record sets with more than one value and resolver caps, which limit cache times. Prefetch means fetching early; serve-stale means using expired data. Those features and DNSSEC, which checks signed DNS data, are outside this model too. Missing cache data means refresh-required, not NXDOMAIN. `cached-answer:<value>` and `cached-negative:<kind>` describe only this snapshot.

## Evidence and handover

Save a table with each query ID, name path and record purpose. Add the expiry, seconds left, your prediction and any doubt. Predict before changing a TTL in a copied case. Explain which value changes at once and which saved value does not. Give another learner your table. Ask them to check one expiry without viewing the answer. The supplied cases are made up; no real resolver was run. You may remove your own `run/` practice files after saving first attempts.

## Primary references

Read on 2026-10-25. The exercise is an intentionally smaller model of these rules.

- [RFC 1034, record types, aliases and TTL](https://www.rfc-editor.org/info/rfc1034/)
- [RFC 2308 sections 3 and 5, negative caching](https://www.rfc-editor.org/info/rfc2308/)
- [RFC 3596, AAAA records](https://www.rfc-editor.org/info/rfc3596/)
