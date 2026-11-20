# Worked example: supplied register A

Read this only after saving the first guided prediction. The case is synthetic,
and `case.json` is authoritative. It has no extracted evidence artifacts. Its
`as_of` timestamp is exactly `2026-01-15T00:00:00Z`.

## Record `i1`

The supplied fields say:

- value/type: `mail.test` / `domain`;
- evidence ID: `r1`;
- observed: `2026-01-10T00:00:00Z`;
- reported: `2026-01-11T00:00:00Z`;
- valid until: `2026-01-20T00:00:00Z`;
- supplied conflict: false;
- source/confidence/scope: `direct` / 80 / `single-host`.

At `2026-01-15T00:00:00Z`, expiry has not been reached, there is no supplied
conflict, the source is not labelled copied, confidence is stated and at least
70, and scope is not shared. The first matching rule is therefore
`retain-as-context`.

The review-date calculation is exact:

```text
as_of + 7 days = 2026-01-22T00:00:00Z
valid_until    = 2026-01-20T00:00:00Z
earlier value  = 2026-01-20T00:00:00Z
```

Thus the review date is `2026-01-20T00:00:00Z`, five days after `as_of` and two
days before the seven-day candidate. `retain-as-context` does not say the domain
is malicious, safe, owned by anyone or currently in use.

## Record `i2`

The supplied fields say:

- value/type: `relay.test` / `domain`;
- evidence ID: `r2`;
- observed: `2026-01-10T00:00:00Z`;
- reported: `2026-01-11T00:00:00Z`;
- valid until: `2026-01-20T00:00:00Z`;
- supplied conflict: false;
- source/confidence/scope: `copied` / 95 / `single-host`.

The record is not expired and has no supplied conflict. The next rule applies
because source is `copied`, so the decision is `seek-support`. Confidence 95
does not override that earlier condition. Every decision except
`retain-as-context` is reviewed at `as_of`, so the review date is exactly
`2026-01-15T00:00:00Z`.

The smallest next request could ask for the original supporting observation,
its collection context and the person or process that supplied it. That request
does not assert that such material exists or is reliable.

## Supplied-field limits

`direct`, 80, 95, `single-host`, timestamps, expiry and false conflict flags are
all supplied metadata. The helper checks their format and applies the lesson's
rules; it does not verify the original source, collection method, truth,
reliability, independence or corroboration. The original source is unknown
unless separately supplied, and this case supplies no original material. No
lookup, reputation query, blocking action, external submission, attribution or
cross-source link was performed.

A concise handover could say: "For `i1`, expiry, conflict, support and shared
scope did not apply, so I retained it only as context until the earlier date,
2026-01-20T00:00:00Z. For `i2`, the supplied copied label required
`seek-support` and review at `2026-01-15T00:00:00Z`. These are decisions about
supplied metadata, not verified truth. I would request `r2`'s original supporting
observation next."

Keep the first worksheet and any correction. A person must assess whether the
reasoning and limits are sound; two matching labels do not establish independent
skill.
