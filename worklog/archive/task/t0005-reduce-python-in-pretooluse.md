+++
id = "t0005"
title = "Reduce Python invocations in PreToolUse hook"
status = "done"
tags = ["hooks", "performance"]
modifies = ["s0003"]
blocked_by = []
+++

The `PreToolUse` hook runs `python allow-skill-scripts.py` on every Bash tool use, adding ~200ms of Python startup overhead per invocation (measured on Windows).

Use a more specific `matcher` pattern in `hooks.json` so the hook only fires on Bash commands that look like skill script invocations (e.g. `Bash(*skills/*/scripts/*.py*)`), rather than on every Bash call. This eliminates the ~200ms Python startup overhead for the vast majority of Bash tool uses. The remaining invocations where the hook does fire are actual skill calls, where the overhead is negligible relative to the script's own runtime.
