# Linux recovery helper for the Y70, fans and tray icon

This is a plain-English summary of the work submitted in
[Nexus PR #8](https://github.com/hello-nexus/nexus/pull/8). The GitHub PR contains
the full submitted description and its validation details.

## The problem

Getting Nexus working on the test Linux PC required four fixes: the Y70 could
show the wrong layout, its editor preview could stay blank, motherboard fans
were missing, and the tray icon could be absent after login.

## What the PR adds

An optional helper that:

- Opens the saved Y70 panel directly and places its window on the existing screen.
- Supplies the preview's missing starting message when needed.
- Loads the supported motherboard fan driver when it exposes usable controls.
- Offers an optional, time-limited wait for Plasma at startup.
- Provides setup, repair, checks, backups and removal commands.

It does not run automatically from the normal installer. It leaves monitor
settings alone and does not set fan speeds while finding controllers.

## What was tested

The original recovery steps worked on the physical test PC. The version adapted
for the PR was checked with tests that use temporary files and sample data;
it was not installed over the working setup.

Those checks covered the shell script, download handling, display selection,
ambiguous panel IDs, the optional Plasma wait, and applying/removing the preview
fix. Six JavaScript tests covered preview message order and limiting the fix to
the intended page and Y70 layout.

Fresh installation, login and wake, authentication, updates and removal still
need hardware testing of the submitted version. The PR also documents that
browser sign-in uses a timed launch and removal turns panel auto-launch on
rather than restoring its previous value.

## Work still needed inside Nexus

The contributor could not access the private service and web source repositories.
This PR therefore adds the usable recovery helper and records the proposed
longer-term fixes in the [maintainer notes](IMPLEMENTATION_NOTES.md).

The later Ryujin III display helper is not part of this PR.
