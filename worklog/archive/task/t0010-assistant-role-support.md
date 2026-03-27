+++
id = "t0010"
title = "Support assistant role in invoke-llm prompts"
status = "done"
tags = ["skill", "invoke-llm", "feature"]
modifies = ["s0006", "s0008"]
+++

## Problem

Agents building Q&A evaluation configs cannot use the assistant role. The spec
limits `[[prompts]]` role to `"system"` or `"user"`, and the implementation
enforces this at every layer:

- `_build_run_spec` buckets into `system_parts` / `user_parts` only
- `messages` is `dict[str, str]` — flat, no ordering, no multi-turn
- `llm.invoke` accepts `dict[str, str]` and builds a fixed `[system, user]` array
- Provider call sites hardcode the two-message shape

## Use case

Multi-turn prompts for evaluation:

```toml
[[prompts]]
role = "user"
prompt = "What is X?"

[[prompts]]
role = "assistant"
prompt = "X is Y."

[[prompts]]
role = "user"
prompt = "Was that answer correct? Explain."
```

## Required changes

1. **Spec (s0006)**: allow `role = "assistant"` in `[[prompts]]`.
2. **`Message` dataclass** (lib): introduce `Message(role: str, content: str)`.
   Replace `dict[str, str]` with `list[Message]` everywhere messages flow.
3. **`_build_run_spec`** (invoke.py): build ordered `list[Message]` instead of
   bucketing by role. System prompt stays separate (Anthropic API requires it
   outside the messages array).
4. **`llm.invoke`** (llm.py): accept `list[Message]` and convert to provider
   format. Anthropic: extract system, forward rest. OpenAI/Gemini: pass as-is.
5. **`build_prompt`** (single-shot path): update to return `list[Message]`.
6. **Message sequence validation**: LLM APIs require the pattern
   `system? (user assistant)* user`. Enforce this:
   - Consecutive same-role entries: join with separator into one message.
   - Out-of-place role (e.g. two user turns without an assistant between,
     assistant first, assistant last): error with a clear message naming
     the offending entry.
7. **Tests**: cover multi-turn assembly, sweep with assistant entries, provider
   call shapes.
