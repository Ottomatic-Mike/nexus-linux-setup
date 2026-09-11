# ASUS Ryujin III display bridge for Nexus on Linux

This optional companion lets you edit a Ryujin III layout in Nexus and display
it on the physical cooler. It was developed against Nexus **3.0.12-beta.2** and
USB device **0b05:1aa2**, with a **320×240** LCD. It is separate from the existing
Y70 setup helper. Other Ryujin models, including the 640×480 Extreme, are not supported.

Nexus already discovers this cooler on Linux, but reports `bulk-pipe-unavailable`:
its native USB display transport cannot send the image. This companion renders a
real Nexus panel and sends its pixels through the cooler's bulk endpoint. A small
web adapter exposes that panel in Nexus's existing widget editor. Layouts, sensor
choices and themes are saved by Nexus itself.

## Install

Prerequisites: a working Nexus installation at `/opt/nexus`, the normal desktop
user's Nexus settings at `~/.config/Nexus/settings.json`, system Python 3 with
PyUSB and Pillow, Chrome/Chromium, systemd, and a logged-in desktop session.
The helper checks dependencies; it does not install packages or update Nexus.

From the repository, as your **normal desktop user**:

```bash
python3 ryujin/configure.py install
python3 ryujin/configure.py doctor
```

The installer requests administrator access for the isolated USB worker and web
adapter. It reuses a panel named `Ryujin III — local bridge`, or creates one if it
is absent. To reuse a renamed panel, specify its existing ID:

```bash
python3 ryujin/configure.py install --panel-id YOUR_EXISTING_PANEL_ID
```

Existing layouts are preserved. No machine-specific panel ID is shipped here.

Refresh the Nexus window, then select **Ryujin III — local bridge** in its sidebar.
Click a widget tile to add it; dragging a tile from the picker does not add it in
this Nexus version. Select existing widgets to edit their size, sensors and style;
use the editor's existing placement controls to arrange them. The small screen
fits four 2×2 monitoring widgets well.

Under **Devices → ASUS Ryujin LCD**, leave **Nexus Control** enabled. Switching it
off stops the companion output and sends the saved original LCD mode back to the
cooler. Switching it on resumes the Nexus layout. The original experimental
hardware warning remains visible because the native bulk transport is still
unavailable; use the separate local-bridge entry to edit the screen.

## Daily use and recovery

The USB worker starts with the system. The headless renderer starts with the user
session. You can close the editor and browser windows; rendering continues in a
separate Chrome profile. No browser tab in Codex is needed.

```bash
python3 ryujin/configure.py doctor
python3 ryujin/configure.py repair
```

Repair refreshes the companion files, reapplies the editor adapter, and restarts
only its two services. It does not restart Nexus or the Y70 service. Run repair
after a Nexus update replaces the web files. The adapter is tied to known frontend
patterns: a changed build may require adapting this code rather than just repair.
Unsupported connection/capture modules cause a clear failure instead of a guessed
patch. The installer checks the connection module before creating a panel.

Useful logs:

```bash
journalctl -u nexus-ryujin-usb.service -n 40
journalctl --user -u nexus-ryujin-renderer.service -n 40
```

If Nexus is not ready at login, a renderer that produces no captures for a minute
restarts and retries. USB reconnection is retried on subsequent frames. A known
Linux HID shutdown condition is handled by rebinding only this cooler's generic
HID interface; the whole USB device is never reset by this helper.

## Remove the integration

```bash
python3 ryujin/configure.py uninstall
```

This stops/disables the two companion services and removes their unit files and
the marked web adapter. It preserves the Nexus panel/layout, Chrome profile,
installed companion scripts, configuration and original-state backups so the
setup can be recovered. It does not uninstall Nexus.

## What changes on disk

- `/usr/local/lib/nexus-ryujin-bridge/`: companion scripts.
- `/etc/nexus-ryujin-bridge.json`: desktop user and panel ID, no Nexus token.
- `/var/lib/nexus-ryujin-bridge/`: original LCD mode and content-hash web backups.
- `/etc/systemd/system/nexus-ryujin-usb.service`: privileged display worker.
- `~/.config/systemd/user/nexus-ryujin-renderer.service`: unprivileged renderer.
- `~/.local/share/nexus-ryujin-bridge/chrome/`: separate browser profile.
- `/run/nexus-ryujin-bridge/pixels.sock`: owner-only pixel socket.
- `$XDG_RUNTIME_DIR/nexus-ryujin-bridge.key`: private local bridge capability.
- `/opt/nexus/wwwroot/index.html`: a removable marked script tag, preserving the
  existing Y70 patch. The script lives in `nexus-ryujin-bridge.js` beside it.

The renderer listens only on `127.0.0.1:9412`, requires its private cookie, checks
Host and Origin, and obtains the Nexus token in memory from existing settings.
It never writes that token into units, scripts or logs. The root worker accepts
only the configured user's socket connections and exactly 320×240 BGR frames.
Its command allowlist contains LCD state/mode/frame commands; no fan, pump,
lighting or firmware commands. This companion does not change fan policies,
desktop geometry or Y70 settings.

## Tested behavior and limits

On the development machine the prototype continuously delivered over 17,000
frames. The persistent background services were then checked for successful
frame delivery, stop/resume through Nexus Control, and recovery after restarting
both services. All saved panel layouts remained identical across installation;
Nexus kept its original process and the Y70 service remained active. The user
confirmed that all four physical CPU/GPU widgets continued displaying and
updating after the migration to background services.

Output is approximately **one frame per second**, suitable for sensor displays,
clocks and static content. It captures Nexus's HTML rendering; high-frame-rate
animation, video, WebGL and every third-party widget have not been validated.
This is a local compatibility bridge, not a native Nexus driver. Cold boot,
suspend/resume, uninstall/reinstall and first installation on another machine
have not yet been physically validated. Service restart checks are not a
substitute for those tests. The editor's online badge describes the streamed
panel; use `doctor` to check actual USB frame delivery.

Tests (no hardware writes):

```bash
python3 -m unittest discover -s ryujin/tests
node --test ryujin/tests/adapter.test.cjs
```

These cover fixed frame/command boundaries, loopback HTTP authorization and
origin checks, adapter scope, and idempotent patching that preserves the Y70 fix.

## Protocol reference

The BGR frame format and HID/bulk sequence were informed by
[zenstrukt/signalrgb-device-plugins](https://github.com/zenstrukt/signalrgb-device-plugins),
revision `f926459f51f75abd8d56236fb329c8e5df3c537c`, especially its Ryujin II protocol
notes and plugin. The 320×240 sequence was tested on the actual Ryujin III above;
it must not be generalized to other product IDs. See `THIRD-PARTY-NOTICES` for the
reference project's MIT notice. Nexus and its bundled renderer remain separately
licensed and are loaded from the existing installation, not redistributed here.
