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
