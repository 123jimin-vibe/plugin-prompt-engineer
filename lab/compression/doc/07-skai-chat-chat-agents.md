## AGENTS.md for `src/chat/`

Core chat domain. Manages chat tabs, message chunks, LLM generation, and persistence.

All public APIs consumed via `@/chat` (barrel `index.ts`).

### State

`state.ts` — Slice `chat_slice`. State: `ChatState { tabs: VariantsOf<ChatTab> }`.

Request actions (suffix `Request`) are saga entry points; they carry payloads but do not mutate state directly.

`reducer/` — Reducer implementations split by domain (`tab.ts`, `chunk.ts`, `generation.ts`), spread into the slice.

`selector.ts` — Memoized selectors for tab, chunk, and generation state lookups.

### `impl/` — Pure Domain Logic

No Redux, no sagas.

- `chunk/` — Message chunk types and serde. Three discriminants: `'input'` (user-editable, owns `ChatExecuteInput`), `'output'` (LLM response), `'attach'` (images). Wrapped in `MessageChunkVariants` for branching.
- `state/` — `ChatExecuteState` (`system_messages` + `main_history`). Index types and lookup helpers. Message assembly for LLM calls. Serde and cloning.
- `tab.ts` — `ChatTab` type and factories.
- `generation-request.ts` — Generation request types (variant / next / insert / append-contents).
- `generation-op.ts` — Chunk operations the saga executes. Converts requests to ops.
- `generation-info.ts` — Generation lifecycle info stored on `ChatTab.generations` map (requested → ongoing). Multiple concurrent generations per tab.
- `step.ts` — LLM client creation (briko) and `chatStep()` invocation.
- `save.ts` — Persistence formats (`SavedChat`, `SavedChatCollection`). arktype-validated.
- `liquid/` — LiquidJS template rendering with custom FS adapter for knowledge base.

### `saga/` — Side Effects

Root: `chatSaga()` in `saga/index.ts`.

- `generate/` — Full generation lifecycle. Multiple concurrent generations per tab (`takeEvery`).
  - `saga.ts` — Orchestrator: batch expansion, setup → stream → finalize, error/abort cleanup.
  - `setup.ts` — Converts generation request to chunk op, dispatches initial Redux actions, returns `GenerationContext`.
  - `stream.ts` — Selects LLM params, calls `chatStep`, iterates stream events, patches chunk with deltas.
  - `finalize.ts` — Merges final response messages, dispatches success.
  - `abort.ts` — Abort controller registry. Exports `abortGeneration()` / `abortAllGenerations()`.
  - `types.ts` — `GenerationContext`, `StreamResult`.
- `edit.ts` — Input patching and chunk rendering (STF + LiquidJS).
- `load.ts` — Autosave loading and file loading. Tab init ensures system + first user chunks exist.
- `save.ts` — Manual save and debounced autosave.

### Key Concepts

- **VariantsOf\<T\>** — `{ variants: T[], choice: number }` branching pattern (tabs, chunks). Defined in `@/util`.
- **Cached array index** — O(1) ID→index cache from `@/global`.
- **STF** — Structured Text Format (`llm-msg-io`). Multi-message, multi-role conversations in a single text block.
- **Template engine** — LiquidJS. Input chunks can `{% include %}` knowledge base files.
