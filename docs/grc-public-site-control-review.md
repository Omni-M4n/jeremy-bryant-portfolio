# Public site control review — 13 November 2026

**Technical disposition:** the defined release checks passed. This is a
read-only review of a public portfolio release, not a certification, a
penetration test, or an assessment of account-level security.

**Snapshot boundary:** this result covers source commit `42148d7` and its
[`2fc0165e` deployment](https://2fc0165e.jeremy-bryant.pages.dev/). This
report page and later changes were added after that check. Re-run the rule for
the current Production release.

## Scope and decision rule

The reviewed source was commit `42148d7bcbccd9931643a8eeefb9cafb86bef922`
of `Omni-M4n/jeremy-bryant-portfolio`. The target was
`https://jeremy-bryant.pages.dev/`. The comparison ran at
`2026-11-13T03:00:52Z` against the built `dist/` directory. It made read-only
HTTPS requests. The 109 selected file digests were also compared with the
immutable deployment URL above. No Cloudflare or GitHub account setting was
changed.

The release rule was set by `scripts/verify-live.mjs`: 109 selected built files
must return HTTP 200 with the same SHA-256 digest as the local build; six
specified out-of-scope paths must return HTTP 404; responses must have the
listed security headers; content pages must not carry a `noindex` response
header; the source ZIP must have a ZIP content type. Any mismatch fails the
check. The selected file list excludes the deployment `_headers` file and
custom `404.html`; the latter is checked through the absent-path probes. The
local build and public-output check also had to pass.

## Evidence and limits

| ID | Observation | What it supports | What it does not establish |
| --- | --- | --- | --- |
| P1 | The live check passed 115 requests with zero errors. All 109 selected files matched the local SHA-256 digest. | The served bytes matched that build at the check time. | A matching file is not proof of secure behavior, uptime, or the origin of every source change. |
| P2 | `/.git/config`, `/.env`, `/private/`, `/wrangler.jsonc`, `/labs/foundation_runtime.py`, and an absent-page probe returned HTTP 404. | Those six paths were not served in this release. | Six probes do not enumerate every possible path or prove that no private data exists elsewhere. |
| P3 | The home and GRC responses included a same-origin content security policy, `nosniff`, frame denial, `no-referrer`, a restrictive permissions policy, and one-year HSTS. | The expected response policies were present on the sampled pages. | Header presence alone does not prove browser enforcement or that every page is free of unsafe content. |
| P4 | Content pages used `index, follow`; the live responses had no `X-Robots-Tag: noindex`. | The release did not ask search engines to exclude those pages. | Search engines decide whether and when to list a page. |
| P5 | The downloadable source ZIP returned HTTP 200, the expected ZIP content type, and a digest matching the local archive. | The public download was the built archive at the check time. | A matching archive does not review every sentence, dependency, or future release. |

The [sanitized evidence manifest](grc-public-site-control-manifest.json)
publishes each selected path, digest and status, the six absent-path results,
the sampled home-page response policies and the checked deployment URL. Its
109 file digests were checked again against that immutable deployment. The
full local receipt retains additional response details outside the repository.
This is project evidence, not independent reviewer evidence.

## Decision and next check

The defined publication criteria had no failed item, so the technical release
check passed. This is **not** an approval of residual organizational risk.
The portfolio owner should repeat the comparison after each deployment and
review any changed result before relying on it. The next separate control
review should examine GitHub branch rules, deployment permissions, account
authentication, recovery and a browser-level policy check. None of those
account or recovery controls was assessed here. A reviewer should challenge
the scope and one sampled conclusion before this is described as independently
assessed work.

## Reproduce the check

From a complete checkout with a current Node.js release, build and check the
same source revision. After deploying that build, choose a new receipt filename
outside `dist/` and run:

```sh
node scripts/build.mjs
node scripts/check.mjs
node scripts/verify-live.mjs ../live-check-YYYYMMDD.json
```

The last command reads the public site and writes a local receipt. It does not
publish or change the site. A later release will have a different file count
and digest set. Use the [blank control-review worksheet](grc-control-review-worksheet.md)
to record a fresh decision before comparing with this report.

The [NIST Cybersecurity Framework 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20)
is context for asking who owns a control, what evidence supports it and how it
is reviewed. This exercise does not claim a NIST assessment or compliance.
