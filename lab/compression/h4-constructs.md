# H4 Construct Experiments

For each construct, compare token counts across: original, current compressed output, and proposed structural rewrite.

## C1: Bullet list → inline notation (para-1, ts-naming)

### original
## Naming

- `snake_case` — variables, attributes, arguments
- `camelCase` — functions (including function-typed variables)
- `PascalCase` — classes, interfaces, types

### compressed
## Naming
- `snake_case` — variables, attributes, arguments
- `camelCase` — functions (incl. function-typed variables)
- `PascalCase` — classes, interfaces, types

### rewrite
## Naming
`snake_case` vars/attrs/args · `camelCase` functions · `PascalCase` classes/interfaces/types

## C2: Sentence restructure — eliminate repeated subject (sent-1, ast-vs-interpreter-opt)

### original
These optimizations are distinct from AST optimization passes, which transform the AST before interpretation. Interpreter optimizations leave the AST unchanged and instead short-circuit execution.

### compressed
These optimizations differ from AST optimization passes, which transform the AST before interpretation; interpreter optimizations leave the AST unchanged and short-circuit execution instead.

### rewrite
Unlike AST passes that transform before interpretation, interpreter optimizations leave the AST unchanged and short-circuit execution.

## C3: Repeated scaffolding in file list (para-20, skai-chat-global-files)

### original
App-wide Redux store and shared utilities for a Preact/Redux AI chat application.

### Files

- `store.ts` — `configureStore` wiring. Combines all feature slices, attaches saga middleware. Exports `store`, `AppState`, `AppDispatch`.
- `selector.ts` — App-level selectors bridging `AppState` → `SettingState` (`selectAppSetting`, `useAppSetting`, `useIsRepairMode`).
- `cached-array-index.ts` — Global ID→array-index cache for O(1) lookups on ordered `{id}` arrays. Used pervasively by chat state.
- `fs.ts` — Shared `LiteFS` singleton and helpers (`readAsFile`, `loadObject`/`saveObject` with gzip + arktype validation).
- `image-gen.ts` — ComfyUI client singleton.
- `menu-anchor.ts` — `useMenuAnchor()` hook for MUI Menu anchor state.
- `queue/snackbar.tsx` — Global notification system (`snackbarPush`, `snackbarError`). Error history ring buffer. Imported as `@/global/queue`.
- `index.ts` — Barrel. Re-exports all except `queue/`.

### compressed
Redux store + shared utilities for Preact/Redux AI chat app.

**Files**

- `store.ts` — `configureStore` wiring; combines feature slices, attaches saga middleware; exports `store`, `AppState`, `AppDispatch`.
- `selector.ts` — App-level selectors: `AppState`→`SettingState` (`selectAppSetting`, `useAppSetting`, `useIsRepairMode`).
- `cached-array-index.ts` — Global ID→array-index cache for O(1) lookups on ordered `{id}` arrays; used pervasively by chat state.
- `fs.ts` — Shared `LiteFS` singleton + helpers (`readAsFile`, `loadObject`/`saveObject` with gzip + arktype validation).
- `image-gen.ts` — ComfyUI client singleton.
- `menu-anchor.ts` — `useMenuAnchor()` hook for MUI Menu anchor state.
- `queue/snackbar.tsx` — Global notification system (`snackbarPush`, `snackbarError`); error history ring buffer; imported as `@/global/queue`.
- `index.ts` — Barrel re-exporting all except `queue/`.

### rewrite
Redux store + shared utilities for Preact/Redux AI chat app.

| File | Purpose |
|------|---------|
| `store.ts` | `configureStore` wiring; combines slices, attaches saga middleware. Exports `store`, `AppState`, `AppDispatch`. |
| `selector.ts` | `AppState`→`SettingState` selectors (`selectAppSetting`, `useAppSetting`, `useIsRepairMode`). |
| `cached-array-index.ts` | Global ID→index cache for O(1) lookups on ordered `{id}` arrays; used by chat state. |
| `fs.ts` | `LiteFS` singleton + helpers (`readAsFile`, `loadObject`/`saveObject` with gzip + arktype). |
| `image-gen.ts` | ComfyUI client singleton. |
| `menu-anchor.ts` | `useMenuAnchor()` hook for MUI Menu anchor. |
| `queue/snackbar.tsx` | Notification system (`snackbarPush`, `snackbarError`); error ring buffer. Imported as `@/global/queue`. |
| `index.ts` | Barrel; re-exports all except `queue/`. |

## C4: Two sentences with shared conclusion → merge (para-13, canopus-failure-policy)

### original
### Failure Policy

Subsystem initialization failures (WASAPI device unavailable, DX12 device creation failure, etc.) are reported to the user and the application exits cleanly with a diagnostic message (via logging if available, otherwise stderr/message box).

Runtime failures trigger a clean shutdown. The application does not attempt hot recovery; the user restarts. This is acceptable for a calibration utility that is not a long-running service.

### compressed
### Failure Policy

Subsystem initialization failures (WASAPI unavailable, DX12 device creation failure, etc.) are reported via logging, stderr, or message box, then the application exits cleanly.

Runtime failures trigger clean shutdown; no hot recovery. The user restarts. Acceptable for a calibration utility, not a long-running service.

### rewrite
### Failure Policy

All failures → clean exit. Init failures (WASAPI, DX12, etc.) reported via logging if available, otherwise stderr/message box. Runtime failures: no hot recovery; user restarts. Acceptable for a calibration utility, not a long-running service.

## C5: Passive voice swap with no structural change (sent-5, queue-overflow-detection)

### original
SPSC command queue overflow must be detectable so the scene can discard the affected measurement rather than silently producing invalid calibration data.

### compressed
SPSC command queue overflow must be detectable so affected measurements can be discarded rather than silently producing invalid calibration data.

### rewrite
SPSC command queue overflow must be detectable so the scene can discard affected measurements instead of silently invalidating calibration data.

## C6: Dense paragraph barely touched (para-16, bfc-value-tracking, first two paragraphs only)

### original
### Value Tracking

Single forward scan maintaining a cell → known_value map (CellState). Maps pointer-relative offsets to known values, acting as an implicit frame anchored to the current pointer position. Subsumes the separate dead-loop elimination passes.

**Addressing model:** Goto shifts the map window (O(1)). Balanced loops (body delta = 0) invalidate only written offsets; unbalanced loops invalidate the entire map. Loop test cell is set to 0 on exit. Program start sets `is_all_zero`.

### compressed
### Value Tracking

Single forward scan with a cell→known_value map (CellState) anchored to the current pointer position. Goto shifts the map window (O(1)). Subsumes dead-loop elimination passes.

**Addressing:** Balanced loops (body delta = 0) invalidate only written offsets; unbalanced loops invalidate the entire map. Loop test cell is set to 0 on exit. Program start sets `is_all_zero`.

### rewrite
### Value Tracking

Forward scan: cell→known_value map (CellState), pointer-relative offsets as implicit frame. Goto shifts window (O(1)). Subsumes dead-loop elimination.

**Addressing:** Balanced loops (delta=0) invalidate written offsets only; unbalanced invalidate all. Test cell→0 on loop exit. Program start: `is_all_zero`.
