"""I/O helpers — encoding safety for Windows consoles."""

import sys


def ensure_utf8_stdio() -> None:
    """Reconfigure stdout/stderr to UTF-8 if possible.

    On Windows, the console code page (e.g. cp949, cp1252) may not support
    all Unicode characters, causing UnicodeEncodeError on print(). This is
    a no-op when reconfigure is unavailable (e.g. redirected to a pipe that
    is not a TextIOWrapper).
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
