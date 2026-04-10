Source directory layout for BFC, a BrainFuck compiler library in TypeScript. BSM = BrainFuck assembly mnemonic language.

## Subdirectories

- `bf/` — BrainFuck layer: AST types, `bfParse` (with contraction), `bfEmit` (AST→source), `bfInterpret` (async tree-walker). All public API is prefixed `bf`-. Barrel: `bf/index.ts`.
- `bsm/` — BSM layer. Three-level AST (`ast/`): `CoreNode` → `FrameNode` → `MacroNode`. Parser has two entry points: `bsmParse` (frame-level) and `bsmParseMacro` (macro-level superset). Full pipeline: `bsmFullCompile` chains parse → resolve macros → resolve frames → optimize → compile. `bsmInterpret` (`interpret/`) executes `CoreNode[]` directly without compiling to BF. `patterns/` — reusable structural pattern matchers over core AST loops (one file per pattern); consumed by both the emitter and optimizer. Barrel: `bsm/index.ts`.
- `bsm-old/` — Archived old BSM layer: AST types, lexer, parser, compiler (BSM→BF), decompiler (BF→BSM), optimizer (skeleton), emitter (AST→source), frames extension (frame tracker). Barrel: `bsm-old/index.ts`. Not wired into the public barrel or CLI.
- `cli/` — CLI entry points. `bf.ts` — interpret BF. `bsm.ts` — subcommand dispatch (`compile`, `decompile`). `compile` uses `bsmFullCompile` (macro-aware). Subcommand implementations in `cli/cmd/`.
- `util/` — Shared utilities. `CellTape` — growable typed-array-backed tape with wrapping arithmetic, supporting 8/16/32-bit cell sizes. `io-types.ts` — shared I/O types (`CellSize`, `EofBehavior`, `PutChar`, `GetChar`) and default stdin/stdout callbacks used by both interpreters.
