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
