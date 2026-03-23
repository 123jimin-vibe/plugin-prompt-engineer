+++
id = "s0001"
title = "Prompt Engineer Plugin"
tags = ["plugin", "core"]
paths = ["plugin/**"]
+++

Claude Code plugin providing prompt-engineering utilities as skills.

Plugin root is `plugin/`. Name: `prompt-engineer`, version `0.0.1`.

## Structure

Plugin manifest lives at `.claude-plugin/plugin.json` (name, description, version). Each subdirectory under `skills/` is a skill exposed by the plugin.

## Skills

- **token-counter** — see [s0002](s0002-token-counter.md).

## Conventions

- Skill scripts are written in Python (see [d0001](../decision/d0001-python-for-plugin-scripts.md)).
- Python environment and shared code — see [s0003](s0003-python-environment.md).
- Testing — see [s0004](s0004-testing.md).

## Anticipated Changes

- Additional skills will be added over time.
