# When something is not working

Run these commands from this repo's folder, using your normal desktop account.
The Y70 helper asks for administrator access when it needs it. Run the Ryujin
commands without putting `sudo` in front of them.

## Start here

For Nexus or the Y70 screen:

```bash
./nexus-linux-setup.sh doctor
```

For the Ryujin cooler screen:

```bash
python3 ryujin/configure.py doctor
```

Read the results before running repair. Repair for the main helper can restart
Nexus. Ryujin repair restarts only the two Ryujin background programs.

## The Y70 screen is blank or shows the wrong layout

Try:

```bash
./nexus-linux-setup.sh repair
./nexus-linux-setup.sh doctor
```

To see whether its background program is running and read its recent messages:

```bash
systemctl --user status nexus-y70-direct.service
journalctl --user -u nexus-y70-direct.service -b --no-pager
```

The screen launcher waits for Nexus at `http://localhost:9400` before opening
Chrome. If Nexus is not running, the screen will wait too.

## The helper cannot find the Y70

Show the displays KDE knows about:

```bash
kscreen-doctor -o
```

The helper first looks for the Y70's usual `3840x1100` screen mode. Otherwise, it
looks for a very tall display. If more than one display is an equally good match,
it stops rather than choosing one for you.

The helper does not change your display settings to make a match.

## The editor is blank or says “Panel hidden”

Run repair, then refresh the Nexus window:

```bash
./nexus-linux-setup.sh repair
```

This restores the small preview fix in Nexus's web files. A Nexus update may
have replaced those files.

## Motherboard fans are missing

First run the main helper's health check. To see whether the expected Linux
driver is loaded:

```bash
lsmod | grep nct6775
```

To read what Nexus found when checking fans:

```bash
journalctl -u nexus -b --no-pager | grep -Ei 'cool|fan|pwm|nct'
```

On the tested motherboard, loading the supported driver made seven fan controls
available. Other boards may use different hardware. The helper keeps the driver
in the startup settings only if it actually finds supported fan controls.

For a closer look at the controllers Linux exposes, these commands only read
names and list available control files:

```bash
for h in /sys/class/hwmon/hwmon*; do
  printf '%s: ' "$h"
  cat "$h/name" 2>/dev/null || true
  ls "$h"/pwm[0-9] 2>/dev/null || true
done
```

## The Nexus tray icon is missing on KDE Plasma

Check that the desktop and Nexus are running:

```bash
pgrep -a plasmashell
systemctl status nexus
```

If Nexus started before the desktop, apply the startup fix:

```bash
./nexus-linux-setup.sh repair
```

The fix lives in `/etc/systemd/system/nexus.service.d/10-wait-for-plasma.conf`.

## The Ryujin screen stopped updating

```bash
python3 ryujin/configure.py doctor
```

If the result says control is off, turn on **Devices → ASUS Ryujin LCD → Nexus
Control** in Nexus. If control is on but no recent frames are reported, try:

```bash
python3 ryujin/configure.py repair
python3 ryujin/configure.py doctor
```

See the [Ryujin guide](../ryujin/README.md) for adding widgets, reading logs and
checking whether your cooler model is supported.

## A Nexus update removed a fix

For the Y70:

```bash
./nexus-linux-setup.sh repair
```

For the Ryujin:

```bash
python3 ryujin/configure.py repair
```

Refresh Nexus afterwards. If the Ryujin logs say the Nexus version is unsupported,
the bridge code may need an update. Repeating repair will not fix a changed file
format by itself.

## Nexus will not stop

The main helper already tries a normal stop, then forcibly stops only Nexus if
it takes too long. If you need to do that manually, the following commands will
interrupt Nexus and its controls:

```bash
sudo systemctl stop nexus &
sleep 5
sudo systemctl kill --kill-whom=all --signal=SIGKILL nexus 2>/dev/null || true
wait
```

## Remove a helper

To remove the Y70 helper's changes while keeping Nexus and your data:

```bash
./nexus-linux-setup.sh uninstall
```

This also turns Nexus's own panel auto-launch back on and restarts Nexus.

To remove the Ryujin background programs and editor fix:

```bash
python3 ryujin/configure.py uninstall
```

The Ryujin command keeps the saved panel layout and recovery files. See its
[removal details](../ryujin/README.md#remove-the-ryujin-helper).
