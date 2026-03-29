+++
id = "t0011"
title = "Matrix expansion for max_tokens and vars"
status = "done"
tags = ["invoke-llm", "matrix"]
modifies = ["s0006"]
+++

`max_tokens` and `[vars]` values are the only generation/input fields that don't support array (sweep) expansion, despite being natural sweep dimensions alongside `model` and `temperature`.

## Changes

- `[generation].max_tokens`: support array of ints as a sweep dimension.
- `[vars]` values: support array of file paths as a sweep dimension. Each combination loads different file content for `{{key}}` substitution.
- Update spec s0006, reference doc `config.md`, tests, and implementation.
