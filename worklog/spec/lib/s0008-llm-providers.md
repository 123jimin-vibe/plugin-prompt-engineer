+++
id = "s0008"
title = "LLM Providers"
tags = ["lib", "llm", "api"]
paths = ["plugin/lib/apikey.py", "plugin/lib/llm.py"]
+++

Shared provider routing, client management, and API key validation for all skills that call LLMs.

## Provider Routing

`resolve_provider(model)` maps a model ID to a provider name:

| Prefix | Provider |
|--------|----------|
| `claude*` | `anthropic` |
| `gemini*` | `gemini` |
| everything else | `openai` |

## API Key Validation

`require_api_key(provider)` looks up the env var for a provider and exits with a one-line error if unset.

| Provider | Env var |
|----------|---------|
| `anthropic` | `ANTHROPIC_API_KEY` |
| `openai` | `OPENAI_API_KEY` |
| `gemini` | `GEMINI_API_KEY` |

Unknown provider names are a fatal error.

## Client Creation

`create_client(provider)` returns a cached SDK client. Gemini uses the OpenAI SDK pointed at Google's OpenAI-compatible endpoint.

## Unified Invoke

`invoke(messages, model, temperature, max_tokens)` dispatches to the correct provider and returns a normalized dict: `response`, `model`, `input_tokens`, `output_tokens`, `latency_ms`, `finish_reason`.

`messages` is a `list[Message]` where `Message` is a frozen dataclass with `role` and `content` fields. Roles: `"system"`, `"user"`, `"assistant"`. The sequence must match `system? (user assistant)* user` — `validate_messages()` enforces this before dispatch. The function converts to provider-specific format internally (Anthropic: system extracted to top-level kwarg; OpenAI/Gemini: passed as-is).

## Anticipated Changes

- TODO: retry and rate-limit handling (see also s0006).
- TODO: streaming support.
