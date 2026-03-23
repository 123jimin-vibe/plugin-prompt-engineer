+++
id = "s0002"
title = "Token Counter Skill"
tags = ["skill", "token-counter"]
paths = ["plugin/skills/token-counter/**"]
+++

Counts tokens in strings or files across one or more models/encodings.

## Interface

| Input | Description |
|-------|-------------|
| (positional) | Strings to count. Repeatable. |
| `-f FILE` | File to count. Repeatable. |
| `-m MODEL` | Model or tiktoken encoding. Repeatable. Default: `claude-opus-4-6`. |
| `-s` | Per-section breakdown (YAML frontmatter + `##` headings). **Not yet implemented.** |

## Behavior

- Single input + single model → scalar count (bare number).
- Multiple inputs or models → comparison table via `render_table` (see [s0005](lib/s0005-render-table.md)). Single-valued dimensions are collapsed (e.g. one model → no Model column).
- `-s` splits the input at YAML frontmatter and `##` headings, reporting counts per section. **TODO.**

## Tokenizer Dispatch

- Models starting with `claude-` use `Anthropic().messages.count_tokens`, wrapping the input as `[{"role": "user", "content": text}]`. Requires `ANTHROPIC_API_KEY`; exits with a clear error if missing.
- Everything else is treated as a tiktoken model/encoding name.

## Input Naming

- Positional strings are truncated to 20 characters (with `…` suffix) for table display.
- Files use their filename.

## Dependencies

Requires `tiktoken` and `anthropic` (declared in `plugin/pyproject.toml`).

## Anticipated Changes

- TODO: implement `-s` section breakdown.
