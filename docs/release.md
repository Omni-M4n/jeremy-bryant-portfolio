# Portfolio release design

## Static architecture

Plain HTML, CSS, JavaScript and SVG; no npm dependencies, Worker handler, database, sessions, uploads, forms, third-party scripts or analytics. All public resources live under `/portfolio/`. The main website is deployed independently.

Cloudflare routes reserve the `/portfolio` prefix for this separate static deployment, including the bare path and query-string cases. Unknown paths within that prefix return a real 404. Existing main-site sections are not rebuilt or changed.

The portfolio is public by direct link. HTML and response headers request `noindex, nofollow, noarchive`. This is discovery control, not authentication. No inbound links or sitemap entries are added to the main site.

Responses use `Cache-Control: public, max-age=0, must-revalidate, no-transform`. Cloudflare documents that `no-transform` prevents its automatic analytics-beacon injection. This keeps the portfolio's same-origin policy and dependency-free delivery intact without changing the main site's analytics settings. See [Cloudflare Web Analytics setup](https://developers.cloudflare.com/web-analytics/get-started/).

## Applicable checks

- Validate links, responsive layout, keyboard navigation, menu and diagram interactions.
- Validate custom 404, unknown/encoded paths and inaccessible repository files.
- Use a same-origin CSP, frame denial, MIME protection, referrer and permissions policies, HTTPS and noindex headers.
- Scan the selected source, output and Git history for accidental credentials and household identifiers without printing any suspected value.
- Confirm route ownership and the authenticated account before publishing.
- Compare existing main-site routes before/after and verify all published portfolio pages/assets.
- No dependency audit is required for an empty website dependency graph; the deployment tool is an existing external tool, not shipped to visitors.
- Authentication/CSRF/database/upload controls are not applicable because these features do not exist. Reconsider them if architecture changes.

## Rollback

The portfolio has its own Cloudflare Worker name and deployment history. Roll back only that service to a known working version, or remove only its two portfolio routes to restore the main site's prior response for those paths. Never reassign the apex domain or change another section's routes as part of a portfolio rollback. Retain private deployment receipts with the version and previous route state.
