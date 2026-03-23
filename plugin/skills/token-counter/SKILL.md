---
name: token-counter
description: "Count tokens in strings or files."
---
<skill id="prompt-engineer:token-counter">
Script: `${CLAUDE_SKILL_DIR}/scripts/count.py`

Run with the plugin venv at `${CLAUDE_PLUGIN_DATA}/venv`.

| Flag | Description |
|------|-------------|
| (positional) | Strings to count (repeatable) |
| `-f FILE` | File to count (repeatable) |
| `-m MODEL` | Model or tiktoken encoding (repeatable). Default: `claude-opus-4-6` |
| `-s` | Per-section breakdown (YAML frontmatter + `##` headings) |

Multiple inputs or models print a comparison table. Prefer combining repeatable flags into a single invocation (e.g. `-m cl100k_base -m o200k_base`) rather than running the script multiple times.
</skill>