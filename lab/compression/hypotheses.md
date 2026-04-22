# Compression Hypotheses

Analysis of `results/sent.jsonl` (20 items) and `results/para.jsonl` (17 items) compressed by `claude-sonnet-4-6` using `compress.md` as the system prompt. Reviewed independently by Claude and GPT-5.4; findings merged below.

## Observed Errors

Incorrectly compressed items — meaning was changed or lost.

| ID | Item | What was lost | Source |
|----|------|---------------|--------|
| sent-7 | failure-clean-shutdown | "rather than a long-running service" is ambiguous — original says the app IS a calibration utility (not a long-running service), justifying the approach. Compressed reads as a comparison. | Claude |
| sent-8 | redundant-content-cost | Original distinguishes "already knows" (parametric) from "can discover" (retrieval). Compressed collapses both into "can already access." | Claude |
| sent-10 | grading-with-evidence | Dropped "not just state an opinion" — a key negative constraint on what counts as evidence. | Claude |
| sent-11 | skill-consultation-threshold | Dropped "typically", changing a tendency into an absolute rule. Also collapsed "knowledge or capabilities" → "capabilities." | Both |
| sent-13 | spec-prediction-false-belief | Replaced "false-belief task" with generic "requires actual inference." The false-belief analogy is the core insight. | Both |
| sent-17 | context-file-noise | Dropped "add noise that agents faithfully obey" — the causal mechanism. Changed "unnecessary" → "irrelevant" (different claim). | GPT |
| sent-19 | linear-history-model | "does not use tree-based history" → "uses linear history." Not tree-based does not strictly imply linear; this is added interpretation. | GPT |
| sent-20 | prompt-engineering-subagent | "detailed prompt engineering knowledge" weakened to "handling tasks." Original emphasizes knowledge containment, not just task routing. | GPT |
| para-5 | skai-chat-conventions | Dropped introductory line "Conventions for a TypeScript SPA (Preact + Redux Toolkit + MUI)" — establishes applicability scope. | GPT |
| para-6 | skai-chat-common-agents | Dropped path-specific heading "AGENTS.md for `src/component/common/`" — operationally important scope metadata. | GPT |
| para-7 | bfc-vscode-agents | Dropped "BSM = BrainFuck assembly mnemonic language with three abstraction levels" — needed context for later grammar-design bullet. | GPT |
| para-9 | canopus-logging | Dropped "Optional." at the start of Behavior — the subsystem being optional is a meaningful constraint. | Claude |
| para-13 | canopus-failure-policy | "via logging if available, otherwise stderr/message box" → "via logging, stderr, or message box." Lost conditional fallback ordering. | GPT |
| para-14 | worklog-decision | "active directory" → "stay active." Original refers to filesystem location, not status. | GPT |
| para-16 | bfc-value-tracking | Lost "pointer-relative offsets" and "acting as an implicit frame" — conceptual specifics, not fluff. | GPT |
| para-17 | comments-docstrings | "documentation-appropriate docstrings" → "full docstrings." Full implies exhaustive; original means adequate for the doc generator. | Both |

## Undercompressed Items

Items where the output is nearly identical to the input.

| ID | Item | Notes |
|----|------|-------|
| sent-1 | ast-vs-interpreter-opt | Only changed "distinct" → "differ" and merged with semicolon. Could restructure entirely. |
| sent-5 | queue-overflow-detection | Switched to passive voice — no token savings. |
| sent-15 | skill-self-containedness | Changed "single" → "sole" and "an agent" → "agents." Near-zero compression. |
| para-1 | ts-naming | Only abbreviated "including" → "incl." |
| para-2 | ts-string-literals | Mostly formatting changes; bullets and examples barely touched. |
| para-4 | on-rules-file-layout | Structural content preserved almost verbatim. |
| para-11 | worklog-writing-principles | Four long paragraphs barely trimmed. |
| para-12 | bfc-src-subdirectories | Very long output, nearly identical to input. |
| para-14 | worklog-decision | Near-identical to original. |
| para-16 | bfc-value-tracking | Longest paragraph item; barely compressed. |
| para-20 | skai-chat-global-files | Repetitive file-description scaffolding preserved. |

## Hypotheses

### H6: Few-shot examples with drift teach drift — REFUTED

The H5 examples themselves contain meaning drift. Example 1 compresses "`camelCase` — functions (including function-typed variables)" to "`camelCase` functions", dropping that function-typed variables also use camelCase — a reader would default them to `snake_case` (the variable convention). The model learns from the examples that this level of information loss is acceptable compression, setting a quality ceiling at the example's own quality.

**Prediction:** Replacing drifted examples with drift-free examples will reduce the model's drift rate without needing additional rules.

**Result:** Refuted as stated. Drift-free examples reduced compression (5.0%/5.2% vs 8.0%/6.7%) without reducing drift (1 → 1, same item). Minor issues increased (9 → 12). The drifted portions of the examples were entangled with the aggressive compression they demonstrated; removing drift also removed the compression signal. See F3.

**Resolution (v3):** Rather than replacing the drifted examples, a 4th example from non-test data was added targeting the specific blind spot (intro paragraph preservation). This eliminated all drift (0 vs 1) while keeping compression within 1pp of v2 on non-intro items. The approach works because the 4th example teaches a pattern without diluting the aggression signal from the original 3 examples. See F6.

### H7: Explicit compression target — REFUTED

The current prompt says "compress" open-endedly. GPT-5.4 plays it safe (8.5% baseline). Specifying a target ratio (e.g. "reduce by 30-50%") might push the model past its conservative default without needing structural instructions.

**Prediction:** Adding a numeric compression target will increase compression ratio without proportionally increasing drift.

**Result:** Refuted. Sent +0.4pp (negligible), para -1.0pp (worse). The model ignored the numeric target entirely — few-shot examples remain the dominant compression signal. See F4.

### H8: Negative examples — REFUTED

H5 showed positive examples teach strategy. Negative examples (a bad compression paired with its correction) might teach quality boundaries — specifically the intro-line deletion and qualifier-drop blind spots that persist across all runs.

**Prediction:** Including 1-2 negative examples ("bad → corrected") will reduce drift on the specific error patterns demonstrated, more effectively than rules (H1-H3) did.

**Result:** Refuted. Targeted items (sent-08, sent-11) were already clean in the v3 baseline. Negative examples reduced compression (-0.4pp/-1.3pp) and introduced 2 new drifts (sent-17, para-13) that v3 didn't have. Negative examples function like rules — they make the model globally conservative without selectively preventing targeted errors. See F7.

### H9: Model selection

Sonnet 4.6 compressed 2-5× more aggressively than GPT-5.4 at baseline (18.2% vs 8.5% sent, 11.5% vs 2.1% para). The Sonnet baseline was never drift-analyzed with the same rigor as the GPT-5.4 runs. If Sonnet's higher compression comes with acceptable drift, model choice may matter more than prompt engineering.

**Prediction:** Drift analysis of the Sonnet baseline will show a better compression/quality tradeoff than GPT-5.4 + prompt engineering achieved.

### H10: Multi-pass compression

First pass restructures, second pass catches remaining verbosity. The model might compress further when the text is already partially compressed — less "this looks important, don't touch it" hesitation on already-rewritten text.

**Prediction:** A second compression pass on already-compressed output will yield additional 5-15% reduction with minimal new drift.

### H11: Strip markdown scaffolding — REFUTED

Headers (`##`), bold (`**`), bullet prefixes (`- `), blank lines between sections — all cost tokens. Replacing them with lighter delimiters (colons, newlines) might yield compression that the model doesn't attempt because it treats formatting as immutable.

**Prediction:** Explicitly instructing the model to replace markdown formatting with lighter alternatives will yield measurable token savings on paragraph-level and document-level items where scaffolding is a larger share of total tokens.

**Result:** Refuted at aggregate level. Sent -1.5pp (worse), para -0.2pp (flat). Some items saved tokens by stripping bold/section breaks (para-11 -14, para-16 -10) but gains were offset by the model being more conservative elsewhere. The instruction redistributes tokens rather than reducing them. See F5.