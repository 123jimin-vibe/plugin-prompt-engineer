+++
id = "d0001"
title = "Use Python for plugin scripts"
relates_to = ["s0001", "s0002"]
supersedes = []
+++

## Context

The plugin needs a language for skill script implementations. The first skill (token-counter) requires a tokenizer library. A previous version of this skill was implemented in Python.

## Options Considered

1. **Python** — tiktoken is native, previous implementation used it, strong text-processing ecosystem.
2. **JavaScript** — JS tiktoken ports exist but are second-class; no plugin harness requirement for JS.

## Decision

Python for all plugin scripts.

## Consequences

- Scripts live as `.py` files under each skill's `scripts/` directory.
- Python + pip are runtime dependencies.
- tiktoken can be used directly.
