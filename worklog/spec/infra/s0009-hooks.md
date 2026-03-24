+++
id = "s0009"
title = "Plugin Hooks"
tags = ["infra", "hooks"]
paths = ["plugin/hooks/hooks.json", "plugin/scripts/allow-skill-scripts.py"]
+++

Hooks that run automatically during the plugin lifecycle. Defined in `hooks/hooks.json`.

## SessionStart: ensure-deps

Runs `scripts/ensure-deps.py` on session start. Installs or updates the plugin's Python venv when the plugin version changes. See [s0003](s0003-python-environment.md) for venv lifecycle details.

## PreToolUse: allow-skill-scripts

Auto-allows Bash tool calls that invoke plugin skill scripts, removing the manual approval prompt.

### Matching

The `hooks.json` matcher targets `Bash` tool calls. A fast-path shell `case` statement checks whether the command path contains a plugin skill scripts directory before invoking the Python hook. See [d0004](../../decision/d0004-hook-matcher-bash-fastpath.md).

### Validation

`allow-skill-scripts.py` is pessimistic — it only emits an `allow` decision when **all** of these hold:

1. The hook JSON parses successfully and contains a command with at least two tokens.
2. The first token is a Python interpreter inside the plugin's venv (`$CLAUDE_PLUGIN_DATA/venv`).
3. The second token is a `.py` file at exactly `skills/<name>/scripts/<file>.py` under `$CLAUDE_PLUGIN_ROOT`.

Any check failure → exit silently with no output (no opinion, does not auto-allow).

### Design decisions

- Scoped to skill scripts only, not all plugin scripts — see [d0002](../../decision/d0002-skill-scoped-pretooluse.md).
- Hook config lives in `hooks.json`, not in skill manifests — see [d0003](../../decision/d0003-pretooluse-in-hooks-json.md).
- Fast-path shell filter before Python — see [d0004](../../decision/d0004-hook-matcher-bash-fastpath.md).
