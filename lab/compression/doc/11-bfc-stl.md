+++
id = "s0011"
title = "BSM Standard Macro Library (STL)"
created = 2026-03-17
tags = ["stl", "bsm"]
+++

Pre-loaded macros available to any BSM program without explicit `use`. Requires the Macro Extension (s0007) and Frames (s0006).

Reference: `worklog/plan/p0001-stl-expansion.md` (canonical tier definitions)

## Loading

The compiler implicitly loads `bsm-stl/index.bsm` before user source. STL macros are available globally — no `use` directive needed.

## File Layout

`bsm-stl/index.bsm` imports all STL components via `use` directives in dependency order: cell → logic → control → arithmetic → io. Each tier lives in its own `.bsm` file.

## Macro Visibility

A macro body can only call macros that were declared before it in the flattened load order (i.e., macros from files it `use`s, or earlier declarations in the same file). This is enforced at expansion time via a visibility snapshot captured at declaration. Block arguments are exempt — they execute with the caller's visibility.

## Conventions

| Suffix   | Meaning                                          |
| -------- | ------------------------------------------------ |
| `_d`   | Destructive. Source zeroed. Cheapest — no backup. |
| `_to`    | Source preserved; accumulates into existing dst. |
| *(bare)* | Source preserved; writes fresh result into dst.  |

Parameters are **consumed** (indeterminate after call) unless described as preserved.

`->` separates inputs from outputs.

## Tier 0 — Cell Primitives

File: `bsm-stl/cell.bsm`. `_d` signatures match bare but without scratch.

| Macro    | Signature          | Tmp | Effect                       |
| -------- | ------------------ | :-: | ---------------------------- |
| `mov`    | `(src -> dst)`     | 0   | dst = src; src = 0           |
| `copy`   | `(src -> dst)`     | 1   | dst = src; src preserved     |
| `swap`   | `(a, b)`           | 1   | Exchange values              |
| `add_d`  | `(src -> dst)`     | 0   | dst += src; src = 0          |
| `add_to` | `(src -> dst)`     | 1   | dst += src; src preserved    |
| `add`    | `(a, b -> dst)`    | 1   | dst = a + b; a, b preserved  |
| `sub_d`  | `(src -> dst)`     | 0   | dst -= src; src = 0          |
| `sub_to` | `(src -> dst)`     | 1   | dst -= src; src preserved    |
| `sub`    | `(a, b -> dst)`    | 1   | dst = a - b; a, b preserved  |

## Tier 1 — Arithmetic

File: `bsm-stl/arithmetic.bsm`. `_d` destroys `a`; bare preserves.

| Macro        | Signature         | Tmp (_d / bare) | Effect                      |
| ------------ | ----------------- | :-------------: | --------------------------- |
| `mul`        | `(a, b -> dst)`   | 1 / 2           | dst = a × b; b preserved    |
| `divmod_10`  | `(a -> q, r)`     | 2 / 3           | q = a/10, r = a%10          |
| `divmod`     | `(a, b -> q, r)`  | 2 / 3           | q = a/b, r = a%b; b preserved (undefined when b=0) |

## Tier 2 — Comparison & Logic

File: `bsm-stl/logic.bsm`. `_d` destroys operands; bare preserves.

| Macro     | Signature        | Tmp (_d / bare) | Effect             |
| --------- | ---------------- | :-------------: | ------------------ |
| `is_zero` | `(a -> r)`       | 0 / 1           | r = (a == 0)       |
| `bool`    | `(a -> r)`       | 0 / 1           | r = (a != 0)       |
| `not`     | `(a -> r)`       | 0 / 1           | Alias for `is_zero` |
| `eq`      | `(a, b -> r)`    | 0 / 1           | r = (a == b)       |
| `neq`     | `(a, b -> r)`    | 0 / 1           | r = (a != b)       |
| `gt`      | `(a, b -> r)`    | 2 / 4           | r = (a > b)        |
| `lt`      | `(a, b -> r)`    | 2 / 4           | r = (a < b)        |
| `ge`      | `(a, b -> r)`    | 2 / 4           | r = (a >= b)       |
| `le`      | `(a, b -> r)`    | 2 / 4           | r = (a <= b)       |
| `or_d`    | `(src -> dst)`   | 0               | dst = dst \|\| src; src = 0 |
| `or`      | `(a, b -> r)`    | 1               | r = (a \|\| b); a, b preserved |
| `and`     | `(a, b -> r)`    | 0 / 2           | r = (a && b)       |

## Tier 3 — Control Flow

File: `bsm-stl/control.bsm`

| Macro       | Signature                    | Tmp (_d / bare) | Effect              |
| ----------- | ---------------------------- | :-------------: | -------------------- |
| `if`        | `(cond) {then}`              | 0 / 2           | Run block if cond ≠ 0 |
| `if_else`   | `(cond) {then} {else}`       | 1 / 2           | Branch on cond       |
| `while`     | `(flag) {cond} {body}`       | 0               | Repeat while `{cond}` sets flag ≠ 0 |

## Tier 4 — I/O

File: `bsm-stl/io.bsm`. `_d` destroys input; bare preserves.

### Character Classification

| Macro        | Signature    | Tmp (_d / bare) | Effect              |
| ------------ | ------------ | :-------------: | -------------------- |
| `is_space`   | `(a -> r)`   | 0 / 1           | r = (a == 32)        |
| `is_newline` | `(a -> r)`   | 0 / 1           | r = (a == 10)        |
| `is_digit`   | `(a -> r)`   | 0 / 1           | r = (a ∈ ['0'..'9']) |

### Decimal I/O

| Macro       | Signature    | Tmp | Effect                           |
| ----------- | ------------ | :-: | -------------------------------- |
| `read_uint` | `(-> dst)`   | 3   | Parse unsigned decimal from stdin |
| `print_uint8_d` | `(v)` | 5 | Print 8-bit unsigned decimal; destroys v |
| `print_uint8` | `(v)` | 6 | Print 8-bit unsigned decimal; v preserved |
| `print_uint16_d` | `(v)` | 6 | Print 16-bit unsigned decimal; destroys v |
| `print_uint16` | `(v)` | 7 | Print 16-bit unsigned decimal; v preserved |
| `print_uint32_d` | `(v)` | 6 | Print 32-bit unsigned decimal; destroys v |
| `print_uint32` | `(v)` | 7 | Print 32-bit unsigned decimal; v preserved |

## Tier 5 — Multi-cell (16-bit)

Uses `layout Word { lo, hi }`.

| Macro         | Signature                          | Tmp | Effect            |
| ------------- | ---------------------------------- | :-: | ----------------- |
| `add16_d`     | `(src: Word -> dst: Word)`         | ... | 16-bit add        |
| `sub16_d`     | `(src: Word -> dst: Word)`         | ... | 16-bit sub        |
| `mul16`       | `(a: Word, b: Word -> dst: Word)`  | ... | 16-bit multiply   |
| `divmod16`    | `(a: Word, b: Word -> q: Word, r: Word)` | ... | 16-bit divmod |
| `ge16`        | `(a: Word, b: Word -> r)`          | ... | 16-bit comparison |
| `copy16`      | `(src: Word -> dst: Word)`         | ... | 16-bit copy       |
| `read_uint16` | `(-> dst: Word)`                   | ... | Parse decimal into Word |
| `print_uint16`| `(src: Word)`                      | ... | Print Word as decimal   |
