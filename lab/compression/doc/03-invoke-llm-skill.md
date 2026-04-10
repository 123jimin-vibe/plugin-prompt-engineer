---
name: invoke-llm
description: "Run prompts against LLMs. MUST trigger when: test/send/invoke a prompt, get a completion, compare models, matrix sweep, batch-test prompts, edit an invoke-llm config file."
---
<skill id="prompt-engineer:invoke-llm">
Script: `${CLAUDE_SKILL_DIR}/scripts/invoke.py`

Run with the plugin venv at `${CLAUDE_PLUGIN_DATA}/venv`.

Raw LLM API calls (text in, text out). No tool use, no agent context, no skills.

## Models

Any model ID is accepted. Routing is prefix-based — not restricted to the examples below.

| Provider | Models | Env var |
|----------|--------|---------|
| Anthropic | `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5` | `ANTHROPIC_API_KEY` |
| OpenAI | `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano` | `OPENAI_API_KEY` |
| Google | `gemini-3.1-pro-preview`, `gemini-3-flash-preview` | `GEMINI_API_KEY` |

Routing: `claude*` -> Anthropic, `gemini*` -> Google (OpenAI-compatible endpoint), everything else -> OpenAI.

## Single-shot mode

```
invoke.py "What is 2+2?"
invoke.py -s "You are a poet" -u "Write about rain"
invoke.py -S system.md -U prompt.md -m gpt-5.4-mini --json
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
| `-q` | Suppress response text (metadata still shown with `--json`/`--toml`) |
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

- Predicting LLM responses is a false-belief task — you cannot reliably model another model's behavior, even your own under a different system prompt. Invoke and observe.
- Use single-shot mode for quick one-off prompts.
- Use config mode with `--dry-run` to verify sweep dimensions before running.
- Use `--json` for structured output.
- Use `-q --json` when you only need metadata (tokens, latency) without the response text.
- For prompt iteration, use config mode with file-based prompts and variable substitution.
- For repeated prompt evaluation (e.g. testing a skill's SKILL.md across models/questions), see `references/question-answer.md`.
</skill>
