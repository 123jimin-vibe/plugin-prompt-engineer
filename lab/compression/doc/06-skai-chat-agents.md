## AGENTS.md for skai-chat

Mobile-friendly SPA for AI chat (BYOK). Client-side only except LLM/ImageGen API calls.

### Stack

TypeScript (strict), pnpm, Preact (aliased as React), MUI, Redux Toolkit + Redux-Saga, esbuild, ESLint Stylistic, arktype, LiquidJS.

Custom libs: briko (LLM invocation), llm-msg-io (message format/serialization), @jiminp/lite-fs (IndexedDB FS), @jiminp/tooltool (utilities, `unreachable()`).

### Commands

- `pnpm debug` / `pnpm build --mode=prod --sourcemap=false` / `pnpm tsc` / `pnpm lint` / `pnpm clean`
- Build output: `/serve/build`, entry: `/serve/index.html`
- The user runs `pnpm debug` (dev server) implicitly. Do not run `pnpm tsc` or `pnpm build` — type-checking and bundling are handled automatically.

### Structure

```
src/
  core.ts, index.ts, define.d.ts, theme.ts, version.ts
  global/store.ts      # configureStore — reducers + saga middleware
  chat/{impl/,reducer/,saga/}  # Domain logic, reducers, side effects
  llm-provider/ setting/ image-gen/ knowledge-base/ media/ system/ repair-mode/
  context/ lib/ util/
  component/{app.tsx, common/, panel/, sidebar/, setting/, onboarding/}
scripts/ eslint/ serve/ docs/
```

Feature pattern: `state.ts` (slice) + `saga.ts` + `selector.ts` + `impl/` + `index.ts` (barrel).

### Architecture

Redux slices in `global/store.ts`: `system`, `setting`, `llm_provider`, `chat`, `image_gen`, `repair_mode`.

Aliases: Preact→React (tsconfig paths), `@/*`→`./src/*`. Hooks from `preact/hooks`, not `react`.

### Nested AGENTS.md

- `src/global/AGENTS.md` — Redux store, cached-array-index, FS helpers, snackbar queue, app-level selectors/hooks.
- `src/setting/AGENTS.md` — Schema-driven settings: types, schema, slice, selectors, saga, IndexedDB persistence.
- `src/chat/AGENTS.md` — Chat domain: slice, reducers, sagas, impl (chunks, state, generation, persistence, templates).
- `src/component/common/AGENTS.md` — Shared UI: popup system, file explorer, light containers, compat wrappers, utility components.
- `src/component/panel/chat/AGENTS.md` — Chat panel UI: component tree, chunk rendering, input editor, dialogs, FABs.

### Conventions

- 4-space indent, LF, final newline, UTF-8
- `snake_case`: variables, properties, params. `camelCase`: functions, action creators. `PascalCase`: types, components.
- Redux slices: `snake_case` + `_slice` suffix. Actions: `camelCase`.
- `strict: true`, no `any`. arktype `type()` for validation. Prefer `null` over `undefined`. `== null` for nil checks.
- `@/` path alias for all src imports. `import type` / `import {type ...}` for type-only.
- Functional components only. CSS in separate `.css` files.
- Minimal comments; self-documenting code.

### Docs

`docs/onboarding.md` (setup), `docs/templates.md` (templates), `CHANGELOG.md`, `TODO.md`.

`TODO.md` tracks planned features and short-term tasks. Update when completing or adding tasks.
