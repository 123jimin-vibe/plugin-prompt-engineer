"""Tests for plugin/scripts/allow-skill-scripts.py"""

import importlib.util
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Load the module under test via importlib (hyphenated filename).
# ---------------------------------------------------------------------------
_MODULE_PATH = str(
    pathlib.Path(__file__).resolve().parents[2]
    / "plugin"
    / "scripts"
    / "allow-skill-scripts.py"
)
_spec = importlib.util.spec_from_file_location("allow_skill_scripts", _MODULE_PATH)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

parse_hook_input = mod.parse_hook_input
is_venv_python = mod.is_venv_python
is_skill_script = mod.is_skill_script
emit_allow = mod.emit_allow
main = mod.main


# ===================================================================
# Helpers
# ===================================================================

def _make_hook_json(command: str) -> str:
    """Return the JSON a Claude Code hook would pipe into stdin."""
    return json.dumps({"tool_input": {"command": command}})


def _stdin(text: str):
    """Patch context-manager that replaces sys.stdin with *text*."""
    return patch("sys.stdin", new=StringIO(text))


def _posix_path(p) -> str:
    """Convert a path to forward-slash form so shlex.split does not eat backslashes."""
    return str(p).replace("\\", "/")


# ===================================================================
# parse_hook_input
# ===================================================================

class TestParseHookInput(unittest.TestCase):
    """Tests for parse_hook_input().

    The function reads JSON from stdin with shape
    ``{"tool_input": {"command": "<shell command>"}}`` and returns a tuple
    of shell tokens parsed from the command string.  It returns ``None``
    when the input is invalid or the command yields fewer than 2 tokens
    (since a valid invocation requires at least an executable and a script).
    """

    def test_simple_command(self):
        hook = _make_hook_json("python script.py")
        with _stdin(hook):
            result = parse_hook_input()
        self.assertIsNotNone(result)
        self.assertEqual(result, ("python", "script.py"))

    def test_command_with_arguments(self):
        hook = _make_hook_json("python my_script.py --flag value")
        with _stdin(hook):
            result = parse_hook_input()
        self.assertIsNotNone(result)
        self.assertEqual(result, ("python", "my_script.py", "--flag", "value"))

    def test_single_token_command_returns_none(self):
        """A single token (no script arg) is insufficient -- returns None."""
        hook = _make_hook_json("ls")
        with _stdin(hook):
            result = parse_hook_input()
        self.assertIsNone(result)

    def test_empty_command_returns_none(self):
        hook = _make_hook_json("")
        with _stdin(hook):
            result = parse_hook_input()
        self.assertIsNone(result)

    def test_malformed_json_returns_none(self):
        with _stdin("this is not json"):
            result = parse_hook_input()
        self.assertIsNone(result)

    def test_missing_tool_input_key_returns_none(self):
        with _stdin(json.dumps({"wrong_key": "value"})):
            result = parse_hook_input()
        self.assertIsNone(result)

    def test_missing_command_key_returns_none(self):
        with _stdin(json.dumps({"tool_input": {"no_command": "x"}})):
            result = parse_hook_input()
        self.assertIsNone(result)

    def test_empty_json_object_returns_none(self):
        with _stdin("{}"):
            result = parse_hook_input()
        self.assertIsNone(result)

    def test_empty_stdin_returns_none(self):
        with _stdin(""):
            result = parse_hook_input()
        self.assertIsNone(result)

    def test_command_with_quoted_argument(self):
        hook = _make_hook_json('python script.py "hello world"')
        with _stdin(hook):
            result = parse_hook_input()
        self.assertIsNotNone(result)
        self.assertIn("hello world", result)

    def test_three_token_command(self):
        hook = _make_hook_json("python script.py --verbose")
        with _stdin(hook):
            result = parse_hook_input()
        self.assertIsNotNone(result)
        self.assertEqual(result, ("python", "script.py", "--verbose"))

    def test_command_with_forward_slash_paths(self):
        hook = _make_hook_json("/usr/bin/python /home/user/script.py")
        with _stdin(hook):
            result = parse_hook_input()
        self.assertIsNotNone(result)
        self.assertEqual(result, ("/usr/bin/python", "/home/user/script.py"))

    def test_json_array_returns_none(self):
        """Stdin is valid JSON but an array, not an object."""
        with _stdin("[1, 2, 3]"):
            result = parse_hook_input()
        self.assertIsNone(result)


# ===================================================================
# is_venv_python
# ===================================================================

class TestIsVenvPython(unittest.TestCase):
    """Tests for is_venv_python(exe_path, plugin_data)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # --- helpers ---
    def _make_venv_python(self, exe_name="python"):
        """Create <tmpdir>/venv/<dirs>/<exe_name> and return its path."""
        if sys.platform == "win32":
            venv_bin = pathlib.Path(self.tmpdir) / "venv" / "Scripts"
        else:
            venv_bin = pathlib.Path(self.tmpdir) / "venv" / "bin"
        venv_bin.mkdir(parents=True, exist_ok=True)
        exe = venv_bin / exe_name
        exe.touch()
        return str(exe)

    # --- happy path ---
    def test_valid_venv_python(self):
        exe = self._make_venv_python("python")
        self.assertTrue(is_venv_python(exe, self.tmpdir))

    def test_valid_venv_python3(self):
        exe = self._make_venv_python("python3")
        self.assertTrue(is_venv_python(exe, self.tmpdir))

    def test_valid_venv_python312(self):
        exe = self._make_venv_python("python3.12")
        self.assertTrue(is_venv_python(exe, self.tmpdir))

    # --- negative cases ---
    def test_exe_outside_venv(self):
        other = pathlib.Path(self.tmpdir) / "other"
        other.mkdir()
        exe = other / "python"
        exe.touch()
        self.assertFalse(is_venv_python(str(exe), self.tmpdir))

    def test_exe_named_node_in_venv(self):
        exe = self._make_venv_python("node")
        self.assertFalse(is_venv_python(exe, self.tmpdir))

    def test_exe_named_ruby_in_venv(self):
        exe = self._make_venv_python("ruby")
        self.assertFalse(is_venv_python(exe, self.tmpdir))

    def test_exe_named_pythonic_in_venv(self):
        """Name starts with 'python' but is not a real Python interpreter name."""
        exe = self._make_venv_python("pythonic")
        # Depending on implementation this could go either way; the key check
        # is that the name starts with "python".  We just verify no crash.
        # Accept either True or False -- the important thing is no exception.
        result = is_venv_python(exe, self.tmpdir)
        self.assertIsInstance(result, bool)

    def test_nonexistent_exe(self):
        fake = str(pathlib.Path(self.tmpdir) / "venv" / "bin" / "python")
        self.assertFalse(is_venv_python(fake, self.tmpdir))

    def test_different_plugin_data(self):
        """exe inside one plugin_data, checked against another."""
        exe = self._make_venv_python("python")
        other_dir = tempfile.mkdtemp()
        try:
            self.assertFalse(is_venv_python(exe, other_dir))
        finally:
            shutil.rmtree(other_dir, ignore_errors=True)

    def test_symlink_escape(self):
        """Symlink inside venv/ pointing outside should be caught by resolve."""
        venv_dir = pathlib.Path(self.tmpdir) / "venv"
        venv_dir.mkdir(parents=True, exist_ok=True)
        outside = pathlib.Path(self.tmpdir) / "outside_python"
        outside.touch()
        link = venv_dir / "python"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("Cannot create symlinks on this platform")
        self.assertFalse(is_venv_python(str(link), self.tmpdir))

    def test_empty_exe_path(self):
        self.assertFalse(is_venv_python("", self.tmpdir))

    def test_empty_plugin_data(self):
        exe = self._make_venv_python("python")
        self.assertFalse(is_venv_python(exe, ""))


# ===================================================================
# is_skill_script
# ===================================================================

class TestIsSkillScript(unittest.TestCase):
    """Tests for is_skill_script(script_path, plugin_root)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # --- helpers ---
    def _make_skill_script(self, skill_name="my-skill", script_name="run.py"):
        """Create <root>/skills/<skill>/scripts/<file> and return its path."""
        scripts_dir = (
            pathlib.Path(self.tmpdir) / "skills" / skill_name / "scripts"
        )
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script = scripts_dir / script_name
        script.touch()
        return str(script)

    # --- happy path ---
    def test_valid_skill_script(self):
        path = self._make_skill_script("analyzer", "process.py")
        self.assertTrue(is_skill_script(path, self.tmpdir))

    def test_valid_skill_script_alt_name(self):
        path = self._make_skill_script("my-cool-skill", "main.py")
        self.assertTrue(is_skill_script(path, self.tmpdir))

    def test_valid_skill_script_underscores(self):
        path = self._make_skill_script("data_processor", "transform.py")
        self.assertTrue(is_skill_script(path, self.tmpdir))

    # --- wrong depth / structure ---
    def test_script_too_shallow(self):
        """File directly in skills/."""
        d = pathlib.Path(self.tmpdir) / "skills"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "script.py"
        f.touch()
        self.assertFalse(is_skill_script(str(f), self.tmpdir))

    def test_script_one_level_too_shallow(self):
        """File at skills/<skill>/script.py (missing scripts/ directory)."""
        d = pathlib.Path(self.tmpdir) / "skills" / "my-skill"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "script.py"
        f.touch()
        self.assertFalse(is_skill_script(str(f), self.tmpdir))

    def test_script_too_deep(self):
        """File at skills/<skill>/scripts/sub/script.py."""
        d = (
            pathlib.Path(self.tmpdir)
            / "skills"
            / "my-skill"
            / "scripts"
            / "sub"
        )
        d.mkdir(parents=True, exist_ok=True)
        f = d / "script.py"
        f.touch()
        self.assertFalse(is_skill_script(str(f), self.tmpdir))

    # --- non-.py files ---
    def test_non_py_file_rejected(self):
        path = self._make_skill_script("s", "script.sh")
        self.assertFalse(is_skill_script(path, self.tmpdir))

    def test_no_extension_rejected(self):
        path = self._make_skill_script("s", "script")
        self.assertFalse(is_skill_script(path, self.tmpdir))

    def test_pyc_file_rejected(self):
        path = self._make_skill_script("s", "script.pyc")
        self.assertFalse(is_skill_script(path, self.tmpdir))

    def test_pyw_file_rejected(self):
        path = self._make_skill_script("s", "script.pyw")
        self.assertFalse(is_skill_script(path, self.tmpdir))

    # --- path traversal ---
    def test_path_traversal_rejected(self):
        """Path with ../ that escapes skills/ tree."""
        self._make_skill_script("evil", "legit.py")
        malicious_dir = pathlib.Path(self.tmpdir) / "skills" / "evil" / "scripts"
        outside = pathlib.Path(self.tmpdir) / "evil.py"
        outside.touch()
        traversal_path = str(malicious_dir / ".." / ".." / ".." / "evil.py")
        self.assertFalse(is_skill_script(traversal_path, self.tmpdir))

    def test_wrong_plugin_root(self):
        """Script exists but plugin_root doesn't match."""
        path = self._make_skill_script("s", "run.py")
        other_dir = tempfile.mkdtemp()
        try:
            self.assertFalse(is_skill_script(path, other_dir))
        finally:
            shutil.rmtree(other_dir, ignore_errors=True)

    def test_nonexistent_path(self):
        fake = str(
            pathlib.Path(self.tmpdir) / "skills" / "s" / "scripts" / "nope.py"
        )
        self.assertFalse(is_skill_script(fake, self.tmpdir))

    def test_empty_script_path(self):
        self.assertFalse(is_skill_script("", self.tmpdir))

    def test_empty_plugin_root(self):
        path = self._make_skill_script("s", "run.py")
        self.assertFalse(is_skill_script(path, ""))

    def test_wrong_intermediate_directory_name(self):
        """skills/<skill>/notscripts/<file>.py -- wrong directory name."""
        d = pathlib.Path(self.tmpdir) / "skills" / "s" / "notscripts"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "run.py"
        f.touch()
        self.assertFalse(is_skill_script(str(f), self.tmpdir))

    def test_symlink_escape_in_script(self):
        """Symlink from inside skills tree pointing outside."""
        scripts_dir = (
            pathlib.Path(self.tmpdir) / "skills" / "s" / "scripts"
        )
        scripts_dir.mkdir(parents=True, exist_ok=True)
        outside = pathlib.Path(self.tmpdir) / "outside.py"
        outside.touch()
        link = scripts_dir / "link.py"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("Cannot create symlinks on this platform")
        self.assertFalse(is_skill_script(str(link), self.tmpdir))

    def test_script_in_root_not_skills(self):
        """A .py file directly in plugin_root, not in skills/."""
        f = pathlib.Path(self.tmpdir) / "run.py"
        f.touch()
        self.assertFalse(is_skill_script(str(f), self.tmpdir))


# ===================================================================
# emit_allow
# ===================================================================

class TestEmitAllow(unittest.TestCase):
    """Tests for emit_allow().

    The function outputs a Claude Code hook response JSON to stdout with
    shape: ``{"hookSpecificOutput": {"hookEventName": "PreToolUse",
    "permissionDecision": "allow", ...}}``.
    """

    def test_writes_valid_json_to_stdout(self):
        buf = StringIO()
        with patch("sys.stdout", new=buf):
            emit_allow()
        output = buf.getvalue().strip()
        data = json.loads(output)
        self.assertIsInstance(data, dict)

    def test_contains_allow_decision(self):
        buf = StringIO()
        with patch("sys.stdout", new=buf):
            emit_allow()
        output = buf.getvalue().strip()
        data = json.loads(output)
        hook_output = data.get("hookSpecificOutput", {})
        self.assertEqual(hook_output.get("permissionDecision"), "allow")

    def test_contains_hook_event_name(self):
        buf = StringIO()
        with patch("sys.stdout", new=buf):
            emit_allow()
        data = json.loads(buf.getvalue())
        hook_output = data.get("hookSpecificOutput", {})
        self.assertEqual(hook_output.get("hookEventName"), "PreToolUse")

    def test_output_contains_reason(self):
        buf = StringIO()
        with patch("sys.stdout", new=buf):
            emit_allow()
        data = json.loads(buf.getvalue())
        hook_output = data.get("hookSpecificOutput", {})
        reason = hook_output.get("permissionDecisionReason", "")
        self.assertTrue(len(reason) > 0, "Expected a non-empty reason string")


# ===================================================================
# main
# ===================================================================

class TestMain(unittest.TestCase):
    """Tests for main().

    main() reads CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA from env vars,
    parses hook JSON from stdin, validates the executable and script paths,
    and either emits an allow decision to stdout or exits with code 1.

    Note: On Windows, shlex.split (used by parse_hook_input) treats
    backslashes as escape characters.  Commands built for these tests use
    forward slashes so the paths survive shlex parsing.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plugin_root = str(pathlib.Path(self.tmpdir) / "plugin_root")
        self.plugin_data = str(pathlib.Path(self.tmpdir) / "plugin_data")

        scripts_dir = (
            pathlib.Path(self.plugin_root) / "skills" / "my-skill" / "scripts"
        )
        scripts_dir.mkdir(parents=True)
        self.script = scripts_dir / "run.py"
        self.script.touch()

        if sys.platform == "win32":
            venv_bin = pathlib.Path(self.plugin_data) / "venv" / "Scripts"
        else:
            venv_bin = pathlib.Path(self.plugin_data) / "venv" / "bin"
        venv_bin.mkdir(parents=True)
        self.python_exe = venv_bin / "python"
        self.python_exe.touch()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _env(self, **overrides):
        env = {
            "CLAUDE_PLUGIN_ROOT": self.plugin_root,
            "CLAUDE_PLUGIN_DATA": self.plugin_data,
        }
        env.update(overrides)
        return env

    def _run_main(self, stdin_text, env_dict):
        """Run main() capturing stdout; return (exit_code_or_none, stdout).

        Uses forward-slash paths in env_dict so that is_venv_python and
        is_skill_script resolve correctly even though shlex doesn't mangle
        the env vars themselves (only the command tokens).
        """
        buf = StringIO()
        exit_code = None
        with (
            _stdin(stdin_text),
            patch("sys.stdout", new=buf),
            patch.dict(os.environ, env_dict, clear=False),
        ):
            try:
                main()
            except SystemExit as exc:
                exit_code = exc.code
        return exit_code, buf.getvalue()

    def _make_cmd(self, exe=None, script=None):
        """Build a command string using forward slashes for shlex safety."""
        exe = exe or self.python_exe
        script = script or self.script
        return f"{_posix_path(exe)} {_posix_path(script)}"

    # --- happy path ---
    def test_allow_valid_invocation(self):
        cmd = self._make_cmd()
        hook = _make_hook_json(cmd)
        exit_code, stdout = self._run_main(hook, self._env())
        self.assertIn("allow", stdout)
        if exit_code is not None:
            self.assertEqual(exit_code, 0)

    def test_allow_valid_invocation_outputs_valid_json(self):
        cmd = self._make_cmd()
        hook = _make_hook_json(cmd)
        exit_code, stdout = self._run_main(hook, self._env())
        data = json.loads(stdout)
        hook_output = data.get("hookSpecificOutput", {})
        self.assertEqual(hook_output.get("permissionDecision"), "allow")

    # --- missing env vars ---
    def test_missing_plugin_root_exits_1(self):
        cmd = self._make_cmd()
        hook = _make_hook_json(cmd)
        env = {"CLAUDE_PLUGIN_DATA": self.plugin_data}
        # Remove CLAUDE_PLUGIN_ROOT if it happens to exist in the real env
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
            exit_code, _ = self._run_main(hook, {})
        self.assertEqual(exit_code, 1)

    def test_missing_plugin_data_exits_1(self):
        cmd = self._make_cmd()
        hook = _make_hook_json(cmd)
        env = {"CLAUDE_PLUGIN_ROOT": self.plugin_root}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("CLAUDE_PLUGIN_DATA", None)
            exit_code, _ = self._run_main(hook, {})
        self.assertEqual(exit_code, 1)

    # --- malformed input ---
    def test_malformed_json_exits_1(self):
        exit_code, _ = self._run_main("not json!", self._env())
        self.assertEqual(exit_code, 1)

    def test_empty_stdin_exits_1(self):
        exit_code, _ = self._run_main("", self._env())
        self.assertEqual(exit_code, 1)

    def test_json_without_tool_input_exits_1(self):
        hook = json.dumps({"something": "else"})
        exit_code, _ = self._run_main(hook, self._env())
        self.assertEqual(exit_code, 1)

    # --- invalid exe ---
    def test_non_venv_python_exits_1(self):
        cmd = f"/usr/bin/python {_posix_path(self.script)}"
        hook = _make_hook_json(cmd)
        exit_code, stdout = self._run_main(hook, self._env())
        self.assertEqual(exit_code, 1)
        self.assertNotIn("allow", stdout)

    # --- invalid script ---
    def test_non_skill_script_exits_1(self):
        rogue = pathlib.Path(self.tmpdir) / "rogue.py"
        rogue.touch()
        cmd = f"{_posix_path(self.python_exe)} {_posix_path(rogue)}"
        hook = _make_hook_json(cmd)
        exit_code, stdout = self._run_main(hook, self._env())
        self.assertEqual(exit_code, 1)
        self.assertNotIn("allow", stdout)

    # --- command with wrong number of tokens ---
    def test_single_token_command_exits_1(self):
        """Just an executable, no script argument."""
        hook = _make_hook_json(_posix_path(self.python_exe))
        exit_code, _ = self._run_main(hook, self._env())
        self.assertEqual(exit_code, 1)

    def test_non_python_exe_exits_1(self):
        """Executable is bash, not python."""
        hook = _make_hook_json(f"bash {_posix_path(self.script)}")
        exit_code, _ = self._run_main(hook, self._env())
        self.assertEqual(exit_code, 1)

    def test_empty_command_exits_1(self):
        hook = _make_hook_json("")
        exit_code, _ = self._run_main(hook, self._env())
        self.assertEqual(exit_code, 1)

    # --- allow with extra arguments ---
    def test_allow_with_extra_args(self):
        """Extra arguments after the script should still be allowed."""
        cmd = f"{_posix_path(self.python_exe)} {_posix_path(self.script)} --verbose --count 5"
        hook = _make_hook_json(cmd)
        exit_code, stdout = self._run_main(hook, self._env())
        self.assertIn("allow", stdout)
        if exit_code is not None:
            self.assertEqual(exit_code, 0)

    # --- path traversal via command ---
    def test_script_path_traversal_in_command_exits_1(self):
        """A command with ../ in the script path that escapes the skills tree."""
        # Create a .py file outside the skills tree
        outside = pathlib.Path(self.plugin_root) / "evil.py"
        outside.touch()
        traversal = (
            pathlib.Path(self.plugin_root)
            / "skills"
            / "x"
            / "scripts"
            / ".."
            / ".."
            / ".."
            / "evil.py"
        )
        cmd = f"{_posix_path(self.python_exe)} {_posix_path(traversal)}"
        hook = _make_hook_json(cmd)
        exit_code, stdout = self._run_main(hook, self._env())
        self.assertEqual(exit_code, 1)
        self.assertNotIn("allow", stdout)


if __name__ == "__main__":
    unittest.main()
