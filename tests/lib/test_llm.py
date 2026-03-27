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

_REQUIRED_FUNCS = ["resolve_provider", "create_client", "invoke", "Message", "validate_messages"]
if _module_available:
    for _fn_name in _REQUIRED_FUNCS:
        if not hasattr(_mod, _fn_name):
            _module_available = False
            _missing_reason = f"llm.py is missing: {_fn_name}"
            break

if _module_available:
    resolve_provider = _mod.resolve_provider
    create_client = _mod.create_client
    invoke = _mod.invoke
    Message = _mod.Message
    validate_messages = _mod.validate_messages


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
        self.assertEqual(resolve_provider("gpt-5.4-mini"), "openai")

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
            messages=[Message("system", "Be helpful"), Message("user", "Hi")],
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
            messages=[Message("system", "Be helpful"), Message("user", "Hi")],
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


# ===================================================================
# create_client — caching
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestCreateClientCaching(unittest.TestCase):
    """Calling create_client twice returns the same cached instance."""

    def test_same_client_returned(self):
        mock_cls = MagicMock()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch.dict(sys.modules, {"openai": MagicMock(OpenAI=mock_cls)}):
                if hasattr(_mod, "_clients"):
                    _mod._clients.clear()
                first = create_client("openai")
                second = create_client("openai")
                self.assertIs(first, second)
                # Constructor called only once.
                mock_cls.assert_called_once()


# ===================================================================
# invoke — user-only messages (no system prompt)
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestInvokeAnthropicUserOnly(unittest.TestCase):
    """invoke() with only a user message, no system prompt."""

    def test_user_only_anthropic(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.model = "claude-sonnet-4-6"
        mock_response.usage.input_tokens = 5
        mock_response.usage.output_tokens = 2
        mock_response.stop_reason = "end_turn"

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        if hasattr(_mod, "_clients"):
            _mod._clients.clear()
            _mod._clients["anthropic"] = mock_client

        result = invoke(
            messages=[Message("user", "Hi")],
            model="claude-sonnet-4-6",
            temperature=0.0,
            max_tokens=4096,
        )

        self.assertEqual(result["response"], "Response")
        # Should not pass system kwarg when absent.
        call_kwargs = mock_client.messages.create.call_args.kwargs
        self.assertNotIn("system", call_kwargs)


@unittest.skipUnless(_module_available, _missing_reason)
class TestInvokeOpenAIUserOnly(unittest.TestCase):
    """invoke() with only a user message via OpenAI path."""

    def test_user_only_openai(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "Response"
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4o"
        mock_response.usage.prompt_tokens = 3
        mock_response.usage.completion_tokens = 1

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        if hasattr(_mod, "_clients"):
            _mod._clients.clear()
            _mod._clients["openai"] = mock_client

        result = invoke(
            messages=[Message("user", "Hi")],
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4096,
        )

        self.assertEqual(result["response"], "Response")
        # Should not include a system message in the messages list.
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        messages_sent = call_kwargs["messages"]
        roles = [m["role"] for m in messages_sent]
        self.assertNotIn("system", roles)


# ===================================================================
# invoke — Gemini model
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestInvokeGeminiMocked(unittest.TestCase):
    """invoke() with a Gemini model returns normalized result."""

    def test_returns_normalized_result(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from Gemini"
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gemini-pro"
        mock_response.usage.prompt_tokens = 6
        mock_response.usage.completion_tokens = 3

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        if hasattr(_mod, "_clients"):
            _mod._clients.clear()
            _mod._clients["gemini"] = mock_client

        result = invoke(
            messages=[Message("system", "Be helpful"), Message("user", "Hi")],
            model="gemini-pro",
            temperature=0.5,
            max_tokens=4096,
        )

        self.assertEqual(result["response"], "Hello from Gemini")
        self.assertIn("input_tokens", result)
        self.assertIn("output_tokens", result)
        self.assertIn("latency_ms", result)
        self.assertIn("finish_reason", result)


# ===================================================================
# validate_messages
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestValidateMessagesValid(unittest.TestCase):
    """Valid message sequences pass without error."""

    def test_user_only(self):
        validate_messages([Message("user", "Hi")])

    def test_system_user(self):
        validate_messages([Message("system", "Be helpful"), Message("user", "Hi")])

    def test_multi_turn(self):
        validate_messages([
            Message("system", "Be helpful"),
            Message("user", "Q1"),
            Message("assistant", "A1"),
            Message("user", "Q2"),
        ])

    def test_multi_turn_no_system(self):
        validate_messages([
            Message("user", "Q1"),
            Message("assistant", "A1"),
            Message("user", "Q2"),
        ])


@unittest.skipUnless(_module_available, _missing_reason)
class TestValidateMessagesInvalid(unittest.TestCase):
    """Invalid message sequences raise SystemExit."""

    def test_empty(self):
        with self.assertRaises(SystemExit):
            validate_messages([])

    def test_system_only(self):
        with self.assertRaises(SystemExit):
            validate_messages([Message("system", "sys")])

    def test_starts_with_assistant(self):
        with self.assertRaises(SystemExit):
            validate_messages([Message("assistant", "A"), Message("user", "Q")])

    def test_ends_with_assistant(self):
        with self.assertRaises(SystemExit):
            validate_messages([Message("user", "Q"), Message("assistant", "A")])

    def test_double_user(self):
        """After joining, two consecutive user messages should not exist."""
        with self.assertRaises(SystemExit):
            validate_messages([
                Message("user", "Q1"),
                Message("user", "Q2"),
            ])

    def test_double_assistant(self):
        with self.assertRaises(SystemExit):
            validate_messages([
                Message("user", "Q"),
                Message("assistant", "A1"),
                Message("assistant", "A2"),
                Message("user", "Q2"),
            ])

    def test_assistant_after_system(self):
        with self.assertRaises(SystemExit):
            validate_messages([
                Message("system", "sys"),
                Message("assistant", "A"),
                Message("user", "Q"),
            ])


# ===================================================================
# invoke — multi-turn messages
# ===================================================================

@unittest.skipUnless(_module_available, _missing_reason)
class TestInvokeMultiTurnAnthropicMocked(unittest.TestCase):
    """invoke() passes multi-turn messages correctly to Anthropic."""

    def test_multi_turn_passes_all_messages(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Final answer")]
        mock_response.model = "claude-sonnet-4-6"
        mock_response.usage.input_tokens = 20
        mock_response.usage.output_tokens = 5
        mock_response.stop_reason = "end_turn"

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        if hasattr(_mod, "_clients"):
            _mod._clients.clear()
            _mod._clients["anthropic"] = mock_client

        result = invoke(
            messages=[
                Message("system", "Be helpful"),
                Message("user", "Q1"),
                Message("assistant", "A1"),
                Message("user", "Q2"),
            ],
            model="claude-sonnet-4-6",
            temperature=0.0,
            max_tokens=4096,
        )

        self.assertEqual(result["response"], "Final answer")
        call_kwargs = mock_client.messages.create.call_args.kwargs
        # System extracted to top-level kwarg.
        self.assertEqual(call_kwargs["system"], "Be helpful")
        # Messages should contain user/assistant turns only.
        api_messages = call_kwargs["messages"]
        self.assertEqual(len(api_messages), 3)
        self.assertEqual(api_messages[0]["role"], "user")
        self.assertEqual(api_messages[1]["role"], "assistant")
        self.assertEqual(api_messages[2]["role"], "user")


@unittest.skipUnless(_module_available, _missing_reason)
class TestInvokeMultiTurnOpenAIMocked(unittest.TestCase):
    """invoke() passes multi-turn messages correctly to OpenAI."""

    def test_multi_turn_passes_all_messages(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "Final answer"
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4o"
        mock_response.usage.prompt_tokens = 20
        mock_response.usage.completion_tokens = 5

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        if hasattr(_mod, "_clients"):
            _mod._clients.clear()
            _mod._clients["openai"] = mock_client

        result = invoke(
            messages=[
                Message("system", "Be helpful"),
                Message("user", "Q1"),
                Message("assistant", "A1"),
                Message("user", "Q2"),
            ],
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4096,
        )

        self.assertEqual(result["response"], "Final answer")
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        # OpenAI gets system in the messages array.
        api_messages = call_kwargs["messages"]
        self.assertEqual(len(api_messages), 4)
        roles = [m["role"] for m in api_messages]
        self.assertEqual(roles, ["system", "user", "assistant", "user"])


if __name__ == "__main__":
    unittest.main()
