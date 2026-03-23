"""Tests for plugin/lib/apikey.py — API key validation."""

import importlib.util
import os
import pathlib
import unittest
from unittest.mock import patch

_MODULE_PATH = str(
    pathlib.Path(__file__).resolve().parents[2] / "plugin" / "lib" / "apikey.py"
)
_spec = importlib.util.spec_from_file_location("lib.apikey", _MODULE_PATH)

_module_available = _spec is not None and _spec.loader is not None
_missing_reason = "apikey.py not loadable"

if _module_available:
    try:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
    except BaseException as _exc:
        _module_available = False
        _missing_reason = f"apikey.py failed to load: {_exc}"

if _module_available:
    if not hasattr(_mod, "require_api_key"):
        _module_available = False
        _missing_reason = "apikey.py is missing function: require_api_key"

if _module_available:
    require_api_key = _mod.require_api_key


@unittest.skipUnless(_module_available, _missing_reason)
class TestRequireApiKeyPresent(unittest.TestCase):
    """When the key is set, return it."""

    def test_anthropic_key_returned(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-123"}):
            result = require_api_key("anthropic")
            self.assertEqual(result, "sk-test-123")

    def test_openai_key_returned(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-openai-abc"}):
            result = require_api_key("openai")
            self.assertEqual(result, "sk-openai-abc")


@unittest.skipUnless(_module_available, _missing_reason)
class TestRequireApiKeyMissing(unittest.TestCase):
    """When the key is unset, exit with a clear one-line message."""

    def test_anthropic_missing_exits(self):
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                require_api_key("anthropic")
            msg = str(ctx.exception)
            self.assertIn("ANTHROPIC_API_KEY", msg)

    def test_empty_string_treated_as_missing(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            with self.assertRaises(SystemExit) as ctx:
                require_api_key("anthropic")
            self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))


@unittest.skipUnless(_module_available, _missing_reason)
class TestRequireApiKeyUnknownProvider(unittest.TestCase):
    """Unknown provider names exit with a clear message."""

    def test_unknown_provider(self):
        with self.assertRaises(SystemExit) as ctx:
            require_api_key("nonexistent")
        self.assertIn("nonexistent", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
