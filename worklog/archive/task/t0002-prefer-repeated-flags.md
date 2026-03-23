+++
id = "t0002"
title = "Instruct assistant to prefer repeated flags over multiple invocations"
status = "done"
tags = ["skill", "token-counter", "ux"]
modifies = ["s0002"]
blocked_by = []
+++

The SKILL.md for token-counter should guide the assistant to combine repeatable flags (like `-m`) into a single invocation rather than running the command multiple times. Currently the skill description says flags are "repeatable" and that "Multiple inputs or models print a comparison table," but nothing explicitly tells the assistant to prefer one call with repeated flags over multiple calls.

Add guidance to SKILL.md (and update s0002 if needed) so the assistant knows to use e.g. `-m cl100k_base -m o200k_base` in one invocation instead of two separate runs.
