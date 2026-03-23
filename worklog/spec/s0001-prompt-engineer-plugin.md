+++
id = "s0001"
title = "Prompt Engineer Plugin"
tags = ["plugin", "core"]
paths = ["plugin/**"]
+++

Claude Code plugin providing prompt-engineering utilities as skills.

Plugin root is `plugin/`. Name: `prompt-engineer`, version `0.0.1`.

## Structure

- `plugin/.claude-plugin/plugin.json` — plugin manifest (name, description, version).
- `plugin/skills/` — each subdirectory is a skill exposed by the plugin.
- `plugin/lib/` — shared library code used across skills (currently empty).

## Skills

- **token-counter** — see [s0002](s0002-token-counter.md).

## Conventions

- Skill scripts are written in Python (see [d0001](../decision/d0001-python-for-plugin-scripts.md)).

## Dependencies

Python dependencies are declared in `plugin/requirements.txt` and installed into a virtual environment under `${CLAUDE_PLUGIN_DATA}`.

A `SessionStart` hook compares the bundled `requirements.txt` against a cached copy in `${CLAUDE_PLUGIN_DATA}`. When they differ (or on first run), the hook creates/updates a venv and runs `pip install -r`. If installation fails, the cached copy is removed so the next session retries.

Scripts reference the venv via `${CLAUDE_PLUGIN_DATA}`.

## Plugin Variables

- `${CLAUDE_PLUGIN_ROOT}` — plugin install directory (ephemeral; wiped on update).
- `${CLAUDE_PLUGIN_DATA}` — persistent data directory (survives updates; deleted on uninstall).

## Anticipated Changes

- Additional skills will be added over time.
