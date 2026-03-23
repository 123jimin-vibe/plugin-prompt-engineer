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
| `-s` | Per-section breakdown (YAML frontmatter + `##` headings). |

## Behavior

- Single input + single model → scalar count.
- Multiple inputs or models → comparison table.
- `-s` splits the input at YAML frontmatter and `##` headings, reporting counts per section.

## Dependencies

Requires `tiktoken` (declared in `plugin/pyproject.toml` — see [s0001](s0001-prompt-engineer-plugin.md#dependencies)).

## Script

Currently a stub that verifies tiktoken is importable. Invoked via the plugin venv at `${CLAUDE_PLUGIN_DATA}/venv`.

## Anticipated Changes

- TODO: implement the counting script.
- TODO: determine which tokenizer library/API to use for each model.
