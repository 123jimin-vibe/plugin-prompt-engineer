+++
id = "d0004"
title = "Hook matcher matches tool name only; use bash fast-path"
relates_to = ["s0002", "s0003", "s0006"]
supersedes = ["d0003"]
+++

## Context

d0003 moved PreToolUse hooks to `hooks.json` with matchers like `Bash(.*/invoke-llm/scripts/invoke\.py.*)`, assuming the matcher pattern is tested against the tool input (the command string). Investigation of the Claude Code source (cli.js) revealed that **hook matchers are evaluated against the bare tool name only** (e.g. `"Bash"`, `"Write"`, `"Read"`), not the tool input content.

The `Tool(pattern)` syntax exists in Claude Code but belongs to the **permission rules system** (`parseToolSpec`), not the hook matcher system. These are completely separate code paths. As a result, the d0003 matchers never match anything — the regex `Bash(.*/invoke-llm/scripts/invoke\.py.*)` cannot match the string `"Bash"`.

## Options Considered

1. **`"matcher": "Bash"` + filter inside Python script** — works, but launches Python on every Bash tool call. Python startup cost (~100–200ms) is unacceptable for hooks that fire on `git status`, `ls`, etc.
2. **`"matcher": "Bash"` + inline bash fast-path with Python fallthrough** — the hook command uses a bash `case` statement to do a fast string check on the raw JSON input. Only when the input contains a skill script path signature does it pipe to the Python validator. 99% of Bash calls exit immediately with zero subprocess overhead.
3. **Rewrite validation entirely in bash** — eliminates Python but loses the strict security checks (venv resolution, symlink-safe path validation via `Path.resolve(strict=True)`).

## Decision

Option 2. The hook command is an inline bash one-liner:

```bash
input=$(cat); case "$input" in */.claude/*/prompt-engineer/*/skills/*/scripts/*) python "..." <<< "$input" ;; esac
```

The `case` pattern `*/.claude/*/prompt-engineer/*/skills/*/scripts/*` matches paths like `.claude/plugins/cache/jiminp/prompt-engineer/0.0.11/skills/token-counter/scripts/count.py` while rejecting unrelated Bash commands. Here-string (`<<<`) is used instead of `echo`/`printf` to safely pass JSON containing quotes.

- **Fast path** (no skill script in command): bash `case` fails, exits immediately. No subprocess spawned.
- **Slow path** (actual skill script invocation): passes input to `allow-skill-scripts.py` for proper venv + path validation.

## Consequences

- Hooks actually fire (matcher is just `"Bash"`).
- Negligible overhead on non-matching Bash calls — only bash string matching, no Python.
- Full security validation preserved for actual skill script calls.
- A single PreToolUse hook entry covers all skills, since the `case` pattern matches any skill script under this plugin.
