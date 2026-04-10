## AGENTS.md for BFC

BFC — BrainFuck compiler library and CLI. Parses BF source → AST → interprets or emits output. Future pipeline: `source → bsm (frames) → bsm (core) → bf → output`.

## Stack

- TypeScript (ESNext, NodeNext, `"strict": true`).
- pnpm. Node.js built-in test runner (`node --test`).
- Build: `tsc` → `dist/`. Tests: `pnpm test` (runs `pretest` build, then `node --test "dist/**/*.spec.js"`).
- ESLint via `@jiminp/eslint-config`.
- Linting runs automatically on save — do not run lint commands.

## tsconfig Highlights

- `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noPropertyAccessFromIndexSignature` — use `!` postfix on indexed access, do not use `?:` when `undefined` is not an explicit member, use bracket notation for index signatures.
- `verbatimModuleSyntax` — use `import type` for type-only imports.
- `rewriteRelativeImportExtensions`, `erasableSyntaxOnly` — import with `.ts` extensions; no enums or parameter properties.

## CLI

- Run CLIs via pnpm scripts: `pnpm bsm` / `pnpm bf`. Do not use `npx`.

## Conventions

- Test files: `<module>.spec.ts` colocated beside the module.
- Tests use `node:test` (`describe`/`it`) and `node:assert/strict`.
- snake_case variables/fields, camelCase functions, PascalCase types/classes.
- Existing code uses `satisfies` on expected-shape literals, `!` on indexed accesses, `== null` for null/undefined checks.

## Directory Layout

- `src/` — source code. See [`src/AGENTS.md`](src/AGENTS.md).
- `worklog/` — project management. `worklog/plan/` contains design documents for unimplemented features. Read before implementing new layers.
- `editors/` — editor integrations. See [`editors/vscode/AGENTS.md`](editors/vscode/AGENTS.md).
- `docs/` — user-facing documentation. Keep in sync with CLI behavior, library API, and language semantics when those change.
- `dist/` — build output (gitignored).
