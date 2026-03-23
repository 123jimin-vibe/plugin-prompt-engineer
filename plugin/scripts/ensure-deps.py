"""Ensure plugin Python dependencies are installed.

Compares the bundled requirements.txt against a cached copy in the
persistent data directory. On mismatch (or first run), creates a venv
and installs dependencies. Removes the cached copy on failure so the
next session retries.
"""

import filecmp
import os
import shutil
import subprocess
import sys
import venv


def main():
    plugin_root = os.environ["CLAUDE_PLUGIN_ROOT"]
    plugin_data = os.environ["CLAUDE_PLUGIN_DATA"]

    bundled = os.path.join(plugin_root, "requirements.txt")
    cached = os.path.join(plugin_data, "requirements.txt")
    venv_dir = os.path.join(plugin_data, "venv")

    # Already up to date
    if os.path.exists(cached) and filecmp.cmp(bundled, cached, shallow=False):
        return

    # Create or refresh venv
    venv.create(venv_dir, with_pip=True, clear=True)

    # pip path is platform-dependent
    if sys.platform == "win32":
        pip = os.path.join(venv_dir, "Scripts", "pip")
    else:
        pip = os.path.join(venv_dir, "bin", "pip")

    try:
        subprocess.run(
            [pip, "install", "-r", bundled],
            check=True,
        )
        shutil.copy2(bundled, cached)
    except Exception:
        # Remove cached copy so next session retries
        if os.path.exists(cached):
            os.remove(cached)
        raise


if __name__ == "__main__":
    main()
