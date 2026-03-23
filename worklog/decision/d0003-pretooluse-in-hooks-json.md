+++
id = "d0003"
title = "Move PreToolUse hooks to hooks.json"
status = "accepted"
relates_to = ["s0002", "s0003"]
supersedes = ["d0002"]
+++

## Context

d0002 chose to keep PreToolUse hooks in skill SKILL.md frontmatter to minimize invocations. Investigation for t0008 revealed that skill-scoped hooks in plugins are not registered at all — this is a confirmed upstream bug (anthropics/claude-code#17688). The debug log showed "Registered 1 hooks from 5 plugins" (only the SessionStart from hooks.json); skill frontmatter hooks were silently ignored.

## Options Considered

1. **Move hooks to `hooks.json`** — guaranteed to work. Hooks fire on any Bash call matching the matcher pattern, not only when the skill is active. The matchers are specific enough (`Bash(*invoke-llm/scripts/invoke.py*)`, `Bash(*token-counter/scripts/count.py*)`) that false positives are negligible.
2. **Wait for upstream fix** — blocked indefinitely on an external bug with no timeline.
3. **Workaround: copy skills to `.claude/skills/`** — fragile, version-sync nightmare.

## Decision

Option 1. Both PreToolUse hooks moved to `hooks/hooks.json`. Skill frontmatter hook declarations removed to avoid confusion. The `allow-skill-scripts.py` script and its env var dependencies (`CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`) work correctly in plugin-level hooks.

## Consequences

- Hooks now actually fire. Auto-allow works for skill script invocations.
- Hooks fire on matcher match regardless of whether the skill is active — acceptable given the specific matchers.
- If upstream fixes #17688, hooks could optionally be moved back to skill frontmatter, but there is no compelling reason to do so.
