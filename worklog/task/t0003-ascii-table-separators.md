+++
id = "t0003"
title = "Use ASCII-safe separators in render_table"
status = "pending"
tags = ["lib", "formatting"]
modifies = ["s0005"]
blocked_by = []
+++

The table separator in `render_table` currently uses U+2500 (`─`) which renders as garbage on some terminals (e.g. Windows console output seen as `��`). Replace with ASCII hyphen-minus (`-`) for the header and row separators.

Affected files:
- `plugin/lib/format.py` — separator construction on line 16
- `worklog/spec/lib/s0005-render-table.md` — spec example and behavior description reference `─`
- Tests in `tests/lib/test_render_table.py` — assertions against separator characters
