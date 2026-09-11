# Contributing

Please keep this helper conservative and capability-driven. A change should not
hard-code a panel record ID, Linux username, UID, KScreen connector or local
filesystem path from one reproduction machine.

Before committing:

```bash
./tests/static.sh
```

Changes that touch display behavior must preserve the rule that the helper does
not rewrite KScreen mode, scale, rotation or desktop arrangement. Changes that
touch cooling discovery must not write PWM duty/control values as part of
detection.

Upstream Nexus source fixes should go to the appropriate official component
repository once it is publicly accessible; this helper is a local integration
workaround, not a fork of Nexus.
