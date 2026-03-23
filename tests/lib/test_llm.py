"""Tests for plugin/lib/llm.py — shared LLM client logic."""

import importlib.util
import os
import pathlib
import sys
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Pre-register lib.apikey so llm.py's import works outside the plugin venv.
# ---------------------------------------------------------------------------
_lib_root = pathlib.Path(__file__).resolve().parents[2] / "plugin" / "lib"

_apikey_path = str(_lib_root / "apikey.py")
_apikey_spec = importlib.util.spec_from_file_location("lib.apikey", _apikey_path)
if _apikey_spec and _apikey_spec.loader:
    _apikey_mod = importlib.util.module_from_spec(_apikey_spec)
    _apikey_spec.loader.exec_module(_apikey_mod)
    sys.modules["lib.apikey"] = _apikey_mod

# ---------------------------------------------------------------------------
# Load the module under test.
# ---------------------------------------------------------------------------
_MODULE_PATH = str(_lib_root / "llm.py")
_spec = importlib.util.spec_from_file_location("lib.llm", _MODULE_PATH)

_module_available = _spec is not None and _spec.loader is not None
_missing_reason = "llm.py not loadable"

if _module_available:
    try:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
    except BaseException as _exc:
        _module_available = False
        _missing_reason = f"llm.py failed to load: {_exc}"

_REQUIRED_FUNCS = ["resolve_provider", "create_client", "invoke"]
if _module_available:
    for _fn_name in _REQUIRED_FUNCS:
        if not hasattr(_mod, _fn_name):
            _module_available = False
            _missing_reason = f"llm.py is missing function: {_fn_name}"
            break

if _module_available:
    resolve_provider = _mod.resolve_provider
    create_client = _mod.create_client
    invoke = _mod.invoke


# ===================================================================
# resolve_provider
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestResolveProviderClaude(unittest.TestCase):
    """claude* models route to anthropic."""

    def test_claude_sonnet(self):
        self.assertEqual(resolve_provider("claude-sonnet-4-6"), "anthropic")

    def test_claude_opus(self):
        self.assertEqual(resolve_provider("claude-opus-4-6"), "anthropic")

    def test_claude_bare(self):
        self.assertEqual(resolve_provider("claude-3-haiku"), "anthropic")


@unittest.skipUnless(_module_available, _missing_reason)
class TestResolveProviderGemini(unittest.TestCase):
    """gemini* models route to gemini."""

    def test_gemini_pro(self):
        self.assertEqual(resolve_provider("gemini-pro"), "gemini")

    def test_gemini_2(self):
        self.assertEqual(resolve_provider("gemini-2.0-flash"), "gemini")


@unittest.skipUnless(_module_available, _missing_reason)
class TestResolveProviderOpenAI(unittest.TestCase):
    """Everything else routes to openai."""

    def test_gpt_4o(self):
        self.assertEqual(resolve_provider("gpt-4o"), "openai")

    def test_gpt_5_mini(self):
        self.assertEqual(resolve_provider("gpt-5-mini"), "openai")

    def test_arbitrary_model(self):
        self.assertEqual(resolve_provider("llama-3-70b"), "openai")

    def test_empty_string(self):
        self.assertEqual(resolve_provider(""), "openai")


# ===================================================================
# create_client
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestCreateClientAnthropicMocked(unittest.TestCase):
    """Anthropic client creation with mocked SDK."""

    def test_creates_anthropic_client(self):
        mock_cls = MagicMock()
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            with patch.dict(sys.modules, {"anthropic": MagicMock(Anthropic=mock_cls)}):
                # Clear any cached clients
                if hasattr(_mod, "_clients"):
                    _mod._clients.clear()
                client = create_client("anthropic")
                mock_cls.assert_called_once()

    def test_anthropic_missing_key_exits(self):
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            if hasattr(_mod, "_clients"):
                _mod._clients.clear()
            with self.assertRaises(SystemExit) as ctx:
                create_client("anthropic")
            self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))


@unittest.skipUnless(_module_available, _missing_reason)
class TestCreateClientOpenAIMocked(unittest.TestCase):
    """OpenAI client creation with mocked SDK."""

    def test_creates_openai_client(self):
        mock_cls = MagicMock()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch.dict(sys.modules, {"openai": MagicMock(OpenAI=mock_cls)}):
                if hasattr(_mod, "_clients"):
                    _mod._clients.clear()
                client = create_client("openai")
                mock_cls.assert_called_once()


@unittest.skipUnless(_module_available, _missing_reason)
class TestCreateClientGeminiMocked(unittest.TestCase):
    """Gemini uses OpenAI client with custom base URL."""

    def test_creates_gemini_client_via_openai(self):
        mock_cls = MagicMock()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gem-test"}):
            with patch.dict(sys.modules, {"openai": MagicMock(OpenAI=mock_cls)}):
                if hasattr(_mod, "_clients"):
                    _mod._clients.clear()
                client = create_client("gemini")
                mock_cls.assert_called_once()
                # Should pass base_url for Gemini's OpenAI-compatible endpoint
                call_kwargs = mock_cls.call_args
                self.assertIn("base_url", call_kwargs.kwargs)


# ===================================================================
# invoke
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestInvokeAnthropicMocked(unittest.TestCase):
    """invoke() with an Anthropic model returns normalized result."""

    def test_returns_normalized_result(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello from Claude")]
        mock_response.model = "claude-sonnet-4-6"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        mock_response.stop_reason = "end_turn"

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        if hasattr(_mod, "_clients"):
            _mod._clients.clear()
            _mod._clients["anthropic"] = mock_client

        result = invoke(
            messages={"system": "Be helpful", "user": "Hi"},
            model="claude-sonnet-4-6",
            temperature=0.0,
            max_tokens=4096,
        )

        self.assertIn("response", result)
        self.assertIn("model", result)
        self.assertIn("input_tokens", result)
        self.assertIn("output_tokens", result)
        self.assertIn("latency_ms", result)
        self.assertIn("finish_reason", result)
        self.assertEqual(result["response"], "Hello from Claude")
        self.assertIsInstance(result["latency_ms"], int)


@unittest.skipUnless(_module_available, _missing_reason)
class TestInvokeOpenAIMocked(unittest.TestCase):
    """invoke() with an OpenAI model returns normalized result."""

    def test_returns_normalized_result(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from GPT"
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4o"
        mock_response.usage.prompt_tokens = 8
        mock_response.usage.completion_tokens = 4

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        if hasattr(_mod, "_clients"):
            _mod._clients.clear()
            _mod._clients["openai"] = mock_client

        result = invoke(
            messages={"system": "Be helpful", "user": "Hi"},
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4096,
        )

        self.assertIn("response", result)
        self.assertEqual(result["response"], "Hello from GPT")
        self.assertIn("input_tokens", result)
        self.assertIn("output_tokens", result)
        self.assertIn("latency_ms", result)
        self.assertIn("finish_reason", result)


if __name__ == "__main__":
    unittest.main()
