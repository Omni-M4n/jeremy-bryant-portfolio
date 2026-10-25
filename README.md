# Jeremy Bryant — cybersecurity portfolio

A career portfolio with an LG TV home lab and guided security practice. The home lab used hardware owned by Jeremy. The security cases use made-up data.

- **Portfolio:** https://jeremy-bryant.pages.dev/
- **Full case study:** https://jeremy-bryant.pages.dev/lg-webos-lab/
- **Security foundations labs:** https://jeremy-bryant.pages.dev/security-labs/
- **Complete lab library:** https://jeremy-bryant.pages.dev/security-labs/library/
- **Summer study plan:** https://jeremy-bryant.pages.dev/security-labs/study-plan/
- **Source and downloads:** https://jeremy-bryant.pages.dev/source/
- **LinkedIn:** https://www.linkedin.com/in/jeremy-bryant-61347a445/

## The project

The LG home lab uses existing community Homebrew tools and Glasshouse. The TV is an LG 50UT8050PSB with webOS 10.3.2. The aim was a custom TV setup that still worked for daily use. It also needed a tested way back to the stock home screen.

The project checks covered admin access, SSH access with a key and Telnet turned off. They also covered restart, Glasshouse startup and the stock-home fallback. Temporary network settings used for setup were put back. Jeremy tested normal PS5 and streaming use. These results date from 21 October 2026. They do not show the device's current state or prove that every security risk was checked.

The separate Chiaki extension is **in progress**. Desktop registration and the transfer of TV settings worked. Streaming sound, video and Bluetooth controller use still need checks.

## Contribution and attribution

Jeremy owned and used the hardware. He chose the goals and appearance, shared what he saw, and tested restarts and playback. The scripts here help with the project. The developers credited below wrote the exploit and apps.

Credits: [webOS Homebrew](https://www.webosbrew.org/), [throwaway96](https://github.com/throwaway96), [Glasshouse](https://rorygallagher2024.github.io/glasshouse/), [TacticalBill/chiaki-lg](https://github.com/TacticalBill/chiaki-lg), [chiaki-ng](https://github.com/chiaki-ng/chiaki-ng) and [Qt](https://github.com/qt/qtbase).

## Guided security exercises

<!-- LAB_COUNTS_START -->
This release has **61 core labs** and **25 extensions**.
<!-- LAB_COUNTS_END -->

The [labs](labs/README.md) contain guided exercises. The first six cover DNS,
login events, access review, HTTP logs, file checks and firewall rules. Twenty
more cover networks, defence, recovery, cloud access and settings. Each has
made-up case files, a worked example, checks and practice tasks. The
[foundation catalog](https://jeremy-bryant.pages.dev/security-labs/foundations/)
lists the aim, skills needed first and work to save.
Four [hands-on tool labs](https://jeremy-bryant.pages.dev/security-labs/hands-on/)
add traffic capture, web access tests, offline Snort rule tests and Windows
event review. Each states its own setup and safe scope. A local script check
does not show that a learner used the separate tool. The supplied cases have
reference checks. Jeremy's work on fresh cases still needs review. These
materials do not claim work on production systems or that Jeremy wrote every
helper on his own.

The [complete library](https://jeremy-bryant.pages.dev/security-labs/library/)
groups the checked packages by topic. An extension adds a task or evidence
source to a core lab. It does not count as a new core topic. Draft packages stay
out of the website and download. Each new package has its own setup, worked
case, practice tasks, checks and limits.

Use the [practice guide](labs/PRACTICE-GUIDE.md) for short sessions and fresh
cases. The [summer study plan](labs/SUMMER-STUDY-PLAN.md) puts skills in order.
It includes two flexible summer starts and recall checks. It is a plan for
learning, not a record of completed work.

## Source map

| Path | Contents |
| --- | --- |
| `src/` | Portfolio, case study, local assets and downloadable brief |
| `scripts/` | Dependency-free static build, public-output checks and loopback preview |
| `tools/` | Qt INI pairing-format converter; no real pairing data |
| `labs/` | Original offline and hands-on exercises, fictional fixtures, checks and practice instructions |
| `tests/` | Static-site checks and synthetic converter tests |
| `docs/verification.md` | Sanitised evidence and limitations |
| `docs/recovery.md` | Recovery design and operational boundaries |
| `docs/release.md` | Static hosting, publication controls and rollback |

## Local development

Use a current Node.js release. The website needs no extra npm packages.

```sh
npm run build
npm run check
npm test
npm run preview
```

Extract the download or clone the repository. Run these commands from that
project folder; its name does not matter. Open `http://127.0.0.1:8797/`.
The preview uses loopback, so only this computer can reach it. The website
build and tests do not contact a device.

The converter needs Python 3.9+ and its standard library. Its tests use made-up bytes:

```sh
python -m unittest discover -s tests -p "test_*.py"
```

Read [`tools/README.md`](tools/README.md) before using a real export. Pairing
exports and the settings made from them grant access. Keep them outside this
repository, like passwords.

## Publication

The portfolio uses Cloudflare Pages at `https://jeremy-bryant.pages.dev/`.
Anyone with the URL can view it. The `noindex` tag asks search engines to leave
it out of results. It does not block access.

The source download leaves out Git history, private keys, pairing exports, raw
device logs and personal network details. The site has no contact form, usage
tracking, ads, accounts or database. It loads no extra browser code from other
sites.
