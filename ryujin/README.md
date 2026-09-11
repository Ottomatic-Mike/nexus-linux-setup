# Put Nexus widgets on the Ryujin III screen

This helper lets you choose and edit widgets in Nexus, then shows them on the
ASUS Ryujin III cooler screen. Once set up, it runs in the background. You can
close the editor and browser windows.

It works alongside your existing Nexus installation. It does not change your
Y70 setup, monitor settings, fan speeds, pump settings or lighting settings.

## Check your cooler first

This was tested with:

- **ASUS Ryujin III**, USB ID **0b05:1aa2**.
- **320×240** screen.
- **Nexus 3.0.12-beta.2** on Linux.

Other Ryujin models are not supported by this helper. That includes the
640×480 Extreme model.

The screen updates about **once per second**. This works well for temperatures,
usage numbers, clocks and still images. Fast animation, video and every widget
have not been tested.

## Why this helper is needed

Nexus can find the cooler on Linux, but its built-in screen connection reports
`bulk-pipe-unavailable`. That means it cannot send the image to the screen.

This helper draws a real Nexus panel in a hidden browser and sends that image
to the cooler over USB. A small change to the Nexus webpage makes the panel
available in the normal widget editor. Nexus saves your layout and settings.

## What you need

Before installing, make sure you have:

- Nexus installed and working at `/opt/nexus`.
- Your Nexus settings at `~/.config/Nexus/settings.json`.
- Python 3 with the **PyUSB** and **Pillow** libraries.
- Chrome or Chromium.
- A Linux system using **systemd**, which starts the background programs.
- A logged-in desktop session.

The installer checks for these programs. It does not install missing packages
or update Nexus.

## Install

Open a terminal in this repo's folder as your **normal desktop user**. Do not
put `sudo` in front of this command; it asks for administrator access when needed.

```bash
python3 ryujin/configure.py install
python3 ryujin/configure.py doctor
```

The helper creates a panel called **Ryujin III — local bridge**, or uses the
existing panel with that name. It leaves existing layouts alone.

If you renamed a panel you want to keep using, give its ID explicitly. Replace
the example below with that panel's ID from the Nexus page address:

```bash
python3 ryujin/configure.py install --panel-id YOUR_EXISTING_PANEL_ID
```

## Add and edit widgets

1. Refresh the Nexus window.
2. Select **Ryujin III — local bridge** in the sidebar.
3. **Click a widget tile to add it.** Dragging a tile from the list onto the
   preview does not add it in this Nexus version.
4. Select a widget already in the preview to change its size, sensor or style.
   Use the editor's placement controls to arrange it.
5. Under **Devices → ASUS Ryujin LCD**, turn on **Nexus Control**.

Four small, 2×2 monitoring widgets fit the screen well. The tested layout shows
CPU usage, GPU usage, CPU temperature and GPU temperature.

The original ASUS device may still show an experimental warning. That warning
refers to the built-in connection, which is still unavailable. Use the separate
**Ryujin III — local bridge** entry to edit your widgets.

## Turn the Nexus display on or off

Use **Devices → ASUS Ryujin LCD → Nexus Control**.

Turning it off stops the helper from sending images and asks the cooler to
return to its saved original screen mode. Turning it on resumes your Nexus
layout.

## Everyday use

The USB program starts with the PC. The hidden browser starts when your user
session starts. You do not need to leave Nexus's editor or a Codex tab open.

To check the connection:

```bash
python3 ryujin/configure.py doctor
```

This shows whether the background programs are running, how many images they
have sent, and how old the last image is. When control is on, a recent image
with no error is the expected result. The editor's “online” label alone does
not prove that images are reaching the physical cooler.

## If the screen stops updating

First check that **Nexus Control** is on. Then try:

```bash
python3 ryujin/configure.py repair
python3 ryujin/configure.py doctor
```

Repair copies the helper files again, restores the editor change and restarts
only the two Ryujin background programs. It does not restart Nexus or the Y70.

If Nexus is still starting when you log in, the hidden browser retries after a
minute without images. The USB program also retries failed connections. For a
known Linux USB problem, it reconnects only this cooler's HID interface—the
connection used to send display commands. It does not reset the whole cooler.

To read recent error messages:

```bash
journalctl -u nexus-ryujin-usb.service -n 40
journalctl --user -u nexus-ryujin-renderer.service -n 40
```

### After a Nexus update

Run the Ryujin repair command and refresh Nexus. An update may replace the web
file that provides the editor change.

This helper expects parts of the tested Nexus web version. If the logs report
an unsupported connection or capture module, the helper code needs to be
updated for that Nexus version. Running repair repeatedly will not solve that.

## Remove the Ryujin helper

```bash
python3 ryujin/configure.py uninstall
```

This stops and removes the two startup services and the editor change. It keeps
Nexus installed, your panel layout, the separate browser profile, the helper
scripts, configuration and backups. Those files are kept so you can recover or
reinstall the setup later.

## What was checked

The early version sent more than 17,000 images continuously on the test PC.
After moving it to background services, we checked that:

- Images still reached the cooler with the temporary browser tab closed.
- Nexus Control stopped and resumed the images.
- Restarting both helper services restored the connection.
- All saved panel layouts stayed the same.
- Nexus kept running without a restart, and the Y70 service stayed active.

The user confirmed that all four CPU/GPU widgets were visible and updating on
the physical screen after the change.

A full power-on test, sleep and wake, removal and reinstallation, and installation
on another PC have not yet been checked on physical hardware. Restarting the
services is useful evidence, but does not prove those other cases work.

## Details for people maintaining the helper

### Files it uses

| Location | Purpose |
| --- | --- |
| `/usr/local/lib/nexus-ryujin-bridge/` | Installed helper scripts |
| `/etc/nexus-ryujin-bridge.json` | Desktop user and panel ID; no Nexus login token |
| `/var/lib/nexus-ryujin-bridge/` | Original screen mode and copies of changed web files |
| `/etc/systemd/system/nexus-ryujin-usb.service` | Starts the USB program with administrator access |
| `~/.config/systemd/user/nexus-ryujin-renderer.service` | Starts the hidden browser as your user |
| `~/.local/share/nexus-ryujin-bridge/chrome/` | Separate browser profile |
| `/run/nexus-ryujin-bridge/pixels.sock` | Local connection for sending images to the USB program |
| `$XDG_RUNTIME_DIR/nexus-ryujin-bridge.key` | Private key for the local helper connection |
| `/opt/nexus/wwwroot/nexus-ryujin-bridge.js` | Makes the panel appear in the editor |

The helper also adds a marked script tag to `/opt/nexus/wwwroot/index.html`.
It preserves the existing Y70 fix. Backups are named using a hash of their
contents so different versions can be kept apart.

### Access and USB commands

The browser helper accepts connections only from this PC, at `127.0.0.1:9412`.
Requests need its private cookie and must pass checks on the requested host and
page origin. It reads the existing Nexus login token into memory when needed;
it does not save that token in scripts, service files or logs.

The USB program accepts images only from the configured desktop user. Images
must be exactly 320×240 pixels, with three colour bytes per pixel in BGR order.
The only allowed commands read screen state, set screen mode or send a frame.
Fan, pump, lighting and firmware commands are not included.

### Automated checks

With Python, PyUSB, Pillow and Node.js installed, run from the repo's folder:

```bash
python3 -m unittest discover -s ryujin/tests
node --test ryujin/tests/adapter.test.cjs
```

These tests do not write to hardware. They check image size and command limits,
access checks, changes limited to the intended panel, and applying/removing the
web change without damaging the Y70 fix.

### Reference and license

The image format and USB command sequence were informed by the Ryujin II notes
and plugin in [zenstrukt/signalrgb-device-plugins](https://github.com/zenstrukt/signalrgb-device-plugins),
revision `f926459f51f75abd8d56236fb329c8e5df3c537c`. That sequence was tested on
the Ryujin III listed above. It should not be assumed to work on other models.

The reference project's MIT notice is in [THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES).
Nexus has its own license. This repo uses the installed Nexus files; it does not
include copies of them.
