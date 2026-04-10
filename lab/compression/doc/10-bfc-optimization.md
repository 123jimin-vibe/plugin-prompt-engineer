+++
id = "s0010"
title = "Optimization passes"
created = 2026-03-16
tags = ["bf", "bsm", "optimizer"]
+++

AST optimization passes for BF and BSM layers.

## Overview

Optimizations fall into two categories:

- **Trivial** — applied inline during translation (emitter, compiler) as part of code generation. Always active; unaffected by `--no-opt`.
- **Optimizer passes** — explicit AST transformations invoked as a pipeline stage. Skipped with `--no-opt`.

Both categories rely on shared **pattern matchers** that structurally recognize loop idioms (clear loops, multiply-add loops, dead loops).

## Assumptions

- The target BF interpreter typically optimizes RLE runs (`+++`/`>>>`) and clear loops (`[-]`). Optimizations should preserve these patterns.
- Cell size is unknown by default. Wrapping behavior depends on the target; width-specific optimizations must be gated.
- `Output` and `Input` are observable side effects — reordering across them is unsound. Final cell values are observable, but final pointer position is not.

## BF Layer

### Dead Loop at Start

All cells are zero at program start. Any top-level loop whose test cell has not been written to is dead. The "start" window extends as long as the pointer position is statically known. `Output` and `Breakpoint` do not break the window; `Move`, `Add`, and `Input` mark cells as written.

Not applied inside loop bodies — a body is only reached when its parent cell is non-zero.

### Dead Loop After Loop

When a loop exits, its test cell is guaranteed zero. A subsequent loop on the same cell — separated only by `Output` or `Breakpoint` — is dead. `Move`, `Add`, `Input`, and nested loops break the window. Applied recursively into loop bodies.

## BSM Layer — Trivial

### Clear Loop

A loop whose only effect is decrementing its test cell by any nonzero amount.

- **Emitter**: Uses `CELL = 0` shorthand.
- **Compiler**: Emits canonical `[-]` regardless of original delta.

### Multiply-Add Loop

A loop that decrements a source cell by a constant and adds constant multiples to other cells per iteration.

- **Emitter**: Uses `[N] SRC -> [M] DST, …` shorthand.
- **Compiler**: Emits source decrement first, then targets in offset-sorted order (monotonic sweep to minimize pointer travel).

### Dead Loop at Start

Same principle as BF layer. All cells start at zero; loops on unwritten cells at program start are dead. `Output`, `Goto`, and `Breakpoint` do not write cells and do not break the window. `Input`, `Set`, and `Add` mark only their target cells as written.

### Dead Loop After Loop

Same principle as BF layer. A loop immediately following another loop on the same test cell is dead. `Output` and `Breakpoint` between the two loops are safe. `Goto` between loops invalidates the window — pointer-relative addressing would refer to a different absolute cell.

## BSM Layer — Optimizer Passes

### Pipeline Order

1. Pattern rewrites (clear loop, zero-delta mul-add strip)
2. Goto coalescing
3. Value tracking

### Clear Loop

Rewrites `Loop(cell, [Add(cell, -N)])` → `Set(cell, 0)`. Applied recursively, inner loops first.

### Zero-Delta Multiply-Add Strip

If a multiply-add loop's source delta is zero, the source never changes. The loop either skips (source = 0) or hangs (source ≠ 0). In any terminating execution the targets are unreachable — the loop body is stripped.

### Goto Coalescing

Adjacent `Goto` nodes are merged into a single node by summing offsets. Net-zero results are dropped. Trailing `Goto` nodes at the end of a sequence are dropped — final pointer position is not observable. Applied recursively into loop bodies.

Note: the compiler already coalesces gotos implicitly via deferred pointer movement (`BfBuilder`). This optimizer pass benefits the emitter and interpreter paths.

### Value Tracking

Single forward scan maintaining a cell → known_value map (CellState). Maps pointer-relative offsets to known values, acting as an implicit frame anchored to the current pointer position. Subsumes the separate dead-loop elimination passes.

**Addressing model:** Goto shifts the map window (O(1)). Balanced loops (body delta = 0) invalidate only written offsets; unbalanced loops invalidate the entire map. Loop test cell is set to 0 on exit. Program start sets `is_all_zero`.

**Optimizations applied:**
- **Add coalescing:** consecutive adds to the same unknown cell are merged.
- **Set+add fusion:** `Set(N, V)` followed by `Add(N, D)` → `Set(N, V+D)` (or `Add` if value known — see below).
- **Set-to-add conversion:** When a `Set(N, V)` targets a cell with known value K, it is converted to `Add(N, V-K)`. This avoids the `[-]` clear prefix in the compiled BF. If a pending `Add` already exists for the same offset, the delta is fused into it.
- **Dead store elimination:** a write to an offset overwritten before any observation is dropped.
- **Redundant set elimination:** a set to the same value the cell already holds is dropped.
- **Dead loop elimination:** a loop whose test cell is known zero is dropped entirely.
- **Input clobber:** when EOF behavior is `zero` or `minus_one`, a pending write to a cell immediately before `Input` on that cell is dead. When EOF is `unchanged`, the write survives.

**Design principle — prefer `Add` over `Set`:** The pass does NOT convert `Add` to `Set`, even when the cell value is known. In BF, `Add(N)` compiles to `+++…` while `Set(N)` compiles to `[-]+++…` — the clear prefix is wasteful when the cell is already zero. Conversely, `Set` IS converted to `Add` whenever the cell value is known, since the clear is redundant in that case.

## Pattern Matchers

Structural recognizers over `CoreLoop` nodes. Used by both trivial optimizations and optimizer passes. Return a typed result or `null`.

### Scan Loop

`Loop(cell, [Goto(@±N)])` — the loop moves the pointer by a fixed stride each iteration until landing on a zero cell. Returns `{ cell, stride }`. Recognition only; no AST rewrite.
