---
name: token-counter
description: "Count tokens in strings or files."
---
<skill id="prompt-engineer:token-counter">
Script:

| Flag | Description |
|------|-------------|
| (positional) | Strings to count (repeatable) |
| `-f FILE` | File to count (repeatable) |
| `-m MODEL` | Model or tiktoken encoding (repeatable). Default: `claude-opus-4-6` |
| `-s` | Per-section breakdown (YAML frontmatter + `##` headings) |

Multiple inputs or models print a comparison table.
</skill>