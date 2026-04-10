+++
id = "s0001"
title = "Prompt Engineer Plugin"
tags = ["core"]
paths = ["plugin/**"]
+++

Claude Code plugin providing prompt-engineering utilities as skills.

Plugin root is `plugin/`. Name: `prompt-engineer`, version `0.0.1`.

## Structure

Plugin manifest lives at `.claude-plugin/plugin.json` (name, description, version). Each subdirectory under `skills/` is a skill exposed by the plugin.

## Skills

- **token-counter** — see [s0002](skill/s0002-token-counter.md).
- **invoke-llm** — see [s0006](skill/s0006-invoke-llm.md).

## Evaluation

- **exams** — see [s0007](infra/s0007-exams.md).

## Agents

- **prompt-engineer** — see [s0010](s0010-prompt-engineer-agent.md).

## Conventions

- Skill scripts are written in Python (see [d0001](../decision/d0001-python-for-plugin-scripts.md)).
- Python environment and shared code — see [s0003](infra/s0003-python-environment.md).
- Testing — see [s0004](infra/s0004-testing.md).

## Anticipated Changes

- Additional skills will be added over time.
