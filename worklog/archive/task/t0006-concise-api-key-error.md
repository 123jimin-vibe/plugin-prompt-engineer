+++
id = "t0006"
title = "Concise error message when API key is missing"
status = "done"
tags = ["token-counter", "error-handling"]
modifies = ["s0002"]
+++

## Problem

When `ANTHROPIC_API_KEY` is unset, the Anthropic SDK raises a `TypeError` with a multi-line traceback. The spec says "exits with a clear error if missing" but the implementation does not catch this.

## Scope

- Detect missing API key before the SDK call and exit with a one-line message (e.g. `Error: ANTHROPIC_API_KEY is not set.`).
- Extract the check into a reusable pattern — other parts of the plugin (LLM invocation) will need the same logic.
- Design should anticipate multiple API providers (OpenAI, Gemini) in future.

## Notes

- Current failure point: `count.py:51` — `Anthropic()` constructor or the subsequent API call raises when no key is found.
- The spec already describes the desired behavior; this task brings the code into compliance.
