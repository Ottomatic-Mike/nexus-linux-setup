# Help improve this repo

Please explain what was broken, what you changed, and how you checked the fix.
Write instructions that someone using Linux for the first time can follow.
Explain technical terms when they are needed.

Keep changes focused. Do not include your username, screen ID, USB serial
number, login token or other details that only work on your PC.

The helpers must keep these promises:

- Leave monitor resolution, scale, rotation and arrangement alone.
- Do not change fan speeds or fan control settings while looking for hardware.
- Keep existing Nexus layouts and unrelated settings.
- Keep the Y70 and Ryujin helpers separate so either can be used on its own.

## Check your changes

For the main helper:

```bash
./tests/static.sh
```

For the Ryujin helper, with Python, PyUSB, Pillow and Node.js installed:

```bash
python3 -m unittest discover -s ryujin/tests
node --test ryujin/tests/adapter.test.cjs
```

Before committing:

```bash
git diff --check
```

These checks do not prove that a physical screen works. Say which hardware tests
you ran and which you did not. Do not run setup or restart someone's working
system just to check a documentation change.

Changes to Nexus itself belong in the official Nexus project. This repo contains
local fixes that work alongside an installed copy of Nexus.
