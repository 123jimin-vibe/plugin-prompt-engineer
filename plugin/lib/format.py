"""Plain-text formatting utilities for skill script output."""


def render_table(
    rows: list[tuple[str, ...]],
    columns: list[str],
    separator_before: int | list[int] | None = None,
) -> str:
    """Render a right-aligned plain-text table with a header separator."""
    # Column widths from header and data.
    widths = [len(c) for c in columns]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    sep_line = "──".join("─" * w for w in widths)

    # Normalize separator_before to a set of positive indices.
    if separator_before is None:
        sep_indices: set[int] = set()
    elif isinstance(separator_before, int):
        sep_indices = {separator_before % len(rows)} if rows else set()
    else:
        sep_indices = {idx % len(rows) for idx in separator_before} if rows else set()

    def format_row(cells: list[str] | tuple[str, ...]) -> str:
        return "  ".join(cell.rjust(w) for cell, w in zip(cells, widths))

    lines = [format_row(columns), sep_line]
    for i, row in enumerate(rows):
        if i in sep_indices:
            lines.append(sep_line)
        lines.append(format_row(row))

    return "\n".join(lines)
