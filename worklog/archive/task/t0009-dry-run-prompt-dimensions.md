+++
id = "t0009"
title = "Fix dry_run to report prompt sweep dimensions"
status = "done"
tags = ["skill", "invoke-llm", "bugfix"]
modifies = ["s0006"]
+++

## Bug

`dry_run()` only inspects `model` and `temperature` from run specs. Prompt sweep
dimensions (file arrays and inline prompt arrays) are never listed, violating the
spec requirement: "--dry-run prints the number of total runs and lists each sweep
dimension with its values".

The total run count IS correct (the Cartesian product includes prompt dimensions),
but the dimension listing omits them entirely.

## Root cause

Run specs produced by `_build_run_spec` contain only final assembled `messages`,
not the individual dimension values. `dry_run` has no way to reconstruct which
prompt files or texts varied across runs.

## Fix

Propagate dimension metadata from `expand_matrix` so `dry_run` can display all
sweep dimensions including prompts.

## Regression test

Test that `dry_run` output includes prompt file names when a prompt file array is
a sweep dimension. Must fail before fix.
