+++
id = "t0008"
title = "Fix PreToolUse hook not firing for skill scripts"
status = "done"
tags = ["hooks", "token-counter", "invoke-llm"]
modifies = ["s0002", "s0003"]
blocked_by = []
+++

## Problem

PreToolUse hooks defined in skill SKILL.md frontmatter are silently ignored when loaded via plugins. Confirmed as upstream bug: anthropics/claude-code#17688. Debug log showed 0 skill-scoped hooks registered.

## Root cause

The plugin system only loads hooks from `hooks/hooks.json`. Skill frontmatter `hooks:` blocks are parsed for project skills (`.claude/skills/`) but not for plugin skills.

## Resolution (d0003)

Moved both PreToolUse hooks to `hooks/hooks.json`. Removed dead hook declarations from skill frontmatter. Bumped plugin version to 0.0.11.

### Files changed

- `plugin/hooks/hooks.json` — added PreToolUse matchers for both skills
- `plugin/skills/invoke-llm/SKILL.md` — removed frontmatter hooks
- `plugin/skills/token-counter/SKILL.md` — removed frontmatter hooks
- `plugin/.claude-plugin/plugin.json` — version 0.0.10 → 0.0.11
