"""Tests for plugin/skills/invoke-llm/scripts/invoke.py"""

import importlib.util
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Pre-register lib.* modules so invoke.py's imports work outside plugin venv.
# ---------------------------------------------------------------------------
_lib_root = pathlib.Path(__file__).resolve().parents[3] / "plugin" / "lib"
for _lib_name, _lib_file in [
    ("lib.apikey", "apikey.py"),
    ("lib.format", "format.py"),
    ("lib.llm", "llm.py"),
]:
    _lib_path = str(_lib_root / _lib_file)
    _lib_spec = importlib.util.spec_from_file_location(_lib_name, _lib_path)
    if _lib_spec and _lib_spec.loader:
        _lib_mod = importlib.util.module_from_spec(_lib_spec)
        _lib_spec.loader.exec_module(_lib_mod)
        sys.modules[_lib_name] = _lib_mod

# ---------------------------------------------------------------------------
# Load the module under test.
# ---------------------------------------------------------------------------
_MODULE_PATH = str(
    pathlib.Path(__file__).resolve().parents[3]
    / "plugin"
    / "skills"
    / "invoke-llm"
    / "scripts"
    / "invoke.py"
)
_spec = importlib.util.spec_from_file_location("invoke", _MODULE_PATH)

_module_available = _spec is not None and _spec.loader is not None
_missing_reason = "invoke.py not loadable"

if _module_available:
    try:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
    except BaseException as _exc:
        _module_available = False
        _missing_reason = f"invoke.py failed to load: {_exc}"

_REQUIRED_FUNCS = [
    "parse_args", "build_prompt", "load_config", "expand_matrix",
    "substitute_vars", "format_result", "dry_run",
]
if _module_available:
    for _fn_name in _REQUIRED_FUNCS:
        if not hasattr(_mod, _fn_name):
            _module_available = False
            _missing_reason = f"invoke.py is missing function: {_fn_name}"
            break

if _module_available:
    parse_args = _mod.parse_args
    build_prompt = _mod.build_prompt
    load_config = _mod.load_config
    expand_matrix = _mod.expand_matrix
    substitute_vars = _mod.substitute_vars
    format_result = _mod.format_result
    dry_run = _mod.dry_run


# ===================================================================
# parse_args
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsSingleShot(unittest.TestCase):
    """Single-shot mode flags."""

    def test_positional_as_user_prompt(self):
        ns = parse_args(["hello world"])
        # Positional is shorthand for -u.
        prompt = build_prompt(ns)
        self.assertIn("hello world", prompt.get("user", ""))

    def test_u_flag(self):
        ns = parse_args(["-u", "prompt text"])
        prompt = build_prompt(ns)
        self.assertIn("prompt text", prompt["user"])

    def test_s_flag(self):
        ns = parse_args(["-s", "system text", "-u", "user text"])
        prompt = build_prompt(ns)
        self.assertIn("system text", prompt["system"])

    def test_default_model(self):
        ns = parse_args(["-u", "hi"])
        self.assertEqual(ns.m, "claude-sonnet-4-6")

    def test_custom_model(self):
        ns = parse_args(["-m", "gpt-4o", "-u", "hi"])
        self.assertEqual(ns.m, "gpt-4o")

    def test_default_max_tokens(self):
        ns = parse_args(["-u", "hi"])
        self.assertEqual(ns.max_tokens, 4096)

    def test_custom_max_tokens(self):
        ns = parse_args(["--max-tokens", "1024", "-u", "hi"])
        self.assertEqual(ns.max_tokens, 1024)


@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsMutualExclusion(unittest.TestCase):
    """Mutual exclusion between modes and output formats."""

    def test_json_and_toml_mutually_exclusive(self):
        with self.assertRaises(SystemExit):
            parse_args(["--json", "--toml", "-u", "hi"])

    def test_config_and_singleshot_mutually_exclusive(self):
        """Using -c with single-shot prompt flags should error."""
        with self.assertRaises(SystemExit):
            parse_args(["-c", "run.toml", "-u", "hi"])

    def test_dry_run_requires_config(self):
        """--dry-run without -c should error."""
        with self.assertRaises(SystemExit):
            parse_args(["--dry-run", "-u", "hi"])


@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsFileInputs(unittest.TestCase):
    """File-based prompt inputs."""

    def test_U_flag_reads_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("file user prompt")
            fpath = f.name
        try:
            ns = parse_args(["-U", fpath])
            prompt = build_prompt(ns)
            self.assertIn("file user prompt", prompt["user"])
        finally:
            os.unlink(fpath)

    def test_S_flag_reads_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("file system prompt")
            fpath = f.name
        try:
            ns = parse_args(["-S", fpath, "-u", "user text"])
            prompt = build_prompt(ns)
            self.assertIn("file system prompt", prompt["system"])
        finally:
            os.unlink(fpath)


@unittest.skipUnless(_module_available, _missing_reason)
class TestParseArgsOutputFlags(unittest.TestCase):
    """Output-related flags."""

    def test_q_flag(self):
        ns = parse_args(["-q", "-u", "hi"])
        self.assertTrue(ns.q)

    def test_json_flag(self):
        ns = parse_args(["--json", "-u", "hi"])
        self.assertTrue(ns.json)

    def test_toml_flag(self):
        ns = parse_args(["--toml", "-u", "hi"])
        self.assertTrue(ns.toml)

    def test_o_flag(self):
        ns = parse_args(["-o", "out.txt", "-u", "hi"])
        self.assertEqual(ns.o, "out.txt")


# ===================================================================
# build_prompt — insertion order
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestBuildPromptOrder(unittest.TestCase):
    """Prompts are concatenated in command-line order, joined by separator."""

    def test_multiple_user_prompts_joined(self):
        ns = parse_args(["-u", "first", "-u", "second"])
        prompt = build_prompt(ns)
        user = prompt["user"]
        # Both present, first before second.
        idx1 = user.index("first")
        idx2 = user.index("second")
        self.assertLess(idx1, idx2)

    def test_default_separator(self):
        ns = parse_args(["-u", "aaa", "-u", "bbb"])
        prompt = build_prompt(ns)
        # Default separator is "\n\n".
        self.assertIn("aaa\n\nbbb", prompt["user"])

    def test_positional_and_u_combined(self):
        """Positional is shorthand for -u, order preserved."""
        ns = parse_args(["positional", "-u", "flagged"])
        prompt = build_prompt(ns)
        user = prompt["user"]
        idx1 = user.index("positional")
        idx2 = user.index("flagged")
        self.assertLess(idx1, idx2)

    def test_system_only_no_user(self):
        """System prompt without user prompt."""
        ns = parse_args(["-s", "sys only"])
        prompt = build_prompt(ns)
        self.assertIn("sys only", prompt.get("system", ""))
        # user may be empty or absent
        self.assertFalse(prompt.get("user", ""))

    def test_interleaved_file_and_inline_order(self):
        """File and inline inputs interleaved preserve command-line order."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("from file")
            fpath = f.name
        try:
            ns = parse_args(["-u", "first", "-U", fpath, "-u", "third"])
            prompt = build_prompt(ns)
            user = prompt["user"]
            idx1 = user.index("first")
            idx2 = user.index("from file")
            idx3 = user.index("third")
            self.assertLess(idx1, idx2)
            self.assertLess(idx2, idx3)
        finally:
            os.unlink(fpath)


# ===================================================================
# load_config
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestLoadConfig(unittest.TestCase):
    """TOML config parsing."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_toml(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _write_file(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_basic_config(self):
        self._write_file("prompt.md", "Hello")
        path = self._write_toml("run.toml", """\
[generation]
model = "claude-sonnet-4-6"
max_tokens = 4096

[[prompts]]
role = "user"
file = "prompt.md"
""")
        config = load_config(path)
        self.assertIn("generation", config)
        self.assertIn("prompts", config)

    def test_paths_resolve_relative_to_toml(self):
        """File paths in config resolve relative to the TOML file's parent."""
        self._write_file("my_prompt.md", "Hello from file")
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"

[[prompts]]
role = "user"
file = "my_prompt.md"
""")
        config = load_config(path)
        # The loaded config should have resolved the file path.
        prompts = config["prompts"]
        self.assertEqual(len(prompts), 1)
        # The file content or resolved path should reference the tmpdir.
        prompt_file = prompts[0].get("file")
        if isinstance(prompt_file, str):
            self.assertTrue(
                os.path.isabs(prompt_file),
                "File path should be resolved to absolute"
            )

    def test_vars_section(self):
        self._write_file("input.md", "var content")
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"

[vars]
input = "input.md"

[[prompts]]
role = "user"
prompt = "test"
""")
        config = load_config(path)
        self.assertIn("vars", config)

    def test_output_section(self):
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"

[output]
file = "results.jsonl"

[[prompts]]
role = "user"
prompt = "test"
""")
        config = load_config(path)
        self.assertIn("output", config)


# ===================================================================
# expand_matrix
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestExpandMatrix(unittest.TestCase):
    """Cartesian product of sweep dimensions."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_toml(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _write_file(self, name, content=""):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_scalar_config_one_run(self):
        """All scalars → 1 run."""
        self._write_file("p.md", "hello")
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"
temperature = 0.0

[[prompts]]
role = "user"
file = "p.md"
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 1)

    def test_two_models_three_temps(self):
        """2 models × 3 temps = 6 runs."""
        self._write_file("p.md", "hello")
        path = self._write_toml("run.toml", """\
[generation]
model = ["gpt-4o", "claude-sonnet-4-6"]
temperature = [0.0, 0.5, 1.0]

[[prompts]]
role = "user"
file = "p.md"
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 6)

    def test_prompt_file_sweep(self):
        """2 models × 2 prompt files = 4 runs."""
        self._write_file("a.md", "prompt a")
        self._write_file("b.md", "prompt b")
        path = self._write_toml("run.toml", """\
[generation]
model = ["gpt-4o", "claude-sonnet-4-6"]

[[prompts]]
role = "user"
file = ["a.md", "b.md"]
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 4)

    def test_full_matrix(self):
        """2 models × 3 temps × 2 system files = 12 runs (spec example)."""
        self._write_file("strict.md", "strict")
        self._write_file("relaxed.md", "relaxed")
        path = self._write_toml("run.toml", """\
[generation]
model = ["claude-sonnet-4-6", "gpt-5.4-mini"]
temperature = [0.0, 0.5, 1.0]

[[prompts]]
role = "system"
file = ["strict.md", "relaxed.md"]

[[prompts]]
role = "user"
prompt = "inline text"
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 12)

    def test_prompt_array_sweep(self):
        """Inline prompt array = sweep dimension. 2 prompts → 2 runs."""
        path = self._write_toml("run.toml", """\
[generation]
model = "claude-sonnet-4-6"

[[prompts]]
role = "user"
prompt = ["question one", "question two"]
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 2)
        # Each run should have a different user prompt.
        user_prompts = [run["messages"]["user"] for run in matrix]
        self.assertIn("question one", user_prompts)
        self.assertIn("question two", user_prompts)

    def test_prompt_array_with_model_sweep(self):
        """2 models × 3 inline prompts = 6 runs."""
        path = self._write_toml("run.toml", """\
[generation]
model = ["gpt-4o", "claude-sonnet-4-6"]

[[prompts]]
role = "user"
prompt = ["q1", "q2", "q3"]
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 6)

    def test_prompt_array_with_file_array(self):
        """2 system files × 2 inline user prompts = 4 runs."""
        self._write_file("a.md", "system a")
        self._write_file("b.md", "system b")
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"

[[prompts]]
role = "system"
file = ["a.md", "b.md"]

[[prompts]]
role = "user"
prompt = ["question one", "question two"]
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 4)


# ===================================================================
# substitute_vars
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestSubstituteVars(unittest.TestCase):
    """{{key}} replacement with [vars] content."""

    def test_single_substitution(self):
        result = substitute_vars("Hello {{name}}", {"name": "World"})
        self.assertEqual(result, "Hello World")

    def test_multiple_substitutions(self):
        result = substitute_vars(
            "{{a}} and {{b}}",
            {"a": "first", "b": "second"},
        )
        self.assertEqual(result, "first and second")

    def test_repeated_key(self):
        result = substitute_vars("{{x}} {{x}}", {"x": "val"})
        self.assertEqual(result, "val val")

    def test_missing_key_errors(self):
        """Reference to a missing var is an error."""
        with self.assertRaises((SystemExit, KeyError, ValueError)) as ctx:
            substitute_vars("Hello {{missing}}", {})
        # Error message should name the unresolved key.
        self.assertIn("missing", str(ctx.exception))

    def test_no_placeholders(self):
        result = substitute_vars("no placeholders here", {"key": "val"})
        self.assertEqual(result, "no placeholders here")


@unittest.skipUnless(_module_available, _missing_reason)
class TestSubstituteVarsEndToEnd(unittest.TestCase):
    """Variable substitution through the full config → expand_matrix pipeline."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_file(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _write_toml(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_vars_content_injected_into_prompt(self):
        """[vars] file content replaces {{key}} in prompts with substitute=true."""
        self._write_file("context.md", "important context here")
        self._write_file("template.md", "Given: {{input}}\nAnswer the question.")
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"

[vars]
input = "context.md"

[[prompts]]
role = "user"
file = "template.md"
substitute = true
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        self.assertEqual(len(matrix), 1)
        user_msg = matrix[0]["messages"]["user"]
        # The placeholder should be replaced with file content.
        self.assertIn("important context here", user_msg)
        self.assertNotIn("{{input}}", user_msg)


# ===================================================================
# format_result
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestFormatResultPlain(unittest.TestCase):
    """Plain text output (no --json or --toml)."""

    def test_plain_shows_response(self):
        result = {
            "response": "Hello",
            "model": "gpt-4o",
            "input_tokens": 5,
            "output_tokens": 1,
            "latency_ms": 100,
            "finish_reason": "stop",
        }
        output = format_result(result, fmt=None, quiet=False)
        self.assertIn("Hello", output)

    def test_plain_quiet_suppresses_response(self):
        result = {
            "response": "Hello",
            "model": "gpt-4o",
            "input_tokens": 5,
            "output_tokens": 1,
            "latency_ms": 100,
            "finish_reason": "stop",
        }
        output = format_result(result, fmt=None, quiet=True)
        # -q in plain mode suppresses output entirely.
        self.assertEqual(output.strip(), "")


@unittest.skipUnless(_module_available, _missing_reason)
class TestFormatResultJSON(unittest.TestCase):
    """JSONL output (--json)."""

    def test_json_contains_all_fields(self):
        result = {
            "response": "Hello",
            "model": "gpt-4o",
            "input_tokens": 5,
            "output_tokens": 1,
            "latency_ms": 100,
            "finish_reason": "stop",
        }
        output = format_result(result, fmt="json", quiet=False)
        parsed = json.loads(output)
        for key in ["response", "model", "input_tokens", "output_tokens",
                     "latency_ms", "finish_reason"]:
            self.assertIn(key, parsed)

    def test_json_quiet_omits_response(self):
        result = {
            "response": "Hello",
            "model": "gpt-4o",
            "input_tokens": 5,
            "output_tokens": 1,
            "latency_ms": 100,
            "finish_reason": "stop",
        }
        output = format_result(result, fmt="json", quiet=True)
        parsed = json.loads(output)
        self.assertNotIn("response", parsed)
        # Metadata still present.
        self.assertIn("model", parsed)
        self.assertIn("input_tokens", parsed)


@unittest.skipUnless(_module_available, _missing_reason)
class TestFormatResultTOML(unittest.TestCase):
    """TOML output (--toml)."""

    def test_toml_contains_fields(self):
        result = {
            "response": "Hello",
            "model": "gpt-4o",
            "input_tokens": 5,
            "output_tokens": 1,
            "latency_ms": 100,
            "finish_reason": "stop",
        }
        output = format_result(result, fmt="toml", quiet=False)
        # Should contain key-value pairs.
        self.assertIn("model", output)
        self.assertIn("gpt-4o", output)
        self.assertIn("response", output)

    def test_toml_quiet_omits_response(self):
        result = {
            "response": "Hello",
            "model": "gpt-4o",
            "input_tokens": 5,
            "output_tokens": 1,
            "latency_ms": 100,
            "finish_reason": "stop",
        }
        output = format_result(result, fmt="toml", quiet=True)
        self.assertNotIn("Hello", output)
        self.assertIn("model", output)


# ===================================================================
# dry_run
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestDryRun(unittest.TestCase):
    """--dry-run prints dimension summary and total count."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_toml(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _write_file(self, name, content=""):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_dry_run_shows_total(self):
        self._write_file("a.md", "a")
        self._write_file("b.md", "b")
        path = self._write_toml("run.toml", """\
[generation]
model = ["gpt-4o", "claude-sonnet-4-6"]
temperature = [0.0, 1.0]

[[prompts]]
role = "system"
file = ["a.md", "b.md"]

[[prompts]]
role = "user"
prompt = "test"
""")
        config = load_config(path)
        matrix = expand_matrix(config)

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            dry_run(matrix)
        output = buf.getvalue()
        # 2 models × 2 temps × 2 files = 8 runs
        self.assertIn("8", output)

    def test_dry_run_shows_dimensions(self):
        self._write_file("x.md", "x")
        path = self._write_toml("run.toml", """\
[generation]
model = ["gpt-4o", "claude-sonnet-4-6"]

[[prompts]]
role = "user"
file = "x.md"
""")
        config = load_config(path)
        matrix = expand_matrix(config)

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            dry_run(matrix)
        output = buf.getvalue()
        # Should mention the model dimension values.
        self.assertIn("gpt-4o", output)
        self.assertIn("claude-sonnet-4-6", output)


# ===================================================================
# Config-mode separator handling
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestConfigSeparator(unittest.TestCase):
    """Custom separators in [generation] and per-prompt overrides."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_file(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _write_toml(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_generation_separator_used(self):
        """[generation].separator overrides the default \\n\\n join."""
        self._write_file("a.md", "part a")
        self._write_file("b.md", "part b")
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"
separator = "\\n---\\n"

[[prompts]]
role = "user"
file = "a.md"

[[prompts]]
role = "user"
file = "b.md"
""")
        config = load_config(path)
        matrix = expand_matrix(config)
        user_msg = matrix[0]["messages"]["user"]
        self.assertIn("---", user_msg)
        self.assertIn("part a", user_msg)
        self.assertIn("part b", user_msg)


# ===================================================================
# Config-mode [output].file
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestConfigOutputFile(unittest.TestCase):
    """[output].file resolves relative to the TOML file's parent."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_toml(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_output_file_resolved_to_absolute(self):
        path = self._write_toml("run.toml", """\
[generation]
model = "gpt-4o"

[output]
file = "results.jsonl"

[[prompts]]
role = "user"
prompt = "test"
""")
        config = load_config(path)
        output_file = config["output"]["file"]
        self.assertTrue(
            os.path.isabs(output_file),
            "output.file should be resolved to absolute path"
        )
        # Should be under the TOML's parent directory.
        self.assertTrue(
            output_file.startswith(self.tmpdir),
            "output.file should resolve relative to TOML parent"
        )


if __name__ == "__main__":
    unittest.main()
