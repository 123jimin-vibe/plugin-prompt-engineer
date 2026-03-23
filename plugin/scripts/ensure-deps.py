"""Ensure a Claude Code plugin's Python dependencies are installed.

Reads the plugin version from .claude-plugin/plugin.json via
CLAUDE_PLUGIN_ROOT. On version change (or first run), creates a venv
in CLAUDE_PLUGIN_DATA and pip-installs the plugin root as a package.

Requires:
  - CLAUDE_PLUGIN_ROOT pointing to a directory with pyproject.toml
  - CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json containing "version"
  - CLAUDE_PLUGIN_DATA for persistent storage

Reusable across any Claude Code plugin that ships a pyproject.toml.
"""

import json
import os
import subprocess
import sys
import venv
from pathlib import Path


def get_plugin_version(plugin_root: Path) -> str:
    manifest = plugin_root / ".claude-plugin" / "plugin.json"
    return json.loads(manifest.read_text())["version"]


def get_pip(venv_dir: Path) -> Path:
    match sys.platform:
        case "win32":
            return venv_dir / "Scripts" / "pip"
        case _:
            return venv_dir / "bin" / "pip"


def is_up_to_date(version_file: Path, version: str) -> bool:
    if not version_file.exists():
        return False
    return version_file.read_text().strip() == version


def install(plugin_root: Path, plugin_data: Path):
    version = get_plugin_version(plugin_root)
    version_file = plugin_data / "installed-version"
    venv_dir = plugin_data / "venv"

    if is_up_to_date(version_file, version):
        return

    venv.create(venv_dir, with_pip=True, clear=True)

    try:
        subprocess.run(
            [str(get_pip(venv_dir)), "install", str(plugin_root)],
            check=True,
        )
        version_file.write_text(version)
    except Exception:
        version_file.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    install(
        Path(os.environ["CLAUDE_PLUGIN_ROOT"]),
        Path(os.environ["CLAUDE_PLUGIN_DATA"]),
    )
