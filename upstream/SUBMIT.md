# Work sent to the Nexus maintainers

The Y70, motherboard fan and Plasma tray fixes have been submitted as
[Nexus PR #8](https://github.com/hello-nexus/nexus/pull/8):
**fix(linux): add tested recovery helper for Y70, fans and Plasma startup**.

The PR adds an optional Linux recovery helper to the public Nexus repo.
It does not change the normal installer to run the helper automatically.
The later Ryujin III work in this repo is separate and is not included in that PR.

## What the files in this folder are for

- [PR description](PR_DESCRIPTION.md): a short explanation of the submitted work.
- [Issue notes](ISSUE_BODY.md): the four original problems, in plain English.
- [Reproduction steps](REPRODUCTION.md): how the problems were observed.
- [Maintainer notes](IMPLEMENTATION_NOTES.md): proposed fixes inside Nexus itself.

These local notes do not change the text already posted on GitHub.

## Why the PR adds a helper

When the contribution was prepared, the contributor account could not access
Nexus's `nexus-service` and `nexus-web` source repositories. We could adapt and
test the working helper, but could not edit or test those private components.

The submitted helper also includes improvements over the original local script:
for example, its Plasma startup wait is optional and has a time limit. Do not
assume the two copies have identical options or behavior.

## If the maintainers make the component source available

Use each component's own contribution and testing instructions. The maintainer
notes describe the behavior to aim for without guessing private filenames.
Keep unrelated changes out of the contribution and report which checks ran.

Before sharing logs or examples, remove login tokens, usernames, hostnames,
serial numbers and screen IDs specific to your machine.
