# Suggested issue title

`Linux: Y70 panel identity/simulator init, late hwmon fan discovery, and Plasma tray startup races`

## Summary

This addresses four independent Linux lifecycle failures reproduced on a real
Kubuntu/Plasma + HYTE Y70 system:

1. A known hardware Y70 can be allocated/updated as another panel surface when
   generic `/panel` starts before its final Wayland/KWin geometry is settled.
2. The embedded `/panel?simulator=1` editor can receive incremental state
   without the complete `simulator/init` required to initialize the child.
3. Linux motherboard fans can be omitted for the lifetime of the process when a
   supported hwmon provider appears only after initial cooling enumeration.
4. The system service can start before a graphical session is adoptable, leaving
   tray/session features absent until the service is restarted.

Each failure was isolated independently and validated with a minimal local
workaround before this proposal was written.

## 1. Preserve hardware Y70 panel identity

### Reproduction

The physical Y70 is a 3840×1100 display rotated into portrait. Its final
KScreen geometry is correct.

The generic `/panel` bootstrap derives a surface from runtime browser viewport
size and registers/updates a panel record with that capability. During
startup/resume the kiosk can briefly have a main-monitor-shaped viewport before
KWin moves it to the Y70. In the reproduced case, early dimensions produced a
`phone` surface and the physical kiosk bound to the wrong panel record.

Launching the same kiosk directly at:

```text
/panel/<known-y70-panel-record-id>
```

immediately restored the correct physical layout and stayed correct across
reboots.

### Proposed fix

When the hardware Y70 already has a stable `panelRecordId`, launch the direct
record route. Use generic `/panel` allocation only for a genuinely unbound
panel. Do not allow transient browser geometry to rewrite the surface identity
of an already-associated physical panel.

Keep `localhost` as the canonical local kiosk host; changing the hostname also
changes the Chrome app/window class on Linux.

## 2. Make the simulator handshake complete and restartable

### Reproduction

The editor iframe is:

```text
/panel?simulator=1
```

The child starts with an empty `simulator-empty` layout and a separate
`ready=false` flag. Only `simulator/init` transitions it into its initialized
state. Incremental messages such as `simulator/set-theme`,
`simulator/set-layout`, and `simulator/set-display` do not.

In the failure trace:

```text
child -> parent: simulator/ready
parent -> child: simulator/set-theme
parent -> child: simulator/set-layout
(no simulator/init observed)
```

Forcing `showPanel=true` removed the hidden-panel placeholder but left an empty
canvas. Sending one complete `simulator/init` immediately rendered the exact
stored Y70 layout.

### Proposed fix

On every fresh `simulator/ready`, send exactly one complete current-state
`simulator/init`. If parent data is not loaded yet, remember that the peer is
ready and initialize it once state is available. Queue or suppress incremental
messages until that initial state has been sent. Reset the initialized state
when the iframe document reloads.

Also separate `showPanel` from `settings.panel.autoLaunch`: auto-launch is a
policy setting, not proof that a currently running/directly bound panel is
hidden.

## 3. Re-enumerate Linux fan providers

### Reproduction

Before loading the available `nct6775` module, the system exposed no writable
motherboard PWM channels and Nexus controlled only the NVIDIA GPU fan.

After:

```bash
sudo modprobe nct6775
```

Linux reported an NCT6799-compatible controller and exposed seven `pwmN`
channels. Restarting only Nexus then logged:

```text
[Motherboard] Fans channels=7 id=linux-fans
```

The motherboard fans immediately became controllable.

### Proposed fix

Initial fan enumeration should not be final for the lifetime of the service.
On Linux, recover when supported hwmon PWM providers appear after startup.
Possible implementation choices include observing/retrying hwmon discovery or
performing safe supported module probes before first enumeration and still
re-enumerating after later device appearance.

Discovery must not write fan duty values.

## 4. Retry graphical-session/tray adoption

### Reproduction

At boot, `nexus.service` was active and hardware control worked, but the tray
icon was absent. Restarting the service after `plasmashell` existed made the
tray appear immediately. A local `ExecStartPre` wait for the target user's
Plasma process made the tray reliable across reboot.

### Proposed fix

Do not make the hardware daemon wait for Plasma upstream. Start hardware
monitoring/control normally, but make graphical-session adoption a retryable
attachment. When an eligible user session appears, attach/register tray and
other session-bound integrations. Detach/re-adopt if the session changes.

## Tests requested

### nexus-web

- child emits `simulator/ready` before parent data has loaded; a complete init
  is eventually delivered exactly once;
- iframe reload emits a new `ready`; the new child is initialized;
- incremental layout/theme updates before init cannot leave the simulator
  permanently blank;
- `autoLaunch=false` does not imply `showPanel=false` when runtime panel state
  says a panel is active/visible.

### nexus-service

- hardware Y70 with an existing `panelRecordId` launches
  `/panel/<record-id>`, not generic `/panel`;
- transient initial browser dimensions cannot rewrite that hardware record to
  `phone`;
- Linux fan enumeration recovers when an hwmon PWM provider appears after
  service startup;
- service can start before a graphical session and later registers tray/session
  integration without a service restart.

## Scope

No KDE monitor-mode, scaling or rotation changes are required. The Y70 problem
is panel identity/lifecycle, not KScreen configuration.

No raw PWM workaround is required. The kernel already exposes the board fan
controller correctly once the appropriate hwmon provider is present.
