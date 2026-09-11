# How the fixes work

This page explains the details behind the [main setup guide](../README.md).
For the cooler screen, see the separate [Ryujin guide](../ryujin/README.md).

## Keep the Y70 linked to its saved layout

Nexus gives each saved panel an ID. Opening `/panel/<record-id>` asks for that
specific panel. Opening the general `/panel` page lets Nexus choose or create
one based on the browser window's size.

During startup, the window can briefly be the wrong size before KDE moves it to
the Y70. Nexus can mistake it for a phone screen. The helper avoids this by
opening the saved Y70 panel directly.

The launcher consistently uses `localhost`. Chrome uses the address as part of
the window's identity. Changing it to `127.0.0.1` can break the rule that places
the window on the Y70.

## Put the window on the right display

KScreen manages monitor resolution, scale, rotation and desktop arrangement.
KWin manages windows. The helper leaves KScreen settings alone and gives KWin a
rule for placing only the Nexus screen window on the existing Y70 display.

The KWin 6 script reads `workspace.screens`, matches the direct Nexus window,
uses the display's geometry for `frameGeometry`, and makes that window fullscreen
without borders or a task-switcher entry.

## Let the screen sign in to local Nexus

For a new Chrome profile, the helper may need Nexus's local login token once.
It reads it from Nexus's already-running screen launcher, opens the saved panel
with it, then lets the separate browser profile keep the login.

The token is not written into the helper's saved settings, launcher, service file
or log output.

## Make missing motherboard fans appear

The tested board has an NCT6799-compatible controller. Loading Linux's
`nct6775` driver made seven fan control files available. These are named `pwmN`,
where `N` is the fan channel number. Nexus found them after restarting.

The helper checks for these files and arranges for the driver to load before
Nexus when the hardware is supported. It does not write to `pwmN` or
`pwmN_enable`. Nexus remains responsible for fan speeds and control modes.

## Give the editor preview its starting state

The preview is a small webpage inside the editor, at `/panel?simulator=1`.
It starts empty and announces that it is ready. The editor should reply with a
complete starting layout and theme, using a message named `simulator/init`.

In the failure we observed, the editor sent smaller updates but missed that
starting message. The preview stayed blank even though the layout was saved.

The local fix waits briefly for the normal starting message. If it does not
arrive, but the real layout and theme are available, the fix supplies it.
The related `showPanel` value controls whether the preview is visible. Turning
off automatic screen launch does not mean a separately launched screen is hidden.

For developers, the observed message names were:

```text
simulator/ready
simulator/init
simulator/set-layout
simulator/set-grid
simulator/set-touch
simulator/set-display-bound
simulator/set-theme
simulator/set-selection
simulator/flash-widget
simulator/set-display
```

## Wait for the Plasma desktop

Nexus could start its hardware controls before Plasma was ready, then miss the
tray icon. The local fix waits for the target user's Plasma process at startup.

A longer-term fix inside Nexus would let hardware controls start immediately,
then connect the tray and media controls when a desktop session becomes ready.
It should reconnect if that session changes. See the
[maintainer notes](../upstream/IMPLEMENTATION_NOTES.md).

## Files the main helper may install

Which files are used depends on the hardware and desktop it finds:

```text
/etc/nexus-linux-setup/
/etc/modules-load.d/nexus-fans.conf
/etc/systemd/system/nexus.service.d/10-wait-for-plasma.conf
/etc/systemd/system/nexus.service.d/15-y70-simulator.conf
/etc/systemd/system/nexus.service.d/20-nct6775.conf
/usr/local/libexec/nexus-linux-setup
/usr/local/share/nexus-linux-setup/simulator-fix.js
~/.config/systemd/user/nexus-y70-direct.service
~/.local/bin/nexus-y70-direct
~/.local/share/kwin/scripts/nexus-y70-placement/
```

Copies of web and settings files are saved before changes in
`/etc/nexus-linux-setup/backups/`. Each backup name includes a hash of its contents
so different versions can be kept apart.

The preview fix has start and end markers in `index.html`, so repair can replace
it and uninstall can remove it. A Nexus startup step applies it again if an
update replaced the file.
