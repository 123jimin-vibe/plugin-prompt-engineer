# Compression

Prompt compression for non-creative prompts, mainly SKILL.md files and worklog specs.

## Goals

1. Find which techniques are effective for compressing prompts without losing quality.
2. Find effective instructions for LLMs that would compress prompts (i.e. instructions for the prompt-engineer agent).

## Data

Test data sorted by length relative to text structure (not absolute token/character counts):

- **Sentence-level**
- **Paragraph-level**
- **Document-level**

Each data item must be self-contained. Minor modification from raw data is permitted but should be kept minimal.

Do not use the `doc` dataset unless explicitly requested — experiments on it are slow to execute.

## Analysis

- [hypotheses.md](hypotheses.md) — compression improvement hypotheses
- [findings.md](findings.md) — experiment results
