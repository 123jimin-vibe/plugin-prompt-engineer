# invoke-llm

Raw LLM API calls (text in, text out). No tool use, no agent context, no skills.

Script: `invoke.py`

## Models

Any model ID is accepted. Routing is prefix-based — not restricted to the examples below.

| Provider | Models | Env var |
|----------|--------|---------|
| Anthropic | `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5` | `ANTHROPIC_API_KEY` |
| OpenAI | `gpt-5.4`, `gpt-5-mini` | `OPENAI_API_KEY` |
| Google | `gemini-3.1-pro-preview`, `gemini-3-flash-preview` | `GEMINI_API_KEY` |

Routing: `claude*` -> Anthropic, `gemini*` -> Google (OpenAI-compatible endpoint), everything else -> OpenAI.

## Single-shot mode

```
invoke.py "What is 2+2?"
invoke.py -s "You are a poet" -u "Write about rain"
invoke.py -S system.md -U prompt.md -m gpt-4o
invoke.py -u "Hello" --json
invoke.py -u "Hello" -q --json   # metadata only, no response text
invoke.py -u "Hello" -o output.txt
```

| Flag | Description |
|------|-------------|
| (positional) | User prompt string (shorthand for `-u`) |
| `-u TEXT` | User prompt string (repeatable) |
| `-U FILE` | User prompt from file (repeatable) |
| `-s TEXT` | System prompt string (repeatable) |
| `-S FILE` | System prompt from file (repeatable) |
| `-m MODEL` | Model ID. Default: `claude-sonnet-4-6` |
| `-t TEMP` | Temperature |
| `--max-tokens N` | Max output tokens. Default: `4096` |
| `-o FILE` | Write output to file (still prints to stdout) |
| `-q` | Suppress response text in stdout |
| `--json` | JSONL output with metadata |
| `--toml` | TOML output with metadata |

Prompts are assembled in the order they appear on the command line. Same-role entries joined by `\n\n`.

## Config mode

```
invoke.py -c run.toml
invoke.py -c run.toml --dry-run
invoke.py -c run.toml --json
```

TOML config with matrix sweep (cartesian product of array values). See `references/config.md` for full schema.

`--dry-run` prints dimension summary and total run count without making API calls.

## Assistant guidance

- Use single-shot mode for quick one-off prompts.
- Use config mode with `--dry-run` first to verify sweep dimensions before running.
- Use `--json` for structured output that's easy to parse programmatically.
- Use `-q --json` when you only need metadata (tokens, latency) without the response text.
- For prompt iteration, use config mode with file-based prompts and variable substitution.
