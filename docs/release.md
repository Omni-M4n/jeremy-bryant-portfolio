# Portfolio release design

## Static architecture

Plain HTML, CSS, JavaScript and SVG; no npm dependencies, Worker handler, database, sessions, uploads, forms, third-party scripts or analytics. The site is prepared for its own Cloudflare Pages project at `https://jeremy-bryant.pages.dev/`, with public resources served from `/`.

Unknown paths return the custom 404 page with a 404 status. The `/source/` page provides a sanitised source ZIP and project notes; `/lab-files/<id>/` provides each exercise's README and a route to the full download. The archive contains the selected project source, exercises and synthetic fixtures without Git history.

The portfolio is public by direct link. HTML and response headers request `noindex, nofollow, noarchive`. This is discovery control, not authentication.

Responses use `Cache-Control: public, max-age=0, must-revalidate, no-transform` and a same-origin content security policy. No analytics beacon is included in the project.

## Applicable checks

`node scripts/build.mjs` validates the 20-lab expansion and four hands-on catalogs, checks required
learner files, refreshes the plain-text practice-guide mirror from
`labs/PRACTICE-GUIDE.md`, and builds the static site. The catalog uses native
expandable entries; it adds no browser dependency. `npm test` includes catalog
escaping, destination and identity checks alongside the site checks.

The source download includes 30 exercises. The four hands-on workflows use
separate lab directories and do not change the reviewed twenty-lab fixture
manifest. Their Python suites check application behaviour, packet generation
and XML interpretation. Record actual Wireshark, Burp, Snort and Sysmon runs
separately; a missing external tool must not be replaced with a claimed result.
The public website serves only static instructions and downloads. It never runs
the local training servers, packet inspection or Windows collection workflow.

For the new lab family, `python labs/check_foundation_release.py` verifies the
reviewed source inventory. Its optional `--tests` runs isolated domain suites,
shared-runtime checks and all sixty reference cases. Test receipts may be reused
only when their exact source hashes still match. Domain explanations and learner
readiness require a separate review; file integrity does not establish them.

- Validate links, responsive layout, keyboard navigation, menu and diagram interactions.
- Validate custom 404, unknown/encoded paths and the intended boundary between public downloads and unpublished source files.
- Use a same-origin CSP, frame denial, MIME protection, referrer and permissions policies, HTTPS and noindex headers.
- Scan the selected source, output and downloadable archive for accidental credentials, household identifiers and unrelated identity links without printing any suspected private value.
- Confirm the Pages project and authenticated account before publishing.
- Verify all published portfolio pages, assets, lab README pages and the source download.
- No dependency audit is required for an empty website dependency graph; the deployment tool is an existing external tool, not shipped to visitors.
- Authentication/CSRF/database/upload controls are not applicable because these features do not exist. Reconsider them if architecture changes.

## Rollback

The portfolio uses its own Cloudflare Pages project and deployment history. Roll back that project to a verified working deployment using its supported deployment controls. Retain the previous build and private deployment receipts so the selected source, output and published version can be reconciled.
