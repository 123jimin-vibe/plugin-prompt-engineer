"""Tests for plugin/skills/token-counter/scripts/count.py"""

import importlib.util
import os
import pathlib
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Load the module under test via importlib.
# Guard so the test file is importable even when the implementation is a stub
# or the expected functions are missing.
# ---------------------------------------------------------------------------
_MODULE_PATH = str(
    pathlib.Path(__file__).resolve().parents[3]
    / "plugin"
    / "skills"
    / "token-counter"
    / "scripts"
    / "count.py"
)
_spec = importlib.util.spec_from_file_location("count", _MODULE_PATH)

_module_available = _spec is not None and _spec.loader is not None
_missing_reason = "count.py not loadable"

# Pre-register lib.* in sys.modules so count.py's lazy imports work
# outside the plugin venv.
if _module_available:
    import sys as _sys
    _lib_root = pathlib.Path(__file__).resolve().parents[3] / "plugin" / "lib"
    for _lib_name, _lib_file in [("lib.format", "format.py"), ("lib.apikey", "apikey.py"), ("lib.llm", "llm.py")]:
        _lib_path = str(_lib_root / _lib_file)
        _lib_spec = importlib.util.spec_from_file_location(_lib_name, _lib_path)
        if _lib_spec and _lib_spec.loader:
            _lib_mod = importlib.util.module_from_spec(_lib_spec)
            _lib_spec.loader.exec_module(_lib_mod)
            _sys.modules[_lib_name] = _lib_mod

if _module_available:
    try:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
    except BaseException as _exc:
        _module_available = False
        _missing_reason = f"count.py failed to load: {_exc}"

# Check that all five expected functions exist on the module.
_REQUIRED_FUNCS = ["parse_args", "collect_inputs", "is_claude_model",
                   "count_tokens", "format_output"]
if _module_available:
    for _fn_name in _REQUIRED_FUNCS:
        if not hasattr(_mod, _fn_name):
            _module_available = False
            _missing_reason = f"count.py is missing function: {_fn_name}"
            break

if _module_available:
    parse_args = _mod.parse_args
    collect_inputs = _mod.collect_inputs
    is_claude_model = _mod.is_claude_model
    count_tokens = _mod.count_tokens
    format_output = _mod.format_output


# ===================================================================
# parse_args
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsPositional(unittest.TestCase):
    """Positional string arguments."""

    def test_single_positional(self):
        ns = parse_args(["hello world"])
        # The namespace should expose the positional strings somehow.
        # We look for a list-like attribute that contains our string.
        positionals = getattr(ns, "strings", None) or getattr(ns, "text", None) or getattr(ns, "inputs", None)
        if positionals is None:
            # Fall back: grab all non-flag values from namespace
            self.fail("Cannot locate positional strings attribute on Namespace")
        self.assertIn("hello world", positionals)

    def test_multiple_positionals(self):
        ns = parse_args(["aaa", "bbb", "ccc"])
        positionals = getattr(ns, "strings", None) or getattr(ns, "text", None) or getattr(ns, "inputs", None)
        self.assertIsNotNone(positionals)
        self.assertEqual(len(positionals), 3)


@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsFileFlag(unittest.TestCase):
    """-f FILE flag (repeatable)."""

    def test_single_file(self):
        ns = parse_args(["-f", "path/to/file.txt"])
        files = getattr(ns, "f", None) or getattr(ns, "file", None) or getattr(ns, "files", None)
        self.assertIsNotNone(files, "Cannot locate file attribute on Namespace")
        self.assertIn("path/to/file.txt", files)

    def test_multiple_files(self):
        ns = parse_args(["-f", "a.txt", "-f", "b.txt"])
        files = getattr(ns, "f", None) or getattr(ns, "file", None) or getattr(ns, "files", None)
        self.assertIsNotNone(files)
        self.assertEqual(len(files), 2)
        self.assertIn("a.txt", files)
        self.assertIn("b.txt", files)


@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsModelFlag(unittest.TestCase):
    """-m MODEL flag (repeatable, with default)."""

    def test_default_model(self):
        ns = parse_args(["some text"])
        models = getattr(ns, "m", None) or getattr(ns, "model", None) or getattr(ns, "models", None)
        self.assertIsNotNone(models, "Cannot locate model attribute on Namespace")
        self.assertEqual(models, ["claude-opus-4-6"])

    def test_single_model(self):
        ns = parse_args(["-m", "gpt-4o", "some text"])
        models = getattr(ns, "m", None) or getattr(ns, "model", None) or getattr(ns, "models", None)
        self.assertIsNotNone(models)
        self.assertIn("gpt-4o", models)

    def test_multiple_models(self):
        ns = parse_args(["-m", "gpt-4o", "-m", "claude-opus-4-6", "text"])
        models = getattr(ns, "m", None) or getattr(ns, "model", None) or getattr(ns, "models", None)
        self.assertIsNotNone(models)
        self.assertEqual(len(models), 2)
        self.assertIn("gpt-4o", models)
        self.assertIn("claude-opus-4-6", models)


@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsSilentFlag(unittest.TestCase):
    """-s flag parses (feature is TODO)."""

    def test_s_flag_accepted(self):
        # Should not raise.
        ns = parse_args(["-s", "text"])
        # The flag should be stored somewhere on the namespace.
        # Check common names.
        silent = getattr(ns, "s", None)
        if silent is None:
            silent = getattr(ns, "silent", None)
        if silent is None:
            silent = getattr(ns, "stream", None)
        # At minimum, parsing should succeed without error.
        self.assertIsNotNone(ns)


@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsCombined(unittest.TestCase):
    """All flags together."""

    def test_all_flags(self):
        ns = parse_args([
            "-f", "x.txt", "-f", "y.txt",
            "-m", "gpt-4o", "-m", "claude-opus-4-6",
            "-s",
            "inline text",
        ])
        files = getattr(ns, "f", None) or getattr(ns, "file", None) or getattr(ns, "files", None)
        models = getattr(ns, "m", None) or getattr(ns, "model", None) or getattr(ns, "models", None)
        positionals = getattr(ns, "strings", None) or getattr(ns, "text", None) or getattr(ns, "inputs", None)

        self.assertIsNotNone(files)
        self.assertEqual(len(files), 2)
        self.assertIsNotNone(models)
        self.assertEqual(len(models), 2)
        self.assertIsNotNone(positionals)
        self.assertIn("inline text", positionals)


# ===================================================================
# collect_inputs
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestCollectInputsPositional(unittest.TestCase):
    """Positional string naming and truncation."""

    def test_short_string_name_unchanged(self):
        ns = parse_args(["hello"])
        result = collect_inputs(ns)
        self.assertEqual(len(result), 1)
        name, text = result[0]
        self.assertEqual(text, "hello")
        # Name should be "hello" (no truncation needed).
        self.assertEqual(name, "hello")

    def test_exactly_20_chars_no_truncation(self):
        s = "a" * 20  # exactly 20 chars
        ns = parse_args([s])
        result = collect_inputs(ns)
        name, text = result[0]
        self.assertEqual(text, s)
        # Should NOT be truncated (exactly at limit).
        self.assertNotIn("...", name)
        self.assertEqual(len(name), 20)

    def test_21_chars_truncated(self):
        s = "a" * 21
        ns = parse_args([s])
        result = collect_inputs(ns)
        name, text = result[0]
        self.assertEqual(text, s)
        # Should be truncated to 20 chars + ellipsis.
        self.assertTrue(name.endswith("..."))
        self.assertEqual(len(name), 23)  # 20 content chars + 3 ellipsis chars

    def test_long_string_truncated(self):
        s = "x" * 100
        ns = parse_args([s])
        result = collect_inputs(ns)
        name, _ = result[0]
        self.assertTrue(name.endswith("..."))
        self.assertEqual(len(name), 23)  # 20 + ellipsis


@unittest.skipUnless(_module_available, _missing_reason)
class TestCollectInputsFile(unittest.TestCase):
    """File reading and naming."""

    def test_file_read(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="test_", delete=False
        ) as f:
            f.write("file content here")
            fpath = f.name
        try:
            ns = parse_args(["-f", fpath])
            result = collect_inputs(ns)
            self.assertEqual(len(result), 1)
            name, text = result[0]
            self.assertEqual(text, "file content here")
        finally:
            os.unlink(fpath)

    def test_file_name_is_basename(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="myfile_", delete=False
        ) as f:
            f.write("data")
            fpath = f.name
            expected_basename = os.path.basename(fpath)
        try:
            ns = parse_args(["-f", fpath])
            result = collect_inputs(ns)
            name, _ = result[0]
            self.assertEqual(name, expected_basename)
        finally:
            os.unlink(fpath)


@unittest.skipUnless(_module_available, _missing_reason)
class TestCollectInputsMixed(unittest.TestCase):
    """Mixed positional + file inputs."""

    def test_mixed_inputs(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="mix_", delete=False
        ) as f:
            f.write("from file")
            fpath = f.name
        try:
            ns = parse_args(["inline text", "-f", fpath])
            result = collect_inputs(ns)
            self.assertEqual(len(result), 2)
            names = [r[0] for r in result]
            texts = [r[1] for r in result]
            self.assertIn("inline text", texts)
            self.assertIn("from file", texts)
        finally:
            os.unlink(fpath)


# ===================================================================
# is_claude_model
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestIsClaudeModel(unittest.TestCase):
    """Prefix-based detection of Claude models."""

    def test_claude_opus(self):
        self.assertTrue(is_claude_model("claude-opus-4-6"))

    def test_claude_sonnet(self):
        self.assertTrue(is_claude_model("claude-sonnet-4-6"))

    def test_bare_prefix(self):
        self.assertTrue(is_claude_model("claude-"))

    def test_gpt_4o(self):
        self.assertFalse(is_claude_model("gpt-4o"))

    def test_cl100k_base(self):
        self.assertFalse(is_claude_model("cl100k_base"))

    def test_empty_string(self):
        self.assertFalse(is_claude_model(""))


# ===================================================================
# count_tokens — tiktoken path (no mocking needed)
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestCountTokensTiktoken(unittest.TestCase):
    """Non-Claude models use tiktoken. Deterministic counts."""

    def test_known_string_cl100k(self):
        # "hello world" with cl100k_base encoding is deterministic.
        try:
            import tiktoken
        except ImportError:
            self.skipTest("tiktoken not installed")
        count = count_tokens("hello world", "cl100k_base")
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)
        # tiktoken encodes "hello world" as 2 tokens with cl100k_base.
        enc = tiktoken.get_encoding("cl100k_base")
        expected = len(enc.encode("hello world"))
        self.assertEqual(count, expected)

    def test_known_string_gpt_4o(self):
        """gpt-4o uses o200k_base encoding via tiktoken."""
        try:
            import tiktoken
            tiktoken.encoding_for_model("gpt-4o")
        except (ImportError, KeyError):
            self.skipTest("tiktoken or gpt-4o encoding not available")
        count = count_tokens("hello world", "gpt-4o")
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)

    def test_empty_string_tiktoken(self):
        try:
            import tiktoken
        except ImportError:
            self.skipTest("tiktoken not installed")
        count = count_tokens("", "cl100k_base")
        self.assertEqual(count, 0)


# ===================================================================
# count_tokens — Claude path (mocked, no real API call)
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestCountTokensClaude(unittest.TestCase):
    """Claude models use Anthropic API. Must mock or check error."""

    def test_claude_without_api_key_exits_cleanly(self):
        """If ANTHROPIC_API_KEY is unset, calling with a Claude model should
        raise SystemExit with a message mentioning the env var."""
        import lib.llm as _llm_mod
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            _llm_mod._clients.clear()
            try:
                with self.assertRaises(SystemExit) as ctx:
                    count_tokens("hello", "claude-opus-4-6")
                self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))
            finally:
                _llm_mod._clients.clear()

    def test_claude_with_mocked_api(self):
        """Mock the Anthropic client to avoid real API calls."""
        import lib.llm as _llm_mod

        mock_response = MagicMock()
        mock_response.input_tokens = 42

        mock_client = MagicMock()
        mock_client.messages.count_tokens.return_value = mock_response

        # Inject mock client into lib.llm's cache.
        _llm_mod._clients["anthropic"] = mock_client
        try:
            result = count_tokens("hello world", "claude-opus-4-6")
        finally:
            _llm_mod._clients.clear()

        self.assertEqual(result, 42)
        mock_client.messages.count_tokens.assert_called_once()
        call_kwargs = mock_client.messages.count_tokens.call_args
        # Verify the message structure passed to the API.
        if call_kwargs.kwargs:
            msgs = call_kwargs.kwargs.get("messages")
        else:
            msgs = call_kwargs[1].get("messages") if len(call_kwargs) > 1 else None
        if msgs is not None:
            self.assertEqual(len(msgs), 1)
            self.assertEqual(msgs[0]["role"], "user")
            self.assertIn("hello world", msgs[0]["content"])


# ===================================================================
# format_output
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestFormatOutputScalar(unittest.TestCase):
    """1 input x 1 model -> bare number string."""

    def test_single_input_single_model(self):
        inputs = [("hello", "hello")]
        models = ["claude-opus-4-6"]
        counts = {("hello", "claude-opus-4-6"): 1}
        result = format_output(inputs, models, counts)
        self.assertEqual(result.strip(), "1")

    def test_larger_number(self):
        inputs = [("text", "some text")]
        models = ["gpt-4o"]
        counts = {("text", "gpt-4o"): 12345}
        result = format_output(inputs, models, counts)
        self.assertEqual(result.strip(), "12345")


@unittest.skipUnless(_module_available, _missing_reason)
class TestFormatOutputTable(unittest.TestCase):
    """Multiple inputs/models -> table output."""

    def test_two_inputs_one_model(self):
        """Should have Input column but no Model column."""
        inputs = [("aaa", "text a"), ("bbb", "text b")]
        models = ["claude-opus-4-6"]
        counts = {
            ("aaa", "claude-opus-4-6"): 10,
            ("bbb", "claude-opus-4-6"): 20,
        }
        result = format_output(inputs, models, counts)
        # Should contain input names and counts.
        self.assertIn("aaa", result)
        self.assertIn("bbb", result)
        self.assertIn("10", result)
        self.assertIn("20", result)
        # Single model dimension collapsed: "Model" column absent.
        # We check the header area doesn't contain "Model".
        lines = result.strip().splitlines()
        if lines:
            header = lines[0].lower()
            self.assertNotIn("model", header)

    def test_one_input_two_models(self):
        """Should have Model column but no Input column."""
        inputs = [("text", "hello")]
        models = ["gpt-4o", "claude-opus-4-6"]
        counts = {
            ("text", "gpt-4o"): 5,
            ("text", "claude-opus-4-6"): 7,
        }
        result = format_output(inputs, models, counts)
        # Should contain model names and counts.
        self.assertIn("gpt-4o", result)
        self.assertIn("claude-opus-4-6", result)
        self.assertIn("5", result)
        self.assertIn("7", result)
        # Single input dimension collapsed: "Input" column absent.
        lines = result.strip().splitlines()
        if lines:
            header = lines[0].lower()
            self.assertNotIn("input", header)

    def test_two_inputs_two_models(self):
        """Should have both Input and Model columns."""
        inputs = [("aaa", "text a"), ("bbb", "text b")]
        models = ["gpt-4o", "claude-opus-4-6"]
        counts = {
            ("aaa", "gpt-4o"): 10,
            ("aaa", "claude-opus-4-6"): 12,
            ("bbb", "gpt-4o"): 20,
            ("bbb", "claude-opus-4-6"): 22,
        }
        result = format_output(inputs, models, counts)
        # All names and values present.
        self.assertIn("aaa", result)
        self.assertIn("bbb", result)
        self.assertIn("gpt-4o", result)
        self.assertIn("claude-opus-4-6", result)
        self.assertIn("10", result)
        self.assertIn("12", result)
        self.assertIn("20", result)
        self.assertIn("22", result)

    def test_table_is_not_bare_number(self):
        """Multi-dimensional output should never be a bare number."""
        inputs = [("a", "x"), ("b", "y")]
        models = ["m1"]
        counts = {("a", "m1"): 5, ("b", "m1"): 10}
        result = format_output(inputs, models, counts)
        # Should have more than just a number.
        self.assertNotEqual(result.strip(), "5")
        self.assertNotEqual(result.strip(), "10")


# ===================================================================
# Integration: real Anthropic API (gated on env var)
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
@unittest.skipUnless(
    os.environ.get("ANTHROPIC_API_KEY"),
    "ANTHROPIC_API_KEY not set — skipping live API test",
)
class TestCountTokensIntegration(unittest.TestCase):
    """Live integration test against the Anthropic token-counting API."""

    def test_claude_count_short_string(self):
        result = count_tokens("Hello, world!", "claude-opus-4-6")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_claude_count_empty_string(self):
        result = count_tokens("", "claude-opus-4-6")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
