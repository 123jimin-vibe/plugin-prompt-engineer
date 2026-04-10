+++
id = "s0010"
title = "Prompt Engineer Agent"
tags = ["agent"]
paths = ["plugin/agents/prompt-engineer.md"]
+++

Subagent with detailed prompt engineering knowledge. Offloads prompt-related reasoning from the main agent's context window — the main agent delegates prompt tasks without needing prompt engineering principles in its own context.

The agent file contains a system prompt encoding verified prompt engineering principles. Every principle must be empirically validated: tested against real LLM behavior using the invoke-llm skill, not assumed from intuition or convention. Unverified principles do not belong in the agent file. See [lab/README.md](../../lab/README.md) for the experimental process.

## Anticipated Changes

- Token budget mode: iteratively compress until a target count is met.
