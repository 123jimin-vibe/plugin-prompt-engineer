+++
id = "s0006"
title = "Invoke LLM Skill"
tags = ["skill", "invoke-llm"]
paths = ["plugin/skills/invoke-llm/**"]
+++

Raw LLM API calls (text in, text out). No tool use, no agent context, no skills.

## Modes

Two mutually exclusive modes: **single-shot** (CLI flags) and **config** (TOML file). Prompt flags (`-u`, `-U`, `-s`, `-S`, positional) are mutually exclusive with `-c`. Generation and output flags override their TOML counterparts when used with `-c`.

## Single-shot mode

Positional and flag inputs build a single request.

### Inputs

| Input | Description |
|-------|-------------|
| (positional) | User prompt string (shorthand for `-u`) |
| `-u TEXT` | User prompt string (repeatable) |
| `-U FILE` | User prompt from file (repeatable) |
| `-s TEXT` | System prompt string (repeatable) |
| `-S FILE` | System prompt from file (repeatable) |
| `-m MODEL` | Model ID. Default: `claude-sonnet-4-6` |
| `-t TEMP` | Temperature. Default: see Temperature section |
| `--max-tokens N` | Max output tokens. Default: `4096` |
| `-o FILE` | Write output to file (still prints to stdout) |
| `-q` | Suppress response text in stdout. Metadata (tokens, latency, etc.) still shown if `--json`/`--toml` is active |
| `--json` | JSONL output with metadata |
| `--toml` | TOML output with metadata |

`--json` and `--toml` are mutually exclusive.

### Prompt assembly

All `-u`, `-U`, `-s`, `-S`, and positional inputs are concatenated **in the order they appear on the command line**. Consecutive same-role entries are joined by the default separator (`"\n\n"`). The result is one system message and one user message.

## Message sequence

LLM APIs require the pattern `system? (user assistant)* user`. This is enforced after assembly:

- **Consecutive same-role entries** are joined with the separator into a single message.
- **Out-of-place role** (e.g. assistant first, assistant last, two user turns without an assistant between them after joining) causes a clear error naming the offending position.

This applies to both single-shot and config modes.

## Config mode

```
invoke.py -c run.toml
invoke.py -c run.toml --dry-run
invoke.py -c run.toml --json
invoke.py -c run.toml --toml
```

`--dry-run` requires `-c`. It prints the number of total runs and lists each sweep dimension with its values, then exits without making any API calls.

### TOML schema

```toml
# Used with prompt-engineer:invoke-llm skill.
[generation]
model = ["claude-sonnet-4-6", "gpt-5.4-mini"]   # scalar or array (sweep)
temperature = [0.0, 0.5, 1.0]                  # scalar or array (sweep)
max_tokens = 4096                               # scalar only
separator = "\n\n"                              # default join between same-role entries

[vars]
input = "inputs/case1.md"            # named file refs, content read at runtime

[[prompts]]
role = "system"                       # "system", "user", or "assistant"
file = ["strict.md", "relaxed.md"]    # array = sweep dimension

[[prompts]]
role = "user"
prompt = "inline text"                # use file or prompt, not both

[[prompts]]
role = "user"
file = "question.md"
substitute = true                     # replace {{key}} with [vars] content
separator = "\n---\n"                 # overrides [generation].separator for this join point
```

**Comment convention:** Start config files with `# Used with prompt-engineer:invoke-llm skill.` for identification.

**Matrix:** Cartesian product of all array values across `[generation]` and `[[prompts]]`. Example above: 2 models × 3 temps × 2 system files = 12 runs.

**Path resolution:** All file paths (`file`, `[vars]`, `[output].file`) resolve relative to the TOML file's parent directory.

**Variable substitution:** When `substitute = true`, `{{key}}` placeholders are replaced with content from `[vars]`. A reference to a missing var is an error — the run aborts with a message naming the unresolved key.

**Per-run errors** are recorded without aborting the sweep. A summary table prints to stderr after completion.

### Output file

```toml
[output]
file = "results.jsonl"
```

## Flag overrides in config mode

When generation or output flags are passed alongside `-c`, they override the corresponding TOML values:

| Flag | Overrides | Effect |
|------|-----------|--------|
| `-m MODEL` | `[generation].model` | Replaces model (collapses any sweep to this single model) |
| `-t TEMP` | `[generation].temperature` | Replaces temperature (collapses any sweep to this single value) |
| `--max-tokens N` | `[generation].max_tokens` | Replaces max tokens |
| `-o FILE` | `[output].file` | Replaces output file path |

Flags that are not explicitly passed do not override — config values are used as-is. Prompt flags (`-u`, `-U`, `-s`, `-S`, positional) remain mutually exclusive with `-c`.

## Provider routing

Three prefixes, three env vars:

| Prefix | Provider | Env var |
|--------|----------|---------|
| `claude*` | Anthropic | `ANTHROPIC_API_KEY` |
| `gemini*` | Google (OpenAI-compatible endpoint) | `GEMINI_API_KEY` |
| everything else | OpenAI | `OPENAI_API_KEY` |

Missing key → clear one-line error via shared `require_api_key` (see s0005 lib). Only the keys actually needed by the run are checked.

## Temperature

TODO: default temperature. `1.0` maximizes cross-provider compatibility (all providers accept it). `0.0` is more useful for deterministic prompt testing. Needs decision.

## Structured output

When `--json` or `--toml` is active, each run produces a record with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | Model output text |
| `model` | string | Model ID used |
| `input_tokens` | int | Prompt token count |
| `output_tokens` | int | Completion token count |
| `latency_ms` | int | Wall-clock time for the API call |
| `finish_reason` | string | Normalized stop reason |

`--json` always emits JSONL (one JSON object per line per run). `--toml` emits a TOML document with `[[results]]` array. Without either flag, only the raw `response` text is printed.

`-q` omits the `response` field from structured output and suppresses raw text in plain mode. Combined with `--json` or `--toml`, the metadata fields (model, tokens, latency, finish_reason) are still emitted.

## Anticipated changes

- TODO: concurrency for matrix sweeps.
- TODO: retry and rate-limit handling.
- TODO: streaming output.
