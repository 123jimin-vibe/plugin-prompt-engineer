+++
id = "s0003"
title = "Python Environment"
tags = ["dependencies", "setup"]
paths = ["plugin/pyproject.toml", "plugin/scripts/**", "plugin/hooks/**", "plugin/lib/**"]
+++

Manages the plugin's Python environment: dependencies, shared code, and venv lifecycle.

## Package

The plugin root (`plugin/`) is a pip-installable Python package defined by `plugin/pyproject.toml`. It declares third-party dependencies and exposes `plugin/lib/` as an importable package.

## Shared Code

`plugin/lib/` is a Python package importable as `lib` by all skill scripts. Installed in editable mode so changes take effect without reinstalling.

## Venv Lifecycle

A `SessionStart` hook (`plugin/hooks/hooks.json`) runs `plugin/scripts/ensure-deps.py`, which:

1. Compares the bundled `pyproject.toml` against a cached copy in `${CLAUDE_PLUGIN_DATA}`.
2. On mismatch (or first run), creates a venv at `${CLAUDE_PLUGIN_DATA}/venv` and runs `pip install -e`.
3. Copies the manifest on success; removes the cached copy on failure so the next session retries.

Cross-platform: uses `venv/Scripts/pip` on Windows, `venv/bin/pip` elsewhere.

## Usage

Skill scripts run with the venv Python at `${CLAUDE_PLUGIN_DATA}/venv`. They can `from lib import ...` directly.

## Plugin Variables

- `${CLAUDE_PLUGIN_ROOT}` — plugin install directory (ephemeral; wiped on update).
- `${CLAUDE_PLUGIN_DATA}` — persistent data directory (survives updates; deleted on uninstall).
