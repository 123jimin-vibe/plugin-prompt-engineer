+++
id = "d0002"
title = "Keep PreToolUse hook skill-scoped, not plugin-level"
status = "accepted"
relates_to = ["s0002", "s0003"]
supersedes = []
+++

## Context

The `allow-skill-scripts.py` hook auto-allows Bash calls that invoke skill scripts with the venv Python. It was placed in `token-counter/SKILL.md` frontmatter (skill-scoped) per t0005 to avoid firing on every Bash call. However, skill-scoped hooks don't receive `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` env vars — those are only available in plugin-level hooks (`hooks.json`).

## Options Considered

1. **Move hook to `hooks.json`** — env vars would be available, but the hook fires on every Bash call matching the pattern across all skills, not just when the token-counter skill is active. Contradicts t0005's goal of minimizing invocations.
2. **Keep skill-scoped, eliminate dependency on plugin env vars** — the hook only fires when the skill is active and the matcher matches. Requires a different validation strategy that doesn't need the plugin paths.

## Decision

Option 2. The hook stays in skill frontmatter. The validation must be reworked to not depend on `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PLUGIN_DATA`.

## Consequences

- The hook only runs when the token-counter skill is active, minimizing total invocations.
- Validation logic must derive or avoid plugin paths entirely.
- May need to replace the Python script with a lighter mechanism to also address execution time.
