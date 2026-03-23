+++
id = "s0005"
title = "Output Formatting"
tags = ["lib", "formatting"]
paths = ["plugin/lib/**"]
+++

Shared plain-text formatting utilities for skill script output, living in `lib/`. Not yet implemented.

## `render_table`

Renders a plain-text table with right-aligned columns, a header separator, and optional row separators.

### Signature

```python
render_table(
    rows: list[tuple[str, ...]],
    columns: list[str],
    separator_before: int | list[int] | None = None,
) -> str
```

### Behavior

- Column widths are computed from the maximum cell width in each column (including the header).
- All columns are right-aligned by default.
- A header separator (`─` repeated to column width, joined by `──`) is always printed between the header row and the first data row.
- `separator_before` inserts a horizontal rule before the row at the given index (or indices). Negative indices are supported.
- Returns a single string with newline-separated lines (no trailing newline).

### Example

```
      Model  Tokens
───────────────────
claude-opus    842
       gpt4    837
───────────────────
      Total    842
```
