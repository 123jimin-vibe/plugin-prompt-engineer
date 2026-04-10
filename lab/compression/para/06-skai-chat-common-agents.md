Shared UI components in a Preact/MUI single-page application.

## AGENTS.md for `src/component/common/`

Shared UI components. No domain logic — pure presentation and interaction utilities.

### Subdirectories

- `popup/` — Promise-based modal system (alert, confirm, prompt, file pickers). Stack-managed via `PopupContext`/`usePopup()`.
- `file-explorer/` — IndexedDB filesystem browser with breadcrumbs, context menus, live directory watching.
- `light-container/` — Lightweight layout: `KeepMounted` (hidden preservation), `Stack` (flex div, lighter than MUI).
- `compat/` — Preact compatibility wrappers for MUI components (`Autocomplete`).

### Standalone Components

`variant-selector`, `confirm-exit`, `external-link`, `image-view`, `loading-cover`, `plain-text`, `virtual-form`.
