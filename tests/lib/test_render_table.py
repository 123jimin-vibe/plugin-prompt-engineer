"""Tests for render_table() in plugin/lib/format.py"""

import importlib.util
import pathlib
import unittest

# ---------------------------------------------------------------------------
# Load the module under test via importlib.
# Guard so the test file is importable even when the implementation is missing.
# ---------------------------------------------------------------------------
_MODULE_PATH = str(
    pathlib.Path(__file__).resolve().parents[2]
    / "plugin"
    / "lib"
    / "format.py"
)
_spec = importlib.util.spec_from_file_location("format", _MODULE_PATH)

_module_available = _spec is not None and _spec.loader is not None
if _module_available:
    try:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        render_table = _mod.render_table
    except Exception:
        _module_available = False


def _sep_line(widths: list[int]) -> str:
    """Build the expected separator line for given column widths.

    Each column gets '─' repeated to its width, joined by '  ' (two spaces).
    """
    return "  ".join("─" * w for w in widths)


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestRenderTableBasic(unittest.TestCase):
    """Basic / structural behaviour."""

    def test_single_row(self):
        result = render_table(
            rows=[("hello",)],
            columns=["Word"],
        )
        lines = result.split("\n")
        self.assertEqual(len(lines), 3)  # header, separator, one data row

    def test_multi_row(self):
        result = render_table(
            rows=[("a",), ("bb",), ("ccc",)],
            columns=["Col"],
        )
        lines = result.split("\n")
        # header + separator + 3 data rows = 5
        self.assertEqual(len(lines), 5)

    def test_empty_rows_list(self):
        """No data rows — should still have the header and separator."""
        result = render_table(rows=[], columns=["Name", "Value"])
        lines = result.split("\n")
        self.assertEqual(len(lines), 2)  # header + separator

    def test_no_trailing_newline(self):
        result = render_table(
            rows=[("x",)],
            columns=["C"],
        )
        self.assertFalse(result.endswith("\n"))

    def test_no_trailing_newline_empty_rows(self):
        result = render_table(rows=[], columns=["A"])
        self.assertFalse(result.endswith("\n"))


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestHeaderSeparator(unittest.TestCase):
    """The header separator line is always present."""

    def test_separator_present(self):
        result = render_table(
            rows=[("data",)],
            columns=["Heading"],
        )
        lines = result.split("\n")
        # The second line must be the separator.
        separator = lines[1]
        # Must consist only of '─' and spaces (the column gap).
        self.assertTrue(
            all(ch in ("─", " ") for ch in separator),
            f"Unexpected characters in separator: {separator!r}",
        )

    def test_separator_width_matches_header(self):
        """Separator columns should be exactly as wide as the column widths."""
        result = render_table(
            rows=[("ab",)],
            columns=["Heading"],
        )
        lines = result.split("\n")
        header_line = lines[0]
        separator_line = lines[1]
        self.assertEqual(len(header_line), len(separator_line))


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestRightAlignment(unittest.TestCase):
    """All columns are right-aligned."""

    def test_single_column_right_aligned(self):
        result = render_table(
            rows=[("ab",), ("abcd",)],
            columns=["Col"],
        )
        lines = result.split("\n")
        # Column width should be 4 (max of "Col"=3, "ab"=2, "abcd"=4).
        # "Col" should be right-aligned → " Col"
        # "ab"  should be right-aligned → "  ab"
        header_line = lines[0]
        self.assertEqual(header_line, " Col")
        data_line_1 = lines[2]
        self.assertEqual(data_line_1, "  ab")
        data_line_2 = lines[3]
        self.assertEqual(data_line_2, "abcd")

    def test_two_columns_right_aligned(self):
        result = render_table(
            rows=[("a", "bb"), ("ccc", "d")],
            columns=["X", "YY"],
        )
        lines = result.split("\n")
        # Col 0 width = max("X"=1, "a"=1, "ccc"=3) = 3
        # Col 1 width = max("YY"=2, "bb"=2, "d"=1) = 2
        # Gap is two spaces.
        # Header:  "  X  YY"
        # Data 1:  "  a  bb"
        # Data 2:  "ccc   d"
        self.assertEqual(lines[0], "  X  YY")
        self.assertEqual(lines[2], "  a  bb")
        self.assertEqual(lines[3], "ccc   d")


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestColumnWidth(unittest.TestCase):
    """Column width is determined by the widest cell (header or data)."""

    def test_header_is_widest(self):
        result = render_table(
            rows=[("a",)],
            columns=["LongHeader"],
        )
        lines = result.split("\n")
        # Width should be len("LongHeader") = 10
        self.assertEqual(lines[0], "LongHeader")
        # "a" is right-aligned within 10 characters.
        self.assertEqual(lines[2], "         a")

    def test_data_is_widest(self):
        result = render_table(
            rows=[("widevalue",)],
            columns=["H"],
        )
        lines = result.split("\n")
        # Width = len("widevalue") = 9
        self.assertEqual(lines[0], "        H")
        self.assertEqual(lines[2], "widevalue")


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestColumnGap(unittest.TestCase):
    """Column gap between columns is two spaces."""

    def test_gap_between_columns(self):
        result = render_table(
            rows=[("a", "b")],
            columns=["A", "B"],
        )
        lines = result.split("\n")
        # Both columns are width 1. Output: "A  B"
        self.assertEqual(lines[0], "A  B")
        self.assertEqual(lines[2], "a  b")

    def test_gap_with_wider_columns(self):
        result = render_table(
            rows=[("aaa", "bb")],
            columns=["X", "Y"],
        )
        lines = result.split("\n")
        # Col 0 width = 3, Col 1 width = 2.
        # Header: "  X   Y"  (3-char col + 2 spaces + 2-char col)
        self.assertEqual(lines[0], "  X   Y")

    def test_three_columns(self):
        result = render_table(
            rows=[("1", "22", "333")],
            columns=["A", "BB", "CCC"],
        )
        lines = result.split("\n")
        # Col widths: 1, 2, 3
        # Header: "A  BB  CCC"
        self.assertEqual(lines[0], "A  BB  CCC")
        self.assertEqual(lines[2], "1  22  333")


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestSeparatorBeforeNone(unittest.TestCase):
    """separator_before=None produces no extra separators."""

    def test_no_extra_separator(self):
        result = render_table(
            rows=[("a",), ("b",), ("c",)],
            columns=["X"],
            separator_before=None,
        )
        lines = result.split("\n")
        # Only the header separator (line index 1) should be a separator.
        sep_count = sum(1 for l in lines if all(ch in ("─", " ") for ch in l))
        self.assertEqual(sep_count, 1)


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestSeparatorBeforeSingleInt(unittest.TestCase):
    """separator_before with a single int inserts one extra separator."""

    def test_separator_before_last_row(self):
        result = render_table(
            rows=[("alice", "100"), ("bob", "200"), ("Total", "300")],
            columns=["Name", "Score"],
            separator_before=2,
        )
        lines = result.split("\n")
        # Expected layout:
        #  line 0: header
        #  line 1: header separator
        #  line 2: alice  100
        #  line 3: bob    200
        #  line 4: separator
        #  line 5: Total  300
        self.assertEqual(len(lines), 6)
        # Line 4 should be a separator.
        self.assertTrue(
            all(ch in ("─", " ") for ch in lines[4]),
            f"Expected separator, got: {lines[4]!r}",
        )

    def test_separator_before_first_row(self):
        result = render_table(
            rows=[("a",), ("b",)],
            columns=["C"],
            separator_before=0,
        )
        lines = result.split("\n")
        # header, header-sep, extra-sep, row0, row1 = 5
        self.assertEqual(len(lines), 5)
        # Line 2 should be a separator.
        self.assertTrue(all(ch in ("─", " ") for ch in lines[2]))


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestSeparatorBeforeList(unittest.TestCase):
    """separator_before with a list of ints inserts multiple separators."""

    def test_two_separators(self):
        result = render_table(
            rows=[("a",), ("b",), ("c",), ("d",)],
            columns=["V"],
            separator_before=[1, 3],
        )
        lines = result.split("\n")
        # header, header-sep, row0, sep, row1, row2, sep, row3 = 8
        self.assertEqual(len(lines), 8)
        # Verify separator lines
        self.assertTrue(all(ch in ("─", " ") for ch in lines[3]))
        self.assertTrue(all(ch in ("─", " ") for ch in lines[6]))


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestSeparatorBeforeNegativeIndex(unittest.TestCase):
    """separator_before supports negative indices."""

    def test_negative_one(self):
        """separator_before=-1 should insert a separator before the last row."""
        result = render_table(
            rows=[("a",), ("b",), ("c",)],
            columns=["V"],
            separator_before=-1,
        )
        lines = result.split("\n")
        # header, header-sep, row0, row1, sep, row2 = 6
        self.assertEqual(len(lines), 6)
        self.assertTrue(all(ch in ("─", " ") for ch in lines[4]))

    def test_negative_in_list(self):
        """Negative index inside a list."""
        result = render_table(
            rows=[("a",), ("b",), ("c",)],
            columns=["V"],
            separator_before=[-1],
        )
        lines = result.split("\n")
        self.assertEqual(len(lines), 6)
        self.assertTrue(all(ch in ("─", " ") for ch in lines[4]))


@unittest.skipUnless(_module_available, "plugin/lib/format.py not available")
class TestExampleFromSpec(unittest.TestCase):
    """End-to-end check matching the spec's example output."""

    def test_spec_example(self):
        result = render_table(
            rows=[
                ("claude-opus", "842"),
                ("gpt4", "837"),
                ("Total", "842"),
            ],
            columns=["Model", "Tokens"],
            separator_before=2,
        )
        expected_lines = [
            "      Model  Tokens",
            "───────────────────",
            "claude-opus     842",
            "       gpt4     837",
            "───────────────────",
            "      Total     842",
        ]
        self.assertEqual(result, "\n".join(expected_lines))


if __name__ == "__main__":
    unittest.main()
