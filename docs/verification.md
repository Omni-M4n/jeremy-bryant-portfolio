# Sanitised project verification

Core device checks were recorded on 21 October 2026. Public summary prepared on 22 October 2026. Original device receipts remain private. This summary distinguishes tool readback from user observation; neither establishes comprehensive security.

| Area | Evidence class | Recorded result |
| --- | --- | --- |
| Device | Recorded metadata | LG 50UT8050PSB, firmware 33.31.75, webOS 10.3.2 |
| Homebrew | Installation/readback | Homebrew Channel 0.7.3 installed |
| Administration | SSH check | Root access verified; key authentication configured |
| Telnet | Configuration/runtime check | Disabled in the completed setup |
| Persistence | Restart and readback | Startup and SSH survived restart |
| Glasshouse | API/readback and restart | 0.118.0 enabled and started automatically |
| Fallback | Switch tests | LG Home and disable/re-enable tested |
| Appearance | Asset readback and owner observation | Wallpaper installed after an initial display problem |
| Normal use | Owner observation | PS5 gaming and streaming applications used successfully |
| Network restoration | Recorded configuration/readback | Temporary PC exceptions/address/server removed; wired TV DHCP restored |
| Chiaki extension | Registration/configuration readback | Registered on desktop; pairing fields transferred with exact byte verification; TV app launched |
| Chiaki playback/controller | Not yet observed | In progress; no success claimed |

## Deliberate limits

- No benchmark establishes a speed improvement.
- No packet-capture study establishes complete telemetry removal.
- No comprehensive debloating or system-component removal is claimed.
- A Glasshouse log reported that the TV kernel lacked the support needed for its developer-inspector filtering function. No claim is made that every service was filtered or assessed.
- A successfully loaded test page was not counted as root access.
- A successfully launched Remote Play app was not counted as working playback.
- This project documents integration and learning on an owned device.

## Public evidence boundary

The public project includes selected source and synthetic checks. Private keys, SSH identity material, account identifiers, PS5 registration keys, raw exports, internal addresses, serial numbers and raw device logs are not included.
