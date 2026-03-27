"""Shared LLM client logic — provider routing, client creation, unified invoke."""

import time
from dataclasses import dataclass

from lib.apikey import require_api_key


@dataclass(frozen=True, slots=True)
class Message:
    """A single message in a conversation."""

    role: str  # "system", "user", or "assistant"
    content: str


def validate_messages(messages: list[Message]) -> None:
    """Enforce ``system? (user assistant)* user`` sequence.

    Raises ``SystemExit`` with a descriptive error on violation.
    Call this **after** consecutive same-role entries have been joined.
    """
    if not messages:
        raise SystemExit("No messages provided.")

    idx = 0

    # Optional leading system message.
    if messages[idx].role == "system":
        idx += 1

    if idx >= len(messages):
        raise SystemExit("Messages contain only a system prompt — at least one user message is required.")

    # Remaining must alternate user/assistant, starting and ending with user.
    if messages[idx].role != "user":
        raise SystemExit(
            f"Expected user message at position {idx}, got {messages[idx].role!r}."
        )

    for i in range(idx, len(messages)):
        expected = "user" if (i - idx) % 2 == 0 else "assistant"
        actual = messages[i].role
        if actual != expected:
            raise SystemExit(
                f"Expected {expected!r} message at position {i}, got {actual!r}."
            )

    if messages[-1].role != "user":
        raise SystemExit(
            f"Messages must end with a user message, got {messages[-1].role!r}."
        )

_clients: dict = {}

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def resolve_provider(model: str) -> str:
    """Return provider name for *model*: anthropic, gemini, or openai."""
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith("gemini"):
        return "gemini"
    return "openai"


def create_client(provider: str):
    """Return a cached client for *provider*, creating on first call."""
    if provider in _clients:
        return _clients[provider]

    key = require_api_key(provider)

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=key)
    elif provider == "gemini":
        from openai import OpenAI

        client = OpenAI(api_key=key, base_url=_GEMINI_BASE_URL)
    else:
        from openai import OpenAI

        client = OpenAI(api_key=key)

    _clients[provider] = client
    return client


def invoke(
    messages: list[Message],
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """Call an LLM and return a normalized result dict.

    *messages* is a validated ``list[Message]`` (see ``validate_messages``).
    Returns dict with: response, model, input_tokens, output_tokens,
    latency_ms, finish_reason.
    """
    validate_messages(messages)
    provider = resolve_provider(model)
    client = create_client(provider)

    start = time.perf_counter()

    if provider == "anthropic":
        # Anthropic: system prompt is a top-level kwarg, not in messages.
        api_messages = [
            {"role": m.role, "content": m.content}
            for m in messages if m.role != "system"
        ]
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        system = [m for m in messages if m.role == "system"]
        if system:
            kwargs["system"] = system[0].content

        resp = client.messages.create(**kwargs)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        return {
            "response": resp.content[0].text,
            "model": resp.model,
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
            "latency_ms": elapsed_ms,
            "finish_reason": resp.stop_reason,
        }

    # OpenAI / Gemini (OpenAI-compatible)
    oai_messages = [{"role": m.role, "content": m.content} for m in messages]

    resp = client.chat.completions.create(
        model=model,
        messages=oai_messages,
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    choice = resp.choices[0]
    return {
        "response": choice.message.content,
        "model": resp.model,
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
        "latency_ms": elapsed_ms,
        "finish_reason": choice.finish_reason,
    }
