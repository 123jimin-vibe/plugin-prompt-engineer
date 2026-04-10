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
