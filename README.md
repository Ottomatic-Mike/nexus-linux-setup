# Get Nexus working on Linux

This repo contains the fixes I used to get Nexus working on my Linux PC.
It covers the HYTE Y70 screen, missing motherboard fans, a missing tray icon,
and the ASUS Ryujin III cooler screen.

It is an unofficial helper for [Nexus](https://github.com/hello-nexus/nexus).
Nexus still controls your widgets, lighting and fan settings.

## Pick the help you need

| What you need | Where to start |
| --- | --- |
| Set up Nexus and the Y70 screen | Follow the steps below |
| Fix an existing Y70 setup | Run the repair command below |
| Put Nexus widgets on a Ryujin III cooler | [Ryujin guide](ryujin/README.md) |
| Find out why something stopped working | [Troubleshooting](docs/TROUBLESHOOTING.md) |
| Understand the fixes | [How it works](docs/TECHNICAL-NOTES.md) |
| Review the work sent to Nexus maintainers | [Submission notes](upstream/SUBMIT.md) |

The Y70 helper and Ryujin helper are separate. Installing one does not install
the other. If your setup already works, you do not need to run repair.

## Set up Nexus and the Y70

Open a terminal in this repo's folder while logged into your normal desktop
account. The helper will ask for your administrator password when needed.

```bash
chmod +x nexus-linux-setup.sh
./nexus-linux-setup.sh install
```

If Nexus is missing, this downloads and runs its official Linux installer.
If Nexus is already installed, it configures the fixes around that installation.
Setup and repair can restart Nexus, so its controls may briefly be unavailable.

Then check the result:

```bash
./nexus-linux-setup.sh doctor
```

`doctor` checks the setup and reports problems. It does not apply repairs.

### Nexus is installed, but something is broken

```bash
./nexus-linux-setup.sh repair
./nexus-linux-setup.sh doctor
```

If a problem remains, use the [troubleshooting guide](docs/TROUBLESHOOTING.md).

## What the Y70 helper fixes

- **Wrong layout on the Y70:** opens the screen's saved layout directly so a
  temporary window size during startup does not make Nexus treat it as a phone.
- **Blank editor preview:** supplies the starting layout and theme when Nexus
  misses the message needed to display them.
- **Missing motherboard fans:** checks whether the `nct6775` Linux driver makes
  a supported fan controller available, then arranges for it to load before Nexus.
- **Missing tray icon on KDE Plasma:** makes Nexus wait for the desktop during
  startup so it can connect to the session.
- **Screen window in the wrong place:** places the Nexus window on the existing
  Y70 display, using your current monitor settings.

It also keeps backups of the web and settings files it changes, and provides
repair, status and removal commands.

## What stays under your control

The helper does not change monitor resolution, scale, rotation or arrangement.
It does not set fan speeds while checking for a fan controller. Fan curves and
lighting settings remain Nexus's job.

It does not save the Nexus login token in its scripts, service files or logs.
Normal removal keeps your Nexus data and the separate browser profile used for
the Y70 screen.

## Where this was tested

The original fixes were checked on this setup:

| Part | Tested setup |
| --- | --- |
| Desktop | Kubuntu, KDE Plasma 6, Wayland |
| Screen | HYTE Y70 Touch, 3840×1100, used in portrait |
| Nexus | 3.0.12 beta releases |
| Linux kernel | Ubuntu 7.0.0-31-generic |
| Motherboard | ASUS ROG STRIX X870E-E GAMING WIFI |
| Fan controller | NCT6799-compatible, using `nct6775` |

The helper checks the hardware it finds rather than assuming every PC matches
this one. This is not a claim that every Linux system has been tested.
See the [Ryujin guide](ryujin/README.md) for its separate test results and limits.

## Update Nexus

To run the official updater and apply the Y70 fixes again:

```bash
./nexus-linux-setup.sh install --update
```

The Y70 preview fix is also applied when the Nexus service next starts.
If you use the Ryujin helper, follow its separate repair steps after an update.

To install a particular release:

```bash
./nexus-linux-setup.sh install --version v3.0.12-beta.2
```

To use an official release archive you already downloaded, replace the example
filename with its actual path:

```bash
./nexus-linux-setup.sh install --archive ~/Downloads/nexus-linux-x64.tar.gz
```

## See what is configured

```bash
./nexus-linux-setup.sh status
```

## Remove the Y70 helper's changes

```bash
./nexus-linux-setup.sh uninstall
```

This removes the helper's startup, window placement and preview fixes. It turns
Nexus's own panel auto-launch back on and restarts Nexus. It keeps Nexus installed
and preserves your Nexus data. It does not remove the separate Ryujin helper.

To also run Nexus's own uninstaller, if one is available:

```bash
./nexus-linux-setup.sh uninstall --purge-nexus
```

## For contributors

See [Contributing](CONTRIBUTING.md) for checks to run before sending changes.
The [technical notes](docs/TECHNICAL-NOTES.md) explain the files and settings the
helper manages.

The original Y70, fan and tray work has been submitted as
[Nexus PR #8](https://github.com/hello-nexus/nexus/pull/8). The later Ryujin work
is included in this repo; it is not part of that PR.

## License

This helper uses the [MIT license](LICENSE). Nexus has its own license.
This is not an official Nexus release.
