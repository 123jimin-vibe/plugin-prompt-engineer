"""PreToolUse hook — auto-allow Bash calls that invoke plugin skill scripts.

Pessimistic: every check that fails exits 0 with no output (no opinion,
does *not* auto-allow).  Only an exact match of venv-python + skill
script at the expected depth produces an "allow" decision.
"""

import json
import os
import shlex
import sys
from pathlib import Path


def parse_hook_input() -> tuple[str, ...] | None:
    """Read hook JSON from stdin and return the parsed command tokens."""
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return None

    if not isinstance(hook_input, dict):
        return None

    command = hook_input.get("tool_input", {}).get("command", "")
    try:
        parts = shlex.split(command)
    except ValueError:
        return None

    return tuple(parts) if len(parts) >= 2 else None


def is_venv_python(exe_path: str, plugin_data: str) -> bool:
    """Return True if *exe_path* is a Python interpreter inside the plugin venv."""
    try:
        exe = Path(exe_path).resolve(strict=True)
        venv = (Path(plugin_data) / "venv").resolve(strict=True)
    except (OSError, ValueError):
        return False

    if not exe.is_relative_to(venv):
        return False
    if not exe.stem.startswith("python"):
        return False
    return True


def is_skill_script(script_path: str, plugin_root: str) -> bool:
    """Return True if *script_path* is a .py file at skills/<name>/scripts/<file>.py."""
    try:
        script = Path(script_path).resolve(strict=True)
        skills = (Path(plugin_root) / "skills").resolve(strict=True)
    except (OSError, ValueError):
        return False

    if not script.is_relative_to(skills):
        return False

    relative = script.relative_to(skills)
    if len(relative.parts) != 3:
        return False
    if relative.parts[1] != "scripts":
        return False
    if script.suffix != ".py":
        return False
    return True


def emit_allow() -> None:
    """Write an 'allow' decision to stdout."""
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": "Plugin skill script invocation",
            }
        },
        sys.stdout,
    )


def main() -> None:
    parts = parse_hook_input()
    if parts is None:
        return

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA", "")
    if not plugin_root or not plugin_data:
        raise RuntimeError(
            "CLAUDE_PLUGIN_ROOT and/or CLAUDE_PLUGIN_DATA not set. "
            "This hook must run in a context where plugin env vars are available."
        )

    if not is_venv_python(parts[0], plugin_data):
        return
    if not is_skill_script(parts[1], plugin_root):
        return

    emit_allow()


if __name__ == "__main__":
    main()
