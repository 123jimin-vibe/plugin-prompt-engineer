Conventions for a TypeScript SPA (Preact + Redux Toolkit + MUI).

### Conventions

- 4-space indent, LF, final newline, UTF-8
- `snake_case`: variables, properties, params. `camelCase`: functions, action creators. `PascalCase`: types, components.
- Redux slices: `snake_case` + `_slice` suffix. Actions: `camelCase`.
- `strict: true`, no `any`. arktype `type()` for validation. Prefer `null` over `undefined`. `== null` for nil checks.
- `@/` path alias for all src imports. `import type` / `import {type ...}` for type-only.
- Functional components only. CSS in separate `.css` files.
- Minimal comments; self-documenting code.
