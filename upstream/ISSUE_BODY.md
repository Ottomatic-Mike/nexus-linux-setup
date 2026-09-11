# Original Linux problems

These notes describe four separate problems found while getting Nexus working
on a Kubuntu PC with KDE Plasma and a HYTE Y70 Touch screen. The recovery helper
was later submitted in [PR #8](https://github.com/hello-nexus/nexus/pull/8).

## 1. The Y70 showed the wrong layout

During startup, the screen's browser window briefly had the size of another
monitor. Nexus used that size to choose a panel type and treated the Y70 as a
phone. The monitor's actual settings were already correct.

Opening `/panel/<saved-y70-record-id>` directly restored the saved Y70 layout.
Nexus should keep using the known screen ID instead of choosing again from a
temporary window size.

## 2. The editor preview stayed blank

The preview told the editor it was ready. The editor sent layout and theme
updates, but missed the complete starting message, called `simulator/init`.
Sending that message made the saved layout appear immediately.

The editor should send the starting state whenever a preview becomes ready,
including after it reloads. If the layout has not loaded yet, it should send
the starting state as soon as that data becomes available.

## 3. Motherboard fans were missing

Linux had not loaded the supported `nct6775` driver before Nexus checked for
fans. After the driver loaded, Linux exposed seven motherboard fan channels.
Restarting Nexus made them appear in the app.

Nexus should check again when a supported fan controller becomes available.
Finding a controller should not change its fan speeds or control modes.

## 4. The tray icon was missing after login

Nexus's background hardware service was running, but the Plasma desktop was not
ready when it first tried to connect. Restarting Nexus after login made the tray
icon appear. Waiting for Plasma during startup fixed this locally.

Inside Nexus, hardware controls should be able to start right away. Tray and
other desktop features should connect later when the desktop is ready, without
requiring a service restart.

See [reproduction steps](REPRODUCTION.md) for the observed behavior and
[maintainer notes](IMPLEMENTATION_NOTES.md) for the proposed implementation checks.
