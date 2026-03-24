+++
id = "s0007"
title = "Exams"
tags = ["infra", "testing", "prompts"]
paths = ["exams/**"]
+++

Question-answer configs that test prompts shipped by this plugin. Uses the invoke-llm skill's config mode ([s0006](s0006-invoke-llm.md)) to run prompts against LLMs and verify behavior.

## Purpose

Unit tests validate script logic. Exams validate prompt behavior — whether a SKILL.md actually elicits the intended responses from a model. This is the difference between "does the code work" and "does the prompt work."

## Layout

Exams live in `exams/` at the repo root, organized by skill. Example (illustrative — do not keep in sync with actual contents):

```
exams/
  token-counter/
    basic-usage.toml
    edge-cases.toml
  invoke-llm/
    config-mode.toml
    single-shot.toml
```

Each skill directory can contain multiple TOML configs, each targeting a different aspect of the skill's behavior. Name configs descriptively after what they test. Supporting files (input fixtures, expected-output references) live alongside them.

## Config structure

Each exam config is a standard invoke-llm TOML config (see the invoke-llm skill's `config.md` reference). Typically the system prompt points at a skill's SKILL.md and user prompts are the exam questions, but configs can diverge from this pattern.

Run exams using the agent's own `prompt-engineer:invoke-llm` skill.

## Writing questions

Prefer the agent's own `question-answer.md` reference (loaded with the invoke-llm skill) over reading this repo's copy, to avoid duplicating content in context. If the agent doesn't have the skill loaded, the repo file is an acceptable fallback.

## Relationship to s0004 (Testing)

s0004 covers unit/integration tests for script logic (`tests/`). This spec covers prompt-level evaluation (`exams/`).

## Anticipated changes

- Grading is manual review. Automated judge unlikely but not ruled out.
- Baseline regression detection relies on git history of output files.
