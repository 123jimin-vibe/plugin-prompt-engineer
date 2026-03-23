+++
id = "t0007"
title = "Implement invoke-llm skill"
status = "pending"
tags = ["skill", "invoke-llm"]
modifies = ["s0006"]
+++

Implement the invoke-llm skill as specified in s0006.

## Scope

- Single-shot mode: positional/flag inputs, prompt assembly (insertion order), all flags (`-u`, `-U`, `-s`, `-S`, `-m`, `-t`, `--max-tokens`, `-o`, `-q`, `--json`, `--toml`)
- Config mode: TOML parsing, matrix sweep (cartesian product), `--dry-run`, variable substitution, per-entry separator override, `[output].file`
- Provider routing: `claude*` → Anthropic, `gemini*` → Google (OpenAI-compatible), else → OpenAI
- API key validation via `lib.apikey.require_api_key`
- Structured output: JSONL (`--json`), TOML (`--toml`), plain text
- `-q` suppression of response text
- Per-run error recording (config mode), summary table to stderr
- SKILL.md with model table and assistant guidance

## Out of scope (TODOs in spec)

- Concurrency for matrix sweeps
- Retry / rate-limit handling
- Streaming output
- Temperature default decision

## Files to add

### `plugin/skills/invoke-llm/scripts/invoke.py`

Main script.

| Function | Responsibility |
|----------|---------------|
| `parse_args(argv)` | argparse with mutual exclusion (`-c` vs single-shot, `--json` vs `--toml`) |
| `build_prompt(args)` | Assemble system/user messages from flags in insertion order |
| `load_config(path)` | Parse TOML, resolve file paths relative to TOML parent |
| `expand_matrix(config)` | Cartesian product of sweep dimensions → list of run specs |
| `substitute_vars(text, vars)` | `{{key}}` replacement; error on missing key |
| `format_result(result, fmt, quiet)` | Format one result as plain/JSON/TOML, honoring `-q` |
| `dry_run(matrix)` | Print dimension summary + total count to stdout |
| `main()` | Orchestrate: parse → single-shot or config → invoke → format → output |

### `plugin/lib/llm.py`

Shared LLM client logic, reusable by future skills.

| Function | Responsibility |
|----------|---------------|
| `resolve_provider(model)` | `claude*` → `"anthropic"`, `gemini*` → `"gemini"`, else → `"openai"` |
| `create_client(provider)` | Lazy-init Anthropic/OpenAI client with `require_api_key`; Gemini uses OpenAI client with hardcoded base URL |
| `invoke(messages, model, temperature, max_tokens)` | Unified call → normalized result dict (response, model, input_tokens, output_tokens, latency_ms, finish_reason) |

### `plugin/skills/invoke-llm/SKILL.md`

Assistant-facing guidance with model table, flag reference, examples.

### `tests/lib/test_llm.py`

Tests for `resolve_provider`, `create_client` (mocked), `invoke` (mocked).

### `tests/skills/invoke_llm/test_invoke.py`

Tests for `parse_args`, `build_prompt`, `load_config`, `expand_matrix`, `substitute_vars`, `dry_run`, `format_result`.

## Files to modify

| File | Change |
|------|--------|
| `plugin/pyproject.toml` | Update `requires-python` to `>=3.11`; use stdlib `tomllib` (no `tomli` dependency) |
| `plugin/skills/token-counter/scripts/count.py` | Refactor to use `lib.llm.create_client` instead of inline Anthropic client init |

## Dependency graph

```
invoke.py
  ├── lib.llm          (resolve_provider, create_client, invoke)
  │     └── lib.apikey  (require_api_key)
  └── lib.format        (render_table — for summary/dry-run)
```
