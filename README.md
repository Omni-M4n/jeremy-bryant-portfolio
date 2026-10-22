# Jeremy Bryant — cybersecurity portfolio

A personal career portfolio, documented owner-controlled LG webOS home lab and original guided security exercises.

- **Portfolio:** https://deadgoodreviews.com/portfolio/
- **Full case study:** https://deadgoodreviews.com/portfolio/lg-webos-lab/
- **Security foundations labs:** https://deadgoodreviews.com/portfolio/security-labs/
- **LinkedIn:** https://www.linkedin.com/in/jeremy-bryant-61347a445/

## The project

The completed core lab integrates existing community Homebrew tooling and Glasshouse on an LG 50UT8050PSB running webOS 10.3.2. The goal was a maintainable, customised television that retained its everyday functions and a tested stock-home fallback.

Verified project checks include administrator access, key-based SSH with Telnet disabled, startup after restart, Glasshouse startup and fallback, and restoration of temporary installation networking. Normal PS5 and streaming use was owner-tested. These are point-in-time results from 21 October 2026, not a live service status or comprehensive security assessment.

The separate Chiaki extension remains **in progress**: desktop registration and TV configuration transfer succeeded, but streaming audio/video and Bluetooth controller behaviour still need verification.

## Contribution and attribution

Jeremy owned and operated the hardware, selected goals and appearance, provided observations and performed physical restarts and playback tests. The scripts in this repository are project utilities; upstream developers authored the exploit and applications.

Credits: [webOS Homebrew](https://www.webosbrew.org/), [throwaway96](https://github.com/throwaway96), [Glasshouse](https://rorygallagher2024.github.io/glasshouse/), [TacticalBill/chiaki-lg](https://github.com/TacticalBill/chiaki-lg), [chiaki-ng](https://github.com/chiaki-ng/chiaki-ng) and [Qt](https://github.com/qt/qtbase).

## Guided security exercises

The [labs](labs/README.md) contain 26 original offline exercises. The first six
cover DNS, login events, access review, HTTP logs, file integrity and firewall
rules. Twenty additional labs develop network investigation and testing,
defensive operations and recovery, and cloud, identity and configuration review.
Each includes synthetic fixtures, a worked example, verification and progressive
practice. The [expanded catalog](https://deadgoodreviews.com/portfolio/security-labs/foundations/)
lists each purpose, prerequisite and deliverable.
The materials have automated reference checks; Jeremy's independent completion
of unfamiliar variants remains to be assessed. These exercises do not claim
production experience or independent authorship of every utility.

The [practice guide](labs/PRACTICE-GUIDE.md) develops each topic through short
walkthroughs, independent attempts, changed scenarios and later recall checks.

## Repository map

| Path | Contents |
| --- | --- |
| `src/` | Portfolio, case study, local assets and downloadable brief |
| `scripts/` | Dependency-free static build, public-output checks and loopback preview |
| `tools/` | Qt INI pairing-format converter; no real pairing data |
| `labs/` | Original guided exercises, synthetic fixtures, checks and practice instructions |
| `tests/` | Static-site checks and synthetic converter tests |
| `docs/verification.md` | Sanitised evidence and limitations |
| `docs/recovery.md` | Recovery design and operational boundaries |
| `docs/release.md` | Static hosting, publication controls and rollback |

## Local development

Requires a current Node.js release; the website has no runtime or npm dependencies.

```sh
npm run build
npm run check
npm test
npm run preview
```

Open `http://127.0.0.1:8796/portfolio/`. The preview binds to loopback only. No device is contacted by website build or tests.

The converter requires Python 3.9+ and the standard library. Tests use synthetic byte arrays:

```sh
python -m unittest discover -s tests -p "test_*.py"
```

See [`tools/README.md`](tools/README.md) before processing an actual export. Pairing exports and generated configuration are credentials and must remain outside this repository.

## Publication

The portfolio is a separate Cloudflare static-assets deployment under `/portfolio/`. It does not rebuild the main Dead Good Reviews site or add a main-site navigation item. It is public to anyone with its URL; `noindex` asks search engines not to index it and is not access control.

The repository contains no private keys, pairing exports, raw device logs or user-specific networking data. There is no contact form, analytics, advertising, account system, database or external browser dependency in the portfolio.
