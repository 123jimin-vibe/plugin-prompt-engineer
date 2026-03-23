+++
id = "t0003"
title = "Use ASCII-safe separators in render_table"
status = "done"
tags = ["lib", "formatting"]
modifies = ["s0005"]
blocked_by = []
+++

The table separator in `render_table` currently uses U+2500 (`─`) which renders as garbage on some terminals (e.g. Windows console output seen as `��`). Replace with ASCII hyphen-minus (`-`) for the header and row separators.

Also replace U+2026 (`…`) ellipsis in `count.py` string truncation with ASCII `...`, for the same reason.

Affected files:
- `plugin/lib/format.py` — separator construction on line 16
- `plugin/skills/token-counter/scripts/count.py` — ellipsis in `collect_inputs`
- `worklog/spec/lib/s0005-render-table.md` — spec example and behavior description reference `─`
- `worklog/spec/s0002-token-counter.md` — mentions `…` suffix
- Tests in `tests/lib/test_render_table.py` — assertions against separator characters
- Tests in `tests/skills/token_counter/test_count.py` — assertions against `…`
