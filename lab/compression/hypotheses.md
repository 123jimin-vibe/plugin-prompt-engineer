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

### H1: Preserve word-level precision

The compressor makes small word-level changes that alter meaning: deleting qualifiers, swapping near-synonyms, inferring positive claims from negations. These look like compression but are meaning drift.

Sub-patterns observed:
- **Qualifier deletion** (sent-11): "typically" → absolute "only."
- **Negation-to-positive inference** (sent-19): "does not use tree-based" → "uses linear" — an interpretation, not a compression.
- **Conditional flattening** (para-13): "if available, otherwise" → flat list, losing fallback priority.
- **Synonym substitution** (sent-17): "unnecessary" → "irrelevant." (para-17): "documentation-appropriate" → "full." (sent-20): "knowledge" → "tasks."

**Proposed instruction:** "Qualifiers (typically, optionally, approximately), negative constraints (not X, never Y), conditional logic (if/otherwise/unless), and boundary conditions (only when, except if) carry meaning. Do not remove them unless provably implied by the remaining text. Do not infer a positive claim from a negation. Prefer original terms over synonyms unless strictly equivalent and shorter."

### H2: Preserve semantic anchors and causal mechanisms

Terms like "false-belief task" (sent-13), "implicit frame" (para-16), and "three abstraction levels" (para-7) are semantic anchors — they carry disproportionate meaning per token. Causal clauses like "add noise that agents faithfully obey" (sent-17) and "acting as an implicit frame" (para-16) explain *why*, not just *what*. The compressor drops both when nearby words seem to convey the gist.

**Proposed instruction:** "Domain-specific terms, named concepts, technical labels, and causal/mechanistic clauses ('which', 'by', 'because', 'acting as') are high-density content. Preserve them even if surrounding words seem to cover the meaning."

### H3: Preserve scope metadata

Lines like "Conventions for a TypeScript SPA (Preact + Redux Toolkit + MUI)" (para-5) and "AGENTS.md for `src/component/common/`" (para-6) look editorial but establish applicability. Dropping them makes the content float without context.

**Proposed instruction:** "Path references, file scopes, and applicability declarations ('for X', 'in Y') constrain where the content applies. Preserve them unless duplicated elsewhere."

### H4: Structural rewriting over word-level trimming

The compressor defaults to word-level edits: synonym substitution, article removal, passive ↔ active voice. This yields near-zero compression on already-dense text. Real gains come from restructuring: merging clauses, changing sentence topology, converting prose to compact notation, and using symbols.

**Experiment (h4-constructs.md):** Token counts (o200k_base) for original → current compressed → proposed structural rewrite:

| Construct | Technique | Orig | Comp | Rewrite | Verdict |
|-----------|-----------|------|------|---------|---------|
| C1 (para-1) | Bullet list → inline `·` | 41 | 42 | **27** (−34%) | Clear win |
| C2 (sent-1) | Sentence restructure | 31 | 30 | **21** (−32%) | Clear win |
| C3 (para-20) | File list → markdown table | 249 | 243 | 246 (−1%) | **No savings** — table syntax is token-heavy |
| C4 (para-13) | Two paragraphs → merged | 83 | 67 | **57** (−31%) | Win over already-decent compression |
| C5 (sent-5) | Passive voice swap | 24 | 22 | 23 | **Wash** — confirms voice changes are useless |
| C6 (para-16) | Dense paragraph restructure | 105 | 89 | **76** (−28%) | Win |

**Validated techniques:** inline notation (`·`, `|`), sentence restructuring (eliminate repeated subjects), paragraph merging, terse colon-style rephrasing.

**Invalidated:** markdown tables (token-expensive syntax), passive ↔ active voice swaps, synonym substitution.

**Proposed instruction:** "When word-level trimming yields <10% reduction, restructure: merge sentences sharing the same subject or conclusion, eliminate repeated subjects, factor out common list patterns, and use compact formats — semicolon-lists, `→` for mappings, `·` or `|` for inline alternatives, colon-style headers. Do not convert to markdown tables. Do not swap passive/active voice. Compress paragraphs as a unit, not sentence-by-sentence."

### H5: Add few-shot examples for calibration

The current system prompt (`compress.md`) is 4 lines of abstract rules with no examples. A few before/after pairs would anchor the model's compression style, preventing both the under-compression (word-swaps) and over-compression (dropping qualifiers) observed.

**Proposed addition:** Include 2–3 few-shot examples demonstrating structural rewriting, symbol use, and qualifier preservation.
