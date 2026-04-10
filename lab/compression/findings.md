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
