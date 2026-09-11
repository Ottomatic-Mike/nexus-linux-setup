# Suggested fixes inside Nexus

These notes are for Nexus maintainers. They describe the behavior needed to fix
the original problems inside Nexus, rather than relying on this local helper.
The private component source was unavailable when these notes were prepared,
so they do not name files we could not inspect.

## Keep the Y70's saved panel ID

If the hardware already has a `panelRecordId`, open:

```text
http://localhost:9400/panel/<url-encoded-panelRecordId>
```

Use the general `/panel` route only when a new panel needs to be chosen or
created. A temporary browser size during startup must not change an existing
Y70 panel into a `phone` panel.

Check that a known Y70 keeps its saved layout even when the browser starts with
the dimensions of another monitor.

## Check for fans again when hardware appears

At startup, find the fan controls currently exposed by Linux's `hwmon` system.
Keep watching or retrying so a supported controller that appears later can be
added. Handle a controller going away too.

Do not write fan speeds, curves or control modes merely to find hardware.
In particular, discovery should leave `pwmN` and `pwmN_enable` unchanged.

Check that a controller appearing after Nexus starts becomes available without
restarting Nexus.

## Connect desktop features when the desktop is ready

Start hardware monitoring and control without waiting for a desktop login.
If no suitable desktop session exists, keep the tray and media integration
pending. Connect those features when a session appears, and reconnect if the
session changes.

Check that starting Nexus before Plasma does not permanently lose the tray icon.

## Always give a new preview its starting state

The editor preview is a webpage inside an iframe. Treat each new or reloaded
iframe as a fresh preview.

1. When it loads, clear the flags that track whether it is ready and initialized.
2. When it sends `simulator/ready`, remember that it is ready.
3. Once the complete current state is available, send one `simulator/init`.
4. Only then send smaller layout, theme and selection updates. Queue any earlier
   updates or include them in the starting state.
5. Repeat this process when the iframe reloads.

The starting state observed in the local fix includes these fields:

```text
surface, deviceTouch, dpi, displayBound, layout, theme, themeMode,
selectedWidgetId, brightness, screenOn, showPanel, deviceId
```

Check the case where the preview is ready before its data has loaded, the case
where updates arrive early, and the case where the iframe reloads. Each new
preview should receive a complete starting state exactly once.

## Do not confuse auto-launch with visibility

`panel.autoLaunch` says whether Nexus should launch a panel automatically.
`showPanel` says whether the panel should be shown. A panel launched separately
can still be visible when auto-launch is off.

Use the actual running panel and display state where available. Check that a
working, separately launched screen does not get a hidden preview just because
`panel.autoLaunch` is false.
