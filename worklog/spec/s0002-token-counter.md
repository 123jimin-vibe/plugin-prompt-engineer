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

Requires `tiktoken` (declared in `plugin/requirements.txt`, installed into venv at `${CLAUDE_PLUGIN_DATA}` — see [s0001](s0001-prompt-engineer-plugin.md#dependencies)).

## Script

TODO: `plugin/skills/token-counter/scripts/token-count.py` — not yet implemented (`scripts/` directory is empty).

SKILL.md currently declares `Script:` with no path. Will need updating once the script exists.

Invoked via the venv Python at `${CLAUDE_PLUGIN_DATA}/venv/bin/python` (or `Scripts/python` on Windows).

## Anticipated Changes

- TODO: implement the counting script.
- TODO: determine which tokenizer library/API to use for each model.
- TODO: update SKILL.md to reference the actual script path once implemented.
