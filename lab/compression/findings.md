# Findings

## F1: Structural rewriting techniques (H4)

Token counts (o200k_base) for original → current compressed → proposed rewrite:

| Construct | Technique | Orig | Comp | Rewrite |
|-----------|-----------|------|------|---------|
| C1 (para-1) | Bullet list → inline `·` | 41 | 42 | **27** (−34%) |
| C2 (sent-1) | Sentence restructure | 31 | 30 | **21** (−32%) |
| C3 (para-20) | File list → markdown table | 249 | 243 | 246 (−1%) |
| C4 (para-13) | Two paragraphs → merged | 83 | 67 | **57** (−31%) |
| C5 (sent-5) | Passive voice swap | 24 | 22 | 23 (−4%) |
| C6 (para-16) | Dense paragraph restructure | 105 | 89 | **76** (−28%) |

**Works:**
- Inline notation (`·`/`|`) — C1: bullet list to inline saved 34% vs 0% from word-level compression.
- Sentence restructure (eliminate repeated subjects, merge clauses) — C2: 32% vs 3%. C6: 28% vs 15%.
- Paragraph merge (shared subject/conclusion → one paragraph) — C4: 31% vs 19%.

**Doesn't work:**
- Markdown tables — C3: table (246) was worse than bullet-list compression (243). Pipe/header row syntax costs more tokens than `- item —` scaffolding saves.
- Passive↔active voice swaps — C5: 1 token difference. Voice changes rearrange tokens, don't remove them.
- Synonym substitution — common English words are single BPE tokens. Swapping one for another is 1→1 = zero savings.

## F2: Hypothesis testing — instructions vs. few-shot (H1, H2, H3, H5)

GPT-5.4, temp 0, `compress.md` base prompt + one hypothesis instruction each. Tested on 20 sentence + 17 paragraph items. Baseline = same prompt without the hypothesis instruction, same model.

### Token reduction (o200k_base)

| Variant | Sent tokens | Sent reduction | Para tokens | Para reduction |
|---------|-------------|----------------|-------------|----------------|
| Original | 740 | — | 2713 | — |
| GPT baseline | 677 | 8.5% | 2656 | 2.1% |
| H1 (word precision) | 691 | 6.6% | 2633 | 2.9% |
| H2 (semantic anchors) | 681 | 8.0% | 2687 | 1.0% |
| H3 (scope metadata) | 674 | 8.9% | 2653 | 2.2% |
| **H5 (few-shot)** | **627** | **15.3%** | **2563** | **5.5%** |
| Sonnet baseline* | 605 | 18.2% | 2402 | 11.5% |

*Different model (Sonnet 4.6); included for reference, not direct comparison.

### Meaning drift

Each compressed output reviewed against its original for semantic loss, added interpretation, or ambiguity. Severity: CLEAN (no drift), minor (subtle shift unlikely to change downstream behavior), drift (changed meaning or lost constraint).

| Variant | Clean | Minor | Drift | Issue rate |
|---------|-------|-------|-------|------------|
| H3 (scope metadata) | 33 | — | 4 | 11% |
| **H5 (few-shot)** | **27** | **9** | **1** | **27%** |
| H1 (word precision) | 24 | 7 | 5 | 32% |
| H2 (semantic anchors) | 24 | — | 13 | 35% |

### Analysis

**H5 (few-shot examples) dominates the compression/quality tradeoff.** It compresses nearly 2× the GPT baseline at both levels, with only 1 meaningful error (para-07: lost BFC/BF/BSM abbreviation definitions). Its 9 minor flags are mostly near-synonym substitution ("discover" → "infer", "needing" → "retaining") — subtle shifts unlikely to change agent behavior.

**H1–H3 (rule-based instructions) barely move the needle on compression and don't reliably prevent their targeted error types:**

- **H1** was designed to preserve qualifiers, yet still dropped "just" (sent-10), "correctly" (sent-13), "wholesale"/"faithfully" (sent-17) — exactly the patterns it targeted. The instruction made GPT-5.4 more conservative overall (6.6% vs 8.5% baseline) without selectively protecting the right words.
- **H2** protected technical vocabulary (no jargon was lost) but failed on qualifier drops, synonym substitution, and punctuation-induced ambiguity. 35% drift rate — worst quality at near-zero compression.
- **H3** had the lowest drift rate (11%) but compressed less than the baseline at paragraph level (2.2% vs 2.1%). It prevented scope metadata loss in most cases but missed "Subsystem" in para-13 — the same error from the original Sonnet run.

**Recurring blind spots across all hypotheses:**

- sent-13: "follow a spec correctly" → "follow a spec" — dropped in H1, H2, H5. H3 kept it but only by accident (near-zero compression on that item).
- sent-08: "discover from existing sources" → "infer from" — appeared in H2, H3, H5. The model consistently replaces retrieval language with inference language.
- sent-07/para-13: "that is not a long-running service" → ", not a long-running service" — punctuation restructuring introduces parse ambiguity. Appeared in H1, H2, H3.

**Why few-shot works better than rules:** Rules tell the model what to preserve but not *how* to compress. The model defaults to word-level edits (synonym swaps, article removal) which yield near-zero compression on already-dense text. Few-shot examples demonstrate structural techniques (inline notation, sentence restructuring, paragraph merging) that unlock real compression — the model learns the *strategy*, not just the constraints. This aligns with F1's finding that structural rewriting outperforms word-level trimming.

**GPT-5.4 vs Sonnet 4.6 as compressor:** GPT-5.4 is substantially more conservative than Sonnet 4.6 at baseline (8.5% vs 18.2% sent, 2.1% vs 11.5% para). This is a model-level difference, not an instruction effect. The Sonnet baseline's higher compression came with more errors (16 catalogued in hypotheses.md). GPT-5.4 + H5 (15.3% / 5.5%) approaches Sonnet's compression level with fewer serious errors.

## F3: Drift-free examples reduce compression without reducing drift (H6)

GPT-5.4, temp 0, `compress-h6.md` (same as `compress.md` but with all example drifts corrected). Tested on 20 sentence + 17 paragraph items.

### Token reduction (o200k_base)

| Variant | Sent tokens | Sent reduction | Para tokens | Para reduction |
|---------|-------------|----------------|-------------|----------------|
| Original | 740 | — | 2713 | — |
| H5 (v2 run) | 681 | 8.0% | 2531 | 6.7% |
| **H6 (drift-free examples)** | **703** | **5.0%** | **2573** | **5.2%** |

### Meaning drift

| Variant | Clean | Minor | Drift | Issue rate |
|---------|-------|-------|-------|------------|
| H5 (v2 run)* | 27 | 9 | 1 | 27% |
| **H6** | **24** | **12** | **1** | **35%** |

*H5 drift counts from F2 analysis; v2 token counts from re-run on current `compress.md`.

H6's single drift is **para-07** — dropped BF/BSM/BFC acronym definitions. Same item and same error as H5.

### Analysis

**H6 is not supported.** Fixing the drifted examples did not reduce drift and made compression worse.

The drifted H5 examples served two functions simultaneously: teaching **compression strategy** (structural rewriting techniques) and setting an **aggression level** (how much to remove). Correcting the drifts preserved the strategy signal but removed the aggression signal. Example 2's output became nearly identical to its input; Example 3 preserved almost every word. The model learned that the acceptable compression ceiling is "keep almost all the words, rearrange slightly."

Consequences:
- **Less compression** (5.0%/5.2% vs 8.0%/6.7%) — the examples no longer demonstrated bold restructuring.
- **More minor issues** (12 vs 9) — with less structural headroom, the model fell back on word-level tweaks (synonym swaps, article drops) that the prompt explicitly prohibits.
- **Same drift** (para-07) — this error is a structural blind spot (dropping an introductory context paragraph), unrelated to the example-level drifts that were corrected.

**Implication for future example design:** Few-shot examples must be both drift-free AND aggressively compressed — a harder constraint than H6 assumed. Simply fixing drifts in existing examples does not work because the compression and the drift are entangled in the same edits.

## F4: Explicit compression target (H7)

GPT-5.4, temp 0, `compress-h7.md` (same as `compress.md` but with "Target 30-50% token reduction" added to the first line). Tested on 20 sentence + 17 paragraph items.

### Token reduction (o200k_base)

| Variant | Sent tokens | Sent reduction | Para tokens | Para reduction |
|---------|-------------|----------------|-------------|----------------|
| Original | 740 | — | 2713 | — |
| H5 (v2 run) | 681 | 8.0% | 2531 | 6.7% |
| **H7 (30-50% target)** | **678** | **8.4%** | **2558** | **5.7%** |

### Meaning drift

| Variant | Clean | Minor | Drift | Issue rate |
|---------|-------|-------|-------|------------|
| H5 (v2 run) | 27 | 9 | 1 | 27% |
| **H7** | **26** | **10** | **1** | **30%** |

H7's single drift is **para-07** — dropped BF/BSM/BFC acronym definitions. Same item and same error as H5.

### Analysis

**H7 is not supported.** The explicit 30-50% compression target had negligible effect on sentence-level compression (+0.4pp) and actually reduced paragraph-level compression (-1.0pp). Drift profile is comparable to H5.

The model ignored the numeric target. GPT-5.4 at temp 0 produces the same conservative output regardless of whether the prompt says "compress" or "compress by 30-50%." The few-shot examples remain the dominant signal — the model compresses to the level demonstrated by the examples, not to the level stated in the instructions. This is consistent with F2's finding that rules (instructions) are weaker than demonstrations (examples).

## F5: Strip markdown scaffolding (H11)

GPT-5.4, temp 0, `compress-h11.md` (same as `compress.md` but with instruction to replace markdown formatting with lighter delimiters). Tested on 20 sentence + 17 paragraph items. Doc-level items excluded per lab policy.

### Token reduction (o200k_base)

| Variant | Sent tokens | Sent reduction | Para tokens | Para reduction |
|---------|-------------|----------------|-------------|----------------|
| Original | 740 | — | 2713 | — |
| H5 (v2 run) | 681 | 8.0% | 2531 | 6.7% |
| **H11 (strip scaffolding)** | **692** | **6.5%** | **2536** | **6.5%** |

### Meaning drift

| Variant | Clean | Minor | Drift | Issue rate |
|---------|-------|-------|-------|------------|
| H5 (v2 run) | 27 | 9 | 1 | 27% |
| **H11** | **25** | **11** | **1** | **32%** |

H11's single drift is **para-07** — dropped BF/BSM/BFC acronym definitions (though BSM was partially preserved). Same core error as H5.

### Analysis

**H11 is not supported at aggregate level.** Net compression is near-identical to H5 at paragraph level (-0.2pp) and worse at sentence level (-1.5pp). Sentence-level items have almost no markdown scaffolding to strip, so the instruction adds prompt weight without a target.

Item-level results are mixed. Some items saved tokens by stripping bold markers and section breaks: para-11 (-14), para-16 (-10), para-05 (-6), para-20 (-6), para-07 (-5). But para-12 grew by +37 tokens — because H11 **preserved** the BFC/BSM introductory context that H5 silently dropped. The scaffolding instruction may have made the model view document structure as something to reformat rather than strip, indirectly protecting intro context that other variants discard.

**Net assessment:** The scaffolding instruction redistributes tokens (stripping formatting, preserving content) rather than reducing them overall. On items where formatting is a large share of total tokens, savings are real but offset by the model being more conservative elsewhere.

## F6: Targeted few-shot example for intro preservation (compress.md v3)

### Background

The para-07 blind spot (dropping introductory context paragraphs) persisted across all tested variants: H1–H3, H5, H6, H7, H11. Two prior attempts to fix it failed:

- **v3 attempt 1** (F3 approach extended): replaced all three examples with drift-free versions. Compression dropped to 3.4%/3.9% and drift increased to 2 items. Root cause: the current example source items (para-01, sent-01, para-13) lack structural redundancy — aggressive compression on them requires dropping information. Making examples drift-free inherently reduces aggression because the drift IS the compression.
- **Rule-based approach** ("Do not drop introductory context"): included in v3 attempt 1 alongside drift-free examples. para-12 preserved its intro, but para-07 did not. Consistent with F2's finding that rules are weaker than examples.

### Design

Rather than replacing the existing (aggressive, slightly drifted) examples, a **4th example** was added from non-test data (doc/08-canopus-overview.md) demonstrating that introductory context should be compressed, not dropped:

```
Input:
Canopus is a calibration and training desktop application for rhythm game players.
It runs as a full-screen or windowed application with multiple navigable scenes.

### Scenes

Scene list is not closed/fixed.

Output:
Canopus: calibration/training desktop app for rhythm game players · full-screen
or windowed, multiple navigable scenes.
### Scenes
Scene list is not closed/fixed.
```

This example compresses only 15% — but its purpose is not to set aggression (the other 3 examples do that). It teaches a specific structural pattern: intro paragraph before a heading → compress it, keep it.

### Token reduction (o200k_base)

| Variant | Sent tokens | Sent reduction | Para tokens | Para reduction |
|---------|-------------|----------------|-------------|----------------|
| Original | 740 | — | 2713 | — |
| v2 (H5) | 681 | 8.0% | 2531 | 6.7% |
| **v3** | **688** | **7.0%** | **2585** | **4.7%** |

### Meaning drift

| Variant | Clean | Minor | Drift | Issue rate |
|---------|-------|-------|-------|------------|
| v2 (H5) | 27 | 9 | 1 | 27% |
| **v3** | **28** | **9** | **0** | **24%** |

### Analysis

**v3 eliminates all drift.** The persistent para-07 blind spot is fixed — BF/BSM/BFC acronym definitions are preserved in full. Para-12's intro context is also preserved. All 12 watchlist items passed (sent-07, 08, 10, 11, 13, 17, para-05, 07, 09, 12, 13, 17).

**Compression decrease is almost entirely quality improvement.** Para-07 (+36 tokens) and para-12 (+37 tokens) account for +73 of the +54 total para token increase. These items gained tokens because the model preserved content that v2 incorrectly dropped. Excluding those two items, v3 compresses non-intro items slightly better than v2 (1982 vs 2001 tokens). Sentence-level compression decreased by 1.0pp (7.0% vs 8.0%), within normal variance.

**Why this worked when other approaches failed:**

1. **The 4th example teaches a PATTERN, not a constraint.** Rules say "don't do X" but don't show alternatives. The example shows what TO DO with an intro paragraph — compress it structurally, keep it in place. This is consistent with F2's finding that examples teach strategy while rules don't.
2. **It doesn't dilute the aggression signal.** The original 3 examples (averaging ~34% compression) still set the aggression level. The 4th example targets a specific blind spot without interfering with the compression strategy.
3. **It uses non-test data.** The example comes from doc/08, not from the sent/para test sets, avoiding overfitting to specific test items while teaching a generalizable pattern.

## F7: Negative examples (H8)

GPT-5.4, temp 0, `compress-h8.md` (v3 prompt + 2 negative examples showing bad compressions with corrections). Tested on 20 sentence + 17 paragraph items.

Negative examples targeted two persistent error patterns:
1. **Qualifier drop** (from sent-11): "typically" dropped, "knowledge or capabilities" → "capabilities."
2. **Specificity collapse** (from sent-08): "already knows or can discover" → "can already access."

### Token reduction (o200k_base)

| Variant | Sent tokens | Sent reduction | Para tokens | Para reduction |
|---------|-------------|----------------|-------------|----------------|
| Original | 740 | — | 2713 | — |
| v3 | 688 | 7.0% | 2585 | 4.7% |
| **H8 (negative examples)** | **691** | **6.6%** | **2622** | **3.4%** |

### Meaning drift

| Variant | Clean | Minor | Drift | Issue rate |
|---------|-------|-------|-------|------------|
| v3 | 28 | 9 | 0 | 24% |
| **H8** | **26** | **9** | **2** | **30%** |

H8 drifts: **sent-17** (dropped "that" from "noise that agents faithfully obey," breaking the relative clause that encodes the causal mechanism) and **para-13** ("All failures → clean exit" framing collapsed the two-tier distinction between init and runtime failure handling). Both were CLEAN in v3.

### Analysis

**H8 is not supported.** Negative examples reduced compression (-0.4pp sent, -1.3pp para vs v3) and increased drift (0 → 2). The targeted items (sent-08, sent-11) were already CLEAN in v3 — the negative examples solved a problem that the v3 prompt had already fixed through other means.

The negative examples had two unintended effects:
1. **Overall conservatism.** Para-11 (+20 tokens) and para-16 (+18 tokens) grew substantially. The model treated the "avoid these errors" section as a general caution signal, not a targeted correction for specific patterns.
2. **Attention displacement.** New drifts appeared on sent-17 and para-13 — items that were CLEAN in v3. The added prompt weight (~228 tokens of negative examples) may have pushed other quality-relevant context out of the model's effective attention window.

**Negative examples function like rules, not like positive examples.** F2 established that rules make GPT-5.4 more conservative without selectively preventing their targeted errors. Negative examples follow the same pattern — they constrain behavior globally rather than teaching specific alternatives. The "bad → corrected" format does not override this: the model still reads them as constraints, not demonstrations of strategy.
