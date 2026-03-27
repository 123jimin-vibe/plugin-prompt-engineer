# Prompt Evaluation via Q&A

Prerequisite: read `config.md` for the TOML config schema.

Predicting LLM behavior is a false-belief task — you cannot reliably model another model's output, even your own under a different system prompt. This pattern evaluates a prompt (especially a skill's SKILL.md) by running it. Useful when single-shot mode becomes unwieldy or repeated tests are needed.

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
prompt = [
  # Tests whether the model handles multi-step requests in order.
  # Expected: does X first, then Y, does not merge them.
  "A user asks you to do X, then follows up with Y. What do you do?",
  # Tests step-by-step reasoning under scenario Z.
  # Expected: addresses each step explicitly, does not skip step 2.
  "Given scenario Z, walk through how you would handle each step.",
]

[output]
file = "eval-results.jsonl"
```

2 models x 2 scenarios = 4 runs. Prefer fewer, scenario-based prompts over many isolated questions. Use `--dry-run` to verify before running.

## Writing questions

Prefer questions with objective, scorable answers. Open-ended questions are fine when the user will review outputs directly. Comment each question in the config with its intention and expected answer.

Common pitfalls (all stem from projecting your own understanding onto the questions):
- **Leading questions**: embedding the expected answer biases the LLM toward it.
- **Testing your interpretation**: resolving ambiguities in your head, then writing questions that validate your reading.
- **Happy-path bias**: only testing inputs that naturally succeed.

Ground questions in realistic user inputs. Prefer harder questions that distinguish good prompts from bad.

## Multi-turn evaluation

Use the `assistant` role to inject a prior response, then ask the model to evaluate it:

```toml
# Used with prompt-engineer:invoke-llm skill.

[generation]
model = "claude-sonnet-4-6"
temperature = 0.0

[[prompts]]
role = "system"
file = "SKILL.md"

[[prompts]]
role = "user"
prompt = "A user asks you to do X, then follows up with Y."

[[prompts]]
role = "assistant"
prompt = ["candidate-answer-a.md", "candidate-answer-b.md"]

[[prompts]]
role = "user"
prompt = "Rate the above response 1-5. Explain."
```

2 candidate answers = 2 runs. Each run evaluates a different assistant response.

## Tips

- Use `--json` or `[output].file` to capture results for comparison.
- Use `[vars]` + `substitute = true` to inject test cases into a prompt template.
