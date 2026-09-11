# How the original problems were checked

These are troubleshooting notes for maintainers, not setup steps to run on a
working PC. Restarting Nexus interrupts its controls. Sleep, wake and login
steps below are ways to investigate timing problems, not claims that every
combination was tested.

## Test PC

| Part | Setup |
| --- | --- |
| Desktop | KDE Plasma 6, Wayland |
| Screen | HYTE Y70 Touch, 3840×1100, used in portrait |
| Nexus | 3.0.12 beta releases |
| Linux kernel | Ubuntu 7.0.0-31-generic |
| Motherboard | ASUS ROG STRIX X870E-E GAMING WIFI |
| Fan controller | NCT6799-compatible |

## Y70 shows the wrong layout

1. Use the Y70 as an extended display with its normal KDE settings.
2. Let Nexus open the general `/panel` page for the screen.
3. Watch the browser window during startup, before KDE finishes placing it.
4. Check which saved panel and panel type Nexus used.

Observed problem: Nexus could create or use a `phone` panel for the physical
Y70. Opening `/panel/<saved-y70-record-id>` directly showed the correct saved
layout. The direct route also stayed correct across the checked reboots.

Login, service restart, and sleep/wake are useful cases to examine when looking
for temporary window sizes.

## Editor preview stays blank

1. Open the Y70 editor and inspect its `/panel?simulator=1` iframe.
2. Watch the messages exchanged with that iframe.
3. Reload the preview or reproduce the state where it is blank.

The observed sequence was:

```text
Preview says: simulator/ready
Editor sends: simulator/set-theme
Editor sends: simulator/set-layout
Missing:      simulator/init
```

Making the preview visible was not enough. Sending one complete starting
message made the saved layout appear immediately.

## Motherboard fans are missing

Before loading the driver, list the hardware names and fan control files:

```bash
for h in /sys/class/hwmon/hwmon*; do
  cat "$h/name" 2>/dev/null
  ls "$h"/pwm[0-9] 2>/dev/null || true
done
```

On the tested board, motherboard fan controls were absent. Loading the supported
driver with the following command made them appear:

```bash
sudo modprobe nct6775
```

Linux reported an NCT6796D-S/NCT6799D-R-compatible chip. The `nct6799` controller
then had seven PWM channels, meaning seven exposed fan speed controls.

After restarting Nexus, its log reported:

```text
[Motherboard] Fans channels=7 id=linux-fans
```

The fans were then available in Nexus. The discovery check did not need to write
fan speeds.

## Tray icon is missing

1. Let Nexus's service start before the Plasma desktop exists.
2. Log into Plasma.
3. Check whether hardware controls work but the tray icon is missing.
4. Restart Nexus after the `plasmashell` process is running.

On the test PC, the restart made the tray icon appear. Waiting for Plasma before
Nexus started also fixed the local startup problem.
