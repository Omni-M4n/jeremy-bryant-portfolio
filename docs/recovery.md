# Recovery design

This documents the approach taken in the completed lab, not a universal rooting guide. Firmware and device compatibility can differ.

## Keep a familiar interface available

Glasshouse's LG Home tile provides the stock interface. The documented Home-button hold and the permanent `Use LG Home` setting were additional recovery paths in this setup. Switching back and re-enabling the custom interface was tested.

## Preserve the preceding configuration

The previous startup configuration was retained before integrating Glasshouse. Recovery copies and SSH identity material remain private. Changes to startup were tested after a restart, and the resulting interface was checked through normal use.

## Remove installation-only infrastructure

The temporary installer listener, narrowly scoped firewall exception and temporary PC network address were removed or restored after installation. Wired TV addressing was returned to DHCP and manual DNS cleared. Normal Wi-Fi use resumed.

## Keep the extension separate

Chiaki was an additional experiment after the core Homebrew/Glasshouse setup. Its configuration does not automatically suspend the PS5 on exit. Playback and controller verification remain outstanding. A failure in that experiment does not change the completion status of the earlier, separately tested core lab.

No device credentials or executable rooting payloads are distributed with this portfolio.
