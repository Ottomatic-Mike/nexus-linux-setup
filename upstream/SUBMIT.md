# Submission guide

Official public umbrella repository:

```text
https://github.com/hello-nexus/nexus
```

As of 2026-09-10 the public README says the component repositories linked as
submodules, including `nexus-service` and `nexus-web`, are private for now and
require `hello-nexus` organization access to clone/build.

That means the source fixes described here primarily belong in repositories
that are not yet publicly reviewable. This package therefore does not invent
private file paths or pretend to contain a source-level diff that could not have
been validated.

## Recommended submission now

Create an issue in `hello-nexus/nexus` using `PR_DESCRIPTION.md` as the body and
attach/link the sanitized reproduction. Suggested issue title:

```text
Linux: Y70 panel identity/simulator init, late hwmon fan discovery, and Plasma tray startup races
```

Ask the maintainers whether they want one internal cross-component change or
separate PRs when `nexus-service` and `nexus-web` become public.

## PR title when the target component source is available

```text
fix(linux): make Y70 kiosk, simulator, fan discovery and session adoption resilient
```

## Git workflow once source is accessible

```bash
git clone https://github.com/<your-user>/<target-repo>.git
cd <target-repo>
git remote add upstream https://github.com/hello-nexus/<target-repo>.git
git fetch upstream
git switch -c fix/linux-y70-session-fans upstream/main

# implement the contracts in IMPLEMENTATION_NOTES.md
# add the tests in PR_DESCRIPTION.md

git diff --check
# run the component repository's documented test commands

git add -A
git commit -m "fix(linux): make Y70 lifecycle resilient"
git push -u origin fix/linux-y70-session-fans
```

Then open a pull request from that branch to the maintainer repository.

Before submission, remove local identifiers such as usernames, hostnames, panel
record IDs, bearer tokens, serial numbers, absolute home paths and connector
names that are unique to one machine.
