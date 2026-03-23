"""Shared LLM client logic — provider routing, client creation, unified invoke."""

import time

from lib.apikey import require_api_key

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
    messages: dict[str, str],
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """Call an LLM and return a normalized result dict.

    *messages* has keys ``"system"`` and/or ``"user"`` with string values.
    Returns dict with: response, model, input_tokens, output_tokens,
    latency_ms, finish_reason.
    """
    provider = resolve_provider(model)
    client = create_client(provider)

    start = time.perf_counter()

    if provider == "anthropic":
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": messages.get("user", "")}],
        }
        if "system" in messages and messages["system"]:
            kwargs["system"] = messages["system"]

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
    oai_messages = []
    if "system" in messages and messages["system"]:
        oai_messages.append({"role": "system", "content": messages["system"]})
    oai_messages.append({"role": "user", "content": messages.get("user", "")})

    resp = client.chat.completions.create(
        model=model,
        messages=oai_messages,
        temperature=temperature,
        max_tokens=max_tokens,
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
