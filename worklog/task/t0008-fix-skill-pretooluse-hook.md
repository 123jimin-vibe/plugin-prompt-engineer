+++
id = "t0008"
title = "Fix PreToolUse hook in skill frontmatter"
status = "pending"
tags = ["hooks", "performance", "token-counter"]
modifies = ["s0002", "s0003"]
blocked_by = []
+++

The `PreToolUse` hook defined in `token-counter/SKILL.md` frontmatter calls `allow-skill-scripts.py`, which depends on `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`. These env vars are only set for plugin-level hooks (`hooks.json`), not skill-scoped hooks. The script silently exits with no opinion, so the auto-allow never fires.

## Constraint

- Must remain a skill-scoped hook (no moving to `hooks.json`).
- Hook invocations and execution time must be minimized. The matcher from t0005 (`Bash(*token-counter/scripts/count.py*)`) already limits when the hook fires; the fix must not regress that. Avoid Python startup (~200ms) if possible.

## Acceptance

- Bash calls that invoke the token-counter script via the plugin venv are auto-allowed without user prompt.
- The hook does not fire on unrelated Bash commands.
- No dependency on `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PLUGIN_DATA` env vars.
