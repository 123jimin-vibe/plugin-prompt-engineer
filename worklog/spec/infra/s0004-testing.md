+++
id = "s0004"
title = "Testing"
tags = ["infra", "testing"]
paths = ["tests/**"]
+++

Tests for plugin scripts live in `tests/`, outside the shipped `plugin/` directory.

## Layout

Mirror the `plugin/` source tree under `tests/`:

- `plugin/scripts/<name>.py` → `tests/scripts/test_<name>.py`
- `plugin/skills/<skill>/scripts/<name>.py` → `tests/skills/<skill>/test_<name>.py`

## Conventions

- Use Python's `unittest` library.
- Import modules with hyphenated filenames via `importlib.util.spec_from_file_location` — do **not** manipulate `sys.path`.
- Tests that need real filesystem paths (e.g. for `pathlib.Path.resolve(strict=True)`) use `tempfile.mkdtemp` and clean up in `tearDown`.
- Tests that cannot run on all platforms (e.g. symlink creation on Windows) should `self.skipTest(...)` gracefully.

## Running

```
python -m pytest tests/ -v
```

## Writing Tests for New Scripts

Tests must be written **without reading the implementation** — only the function signatures and docstrings. This guards against testing implementation details rather than behavior.
