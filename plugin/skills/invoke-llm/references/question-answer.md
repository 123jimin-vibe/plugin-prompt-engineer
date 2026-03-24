# Prompt Evaluation via Q&A

Prerequisite: read `config.md` for the TOML config schema.

Predicting LLM behavior is a false-belief task — you cannot reliably model another model's output, even your own under a different system prompt. This pattern evaluates a prompt (especially a skill's SKILL.md) by running it and reviewing actual outputs. Useful when single-shot mode becomes unwieldy or repeated tests are needed.

## Config

```toml
# Used with prompt-engineer:invoke-llm skill.

[generation]
model = ["claude-sonnet-4-6", "gpt-5.4-mini"]
temperature = 0.0

[[prompts]]
role = "system"
file = "SKILL.md"

[[prompts]]
role = "user"
prompt = ["What is X?", "Explain Y.", "How do you handle Z?"]

[output]
file = "eval-results.jsonl"
```

2 models x 3 questions = 6 runs. Use `--dry-run` to verify before running. Prefer inline `prompt` over `file` to keep configs self-contained.

## Tips

- Use `--json` or `[output].file` to capture results for comparison.
- Use `[vars]` + `substitute = true` to inject test cases into a prompt template.
