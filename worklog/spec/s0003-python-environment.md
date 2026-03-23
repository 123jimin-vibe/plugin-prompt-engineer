+++
id = "s0003"
title = "Python Environment"
tags = ["dependencies", "setup"]
paths = ["plugin/pyproject.toml", "plugin/scripts/**", "plugin/hooks/**", "plugin/lib/**"]
+++

Manages the plugin's Python environment: dependencies, shared code, and venv lifecycle.

`ensure-deps.py` is plugin-agnostic — reusable by any Claude Code plugin that ships a `pyproject.toml` and a `.claude-plugin/plugin.json` with a `version` field.

## Package

The plugin root is a pip-installable Python package defined by `pyproject.toml`. It declares third-party dependencies and exposes `lib/` as an importable package.

## Shared Code

`lib/` is a Python package importable by all skill scripts. Installed as a regular (non-editable) package into the venv — the plugin cache is a copy, so editable installs don't work.

## Venv Lifecycle

A `SessionStart` hook runs `scripts/ensure-deps.py`, which:

1. Reads the plugin version from `.claude-plugin/plugin.json`.
2. Compares against `${CLAUDE_PLUGIN_DATA}/installed-version`.
3. On version change (or first run), creates a venv at `${CLAUDE_PLUGIN_DATA}/venv` and runs `pip install`.
4. Writes the version on success; removes the version file on failure so the next session retries.

Cross-platform: uses `venv/Scripts/pip` on Windows, `venv/bin/pip` elsewhere.

### Assumptions

- `CLAUDE_PLUGIN_ROOT` contains a `pyproject.toml`.
- `CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json` contains a `"version"` field.
- `CLAUDE_PLUGIN_DATA` is available for persistent storage.

## Usage

Skill scripts run with the venv Python at `${CLAUDE_PLUGIN_DATA}/venv`. They can `from lib import ...` directly.

## Plugin Variables

- `${CLAUDE_PLUGIN_ROOT}` — plugin install directory (ephemeral; wiped on update).
- `${CLAUDE_PLUGIN_DATA}` — persistent data directory (survives updates; deleted on uninstall).
